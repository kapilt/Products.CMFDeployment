from segments import *
from ContentStorage import ContentStorage
from Descriptor import DescriptorFactory
from Products.CMFDeployment import incremental
from Products.CMFDeployment.Statistics import TimeStatistics, MemoryStatistics
import os, shutil

class PolicyPipeline( Pipeline ):
    
    def __call__( self, policy):
        self.process( policy)

class PipeEnvironmentInitializer( Pipeline ):

    implements( PipeSegment )

    def process( self, pipe, ctxobj ):
        self.setupServices( pipe, ctxobj )
        self.setupVariables( pipe, ctxobj )
        self.setupURIResolver( pipe, ctxobj )
        return ctxobj
    
    def setupVariables( self, pipe, ctxobj ):
        dfactory = DescriptorFactory( ctxobj )
        pipe.services["DescriptorFactory"] = dfactory

    def setupURIResolver( self, pipe, ctxobj ):
        resolver = pipe.services['ContentResolver']
        uri_resolver = resolver.clone( persistent = 0 )

        organization = pipe.services['ContentOrganization']
        mount_point = organization.getActiveStructure().getCMFMountPoint()
        mount_path = mount_point.getPhysicalPath()
        mlen = len('/'.join(mount_path))
        mount_url_root = mount_point.absolute_url(1)

        # should setup an edit method for this
        uri_resolver.mount_path = mount_url_root
        uri_resolver.source_host = ctxobj.REQUEST['SERVER_URL']
        uri_resolver.mlen = len(mount_url_root)
        #maybe we should change this:
        uri_resolver.content_map= pipe.services['ContentMap']

        pipe.services['URIResolver'] = uri_resolver
        
        
    def setupServices( self, pipe, ctxobj ):
        addService = pipe.services.__setitem__

        source    = ctxobj.getContentIdentification()
        addService("ContentIdentification", source)
        
        structure = ctxobj.getContentOrganization()
        addService("ContentOrganization", structure)
        
        mastering = ctxobj.getContentMastering()
        addService("ContentMastering", mastering)
        
        rules = ctxobj.getContentRules()
        addService("ContentRules", rules)

        deployer  = ctxobj.getContentDeployment()
        addService("ContentTransports", deployer)
        
        views     = ctxobj.getContentDirectoryViews()
        addService("ContentDirectoryViews", views)
        
        resolver  = ctxobj.getDeploymentURIs()
        addService("ContentResolver", resolver )
        
        history   = ctxobj.getDeploymentHistory()
        addService("ContentHistory", history )
        
        policy= ctxobj.getDeploymentPolicy()
        addService("DeploymentPolicy", policy)
        
        addService("ContentStorage", ContentStorage(ctxobj) )
        
        content_map= ctxobj.getContentMap()
        addService("ContentMap", content_map)
        
        stats = TimeStatistics()
        stats ('Initializing the environnement')
        addService("TimeStatistics", stats)
        
        mstats = MemoryStatistics()
        mstats('Initializing the environnement')
        addService("MemoryStatistics", mstats)
        
        deletion_source= ctxobj.getDeletionSource()
        addService("DeletionSource", deletion_source)
        
        dependency_source= ctxobj.getDependencySource()
        addService("DependencySource", dependency_source)

class ContentSource( PipeSegment ):

    implements( IProducer )

    def process( self, pipe, ctxobj ):
        stats = pipe.services["TimeStatistics"]      
        mstats = pipe.services["MemoryStatistics"]
        stats ('Getting the content sources', relative='Initializing the environnement')
        mstats('Getting the content sources')
    
        mlen = pipe.vars.get('mount_length', 0)
        source = pipe.services["ContentIdentification"]
        
        history = pipe.services["ContentHistory"]
        last_time = history.getLastTime()
        return source.getContent(last_time, mount_length = mlen)

class DirectoryViewDeploy( PipeSegment ):
    """
    """

    def process( self, pipe, content ):
        views = pipe.services["ContentDirectoryViews"]
        resolver = pipe.services['URIResolver']
        store = pipe.services["ContentStorage"]
        
        contents = views.getContent()

        for dvc in contents:
            resolver.addResource( dvc )

        for dvc in contents:
            views.cookViewObject( dvc )
            resolver.resolve( dvc )
            store( dvc )

        stats = pipe.services["TimeStatistics"]      
        mstats = pipe.services["MemoryStatistics"]
        
        stats ('View deployed', relative='Content prepared')
        mstats('View deployed')  

        return content

class ContentTransport( PipeSegment ):

    def process( self, pipe, ctxobj ):
        transports = pipe.services['ContentTransports']
        organization = pipe.services['ContentOrganization']
        transports.deploy( organization.getActiveStructure() )


class ContentPreparation( PipeSegment ):
    """
    prepares a piece of content to be deployed, determines matching
    rulel, creates descriptor, and adds to uri resolver.
    """
    
    implements( IProducerConsumer )

    def process( self, pipe, content):
        factory = pipe.services["DescriptorFactory"]
        mastering = pipe.services["ContentMastering"]
        resolver = pipe.services['URIResolver']
        
        descriptors= [] #list of the descriptors returned
        while (True):
            try:
                cont= content.next().getObject()
                descriptor = factory( cont )
                if not mastering.prepare( descriptor ):
                    pass
                resolver.addResource( descriptor )
                descriptors.append(descriptor)
            except:
                break   
          
        stats = pipe.services["TimeStatistics"]      
        mstats = pipe.services["MemoryStatistics"]
        
        stats ('Content prepared', relative='Getting the content sources')
        mstats('Content prepared')  
        return descriptors

    
class ContentProcessPipe( PipeSegment ):

    def process( self, pipe, descriptor):
        mastering = pipe.services["ContentMastering"]
        resolver = pipe.services['URIResolver']
        store = pipe.services["ContentStorage"]
        dependency_source = pipe.services["DependencySource"]
        ds = dependency_source.getContent()
        while True:
            try:
                d = ds.next()
                descriptor.append(d)
            except StopIteration:
                break
        
        for desc in descriptor:
            mastering.cook(desc)
            content = desc.getContent()
            
            if not desc.isGhost():
                resolver.resolve( desc )
                
            store( desc )
        
        stats = pipe.services["TimeStatistics"]      
        mstats = pipe.services["MemoryStatistics"]
        
        stats ('Processing the content', relative='Deploying dependencies')
        mstats('Processing the content')
       
class ContentDeletionPipeline( PipeSegment ):

    def process( self, pipe, ctxobj):
        stats = pipe.services["TimeStatistics"]      
        mstats = pipe.services["MemoryStatistics"]
        
        stats ('Taking care of the deleted content', relative='Processing the content')
        mstats('Taking care of the deleted content')
       
        #delete deleted_records from the filesystem      
        deletion_source = pipe.services['DeletionSource']
        deleted_records= deletion_source.getContent()
        
        organization = pipe.services['ContentOrganization']
        structure = organization.getActiveStructure()
        content_map= pipe.services['ContentMap']
        
        #take the reverse dependencies of the deleted_records
        #no need to clean the deletion source and the dep. source
        try:
            while True:
                record = deleted_records.next()
                descriptor= record.descriptor
                filename = descriptor.getFileName()
                content_path = structure.getContentPathFromDescriptor(descriptor)
                #if the content_path is None, the object has been unindexed
                if descriptor.getId() == ".personal":
                    continue
                location = os.sep.join( ( content_path, filename) )
                if descriptor.isContentFolderish():
                    shutil.rmtree(content_path)
                else:
                    os.remove(location)
                    
                #we clean the content map, deleting all the links on the descriptor
                content_map.clean(descriptor)
        
        except StopIteration:         
            return
           

class ContentWatchEnd( PipeSegment ):

    implements( IWatcher )

    def process( self, pipe, descriptor):
    
        stats = pipe.services["TimeStatistics"]      
        mstats = pipe.services["MemoryStatistics"]
        
        stats ('pipeline processed')
        mstats('pipeline processed')
    
        stats.stop()
        mstats.stop()
    
        block = stats.pprint() + '\n\n' +mstats.pprint()
        return block

#################################
# pipeline - todo conditional matching on record or descriptor        
# segment - uindex / dependency manager /

class DeletionPipeline( object ):

    def condition(self):
        pass

    def process( self, record ):
        pass

"""
  initializer [ policy ] -> policy
  directoryviewdeploy [ policy ] -> policy
  content source [ policy ] -> content stream iterator  
  
"""

class DefaultPolicyPipeline( object ):
    
    step_factories = [ PipeEnvironmentInitializer,
                       ContentSource,
                       DirectoryViewDeploy,
                       ContentProcessPipe ]
    
#IncrementalPipeline = Pipeline(
#    steps = ( PipeEnvironmentInitializer(),
#              ContentSource(),
#              ConditionalBranch(
#                      
#              Iterator( ( ContentPrepPipeline, ) ),
#              DirectoryViewDeploy(),

       
         

        
        
        
