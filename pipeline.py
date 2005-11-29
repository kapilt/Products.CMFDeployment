from segments import *
from ContentStorage import ContentStorage
from Descriptor import DescriptorFactory
from Products.CMFDeployment import incremental

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

class ContentSource( PipeSegment ):

    implements( IProducer )

    def process( self, pipe, ctxobj ):
        getService = pipe.services.__getitem__
        mlen = pipe.vars.get('mount_length', 0)
        source = getService("ContentIdentification")
        
        #print "pipeline: ContentSource: ", source.getContent(mount_length = mlen)
        return source.getContent(mount_length = mlen)

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

        return content

class ContentTransport( PipeSegment ):

    def process( self, pipe, ctxobj ):
        transports = pipe.services['ContentTransports']
        organization = pipe.services['ContentOrganization']
        transports.deploy( organization.getActiveStructure() )
        return ctxobj


class ContentPreparation( PipeSegment ):
    """
    prepares a piece of content to be deployed, determines matching
    rulel, creates descriptor, and adds to uri resolver.
    """
    
    implements( IProducerConsumer )

    def __init__(self):
        self.prepared = []

    def process( self, pipe, content):
            return self.processContent(pipe, content)

    def processContent( self, pipe, content ):
        factory = pipe.services["DescriptorFactory"]
        mastering = pipe.services["ContentMastering"]
        resolver = pipe.services['URIResolver']
        
        descriptors= [] #list of the descriptors returned
        while (True):
            #content = self.getContent( content )
            try:
                descriptor = factory( content.next().getObject() )
            except:
                return descriptors    
            if not mastering.prepare( descriptor ):
                try: content._p_deactivate()
                except: pass
                return []

            resolver.addResource( descriptor )
            descriptors.append(descriptor)
            
        #print "pipeline: ContentPreparation: ", descriptors
        return descriptors

    def getContent( self, ctxobj ):
        return ctxobj.next().getObject()

    
class ContentProcessPipe( PipeSegment ):

    def process( self, pipe, descriptor):
        mastering = pipe.services["ContentMastering"]
        resolver = pipe.services['URIResolver']
        store = pipe.services["ContentStorage"]
        
        #print "pipeline: ContentProcessPipe desc: ", descriptor
        for desc in descriptor:
            mastering.cook(desc)
            content = desc.getContent()
            
            if not desc.isGhost():
                resolver.resolve( desc )
                
            store( desc )
        return descriptor
        


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

       
         

        
        
        
