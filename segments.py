"""
$Id$
"""

def implements( iface ): pass

class Pipeline( object ):

    def __init__(self, **kw):
        self.steps = []
        self.vars = kw
        self.services = {}
        
    def __iter__(self):
        for s in self.steps:
            yield s

    def process( self, context ):
        for s in self:
            context = s.process( self, context )


class IPipeline( object ):
    services = " "
    vars = " "
    steps = " "

    def process( context ): pass

class IPipeSegment( object ):

    def process( pipeline, ctxobj ): pass

class IProducer( PipeSegment ): pass
class IConsumer( PipeSegment ): pass
class IProducerConsumer( PipeSegment ): pass
class IFilter( ProducerConsumer ): pass
class ITee( PipeSegment ): pass
class IWatcher( PipeSegment ): pass

class PipeSegment( object ):

    def process( self, pipeline, ctxobj ):
        raise NotImplemented


#################################

class PolicyPipe( Pipeline ):

    def __call__( self, policy ):
        self.process( policy )

class PipeEnvironmentInitializer( Pipeline ):

    implements( PipeSegment )

    def process( self, pipe, ctxobj ):
        self.setupServices( pipe, ctxobj )
        self.setupVariables( pipe, ctxobj )
        self.setupURIResolver( pipe, ctxobj )
        return ctxobj
    
    def setupVariables( self, pipe, ctxobj ):

        dfactory = DescriptorFactory( ctxobj )
        pipe.services["DescriptorFactory"] = DescriptorFactory
        

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

        pipe.services['URIResolver'] = uri_resolver
        
        
    def setupServices( self, pipe, ctxobj ):
        addService = pipe.services.__setitem__

        source    = ctxobj.getContentIdentification()
        addService("ContentIdentification", source)
        
        structure = ctxobj.getContentOrganization()
        addService("ContentOrganization", structure)
        
        mastering = ctxobj.getContentMastering()
        addService("ContentRules", mastering)
        
        deployer  = ctxobj.getContentDeployment()
        addService("ContentTransports", deployer)
        
        views     = ctxobj.getContentDirectoryViews()
        addService("ContentDirectoryViews", views)
        
        resolver  = ctxobj.getDeploymentURIs()
        addService("ContentResolver", resolver )
        
        history   = ctxobj.getDeploymentHistory()
        addService("ContentHistory", history )

        addService("ContentStorage", ContentStorage(self) )

class ContentSource( PipeSegment ):

    implements( IProducer )

    def process( self, pipe, ctxobj ):
        mlen = pipe.variables.get('mount_length', 0)
        source = self.getService("ContentIdentification")
        return source.getContent(mount_length = mlen)



class DirectoryViewDeploy( PipeSegment ):
    """
    """

    def process( self, pipe, content ):

        views = pipe.services["ContentDirectoryViews"]
        resolver = pipe.services['URIResolver']
        store = pipe.services["ContentStorage"]
        stats = pipe.services['ExecutionStats']
        
        contents = views.getContent()

        for dvc in contents:
            resolver.addResource( dvc )

        for dvc in contents:
            views.cookViewObject( dvc )
            resolver.resolve( dvc )
            store( dvc )

class ContentTransport( PipeSegment ):

    def process( self, pipe, ctxobj ):
        transports = pipe.services['ContentTransports']
        organization = pipe.services['ContentOrganization']
        transports.deploy( organization.getActiveStructure() )


class ContentPrepPipe( PipeSegment ):
    """
    processes a single piece of content
    """
    
    implements( IProducerConsumer )

    def __init__(self):
        self.prepared = []

    def process( self, pipe, context ):

        # expects an iterator
        
        #gc_counter = 0
        for c in context:
            self.processContent( c )
            #if self.gc_threshold%gc_counter == 0:

        return 

    def processContent( self, pipe, content ):
        factory = pipe.services["DescriptorFactory"]
        rules = pipe.services["ContentRules"]
        resolver = pipe.services['URIResolver']
        
        content = self.getContent( content )
        descriptor = factory( content )

        if not rules.match( descriptor ):
            try: content._p_deactivate()
            except: pass
            return

        resolver.addResource( descriptor )

    def getContent( self, ctxobj ):
        return ctxobj.getObject()

    
class ContentProcessPipe( PipeSegment ):

    def process( self, pipe, descriptor):
        rules = pipe.services["ContentRules"]
        resolver = pipe.services['URIResolver']
        store = pipe.services["ContentStorage"]
        
        rules.render( descriptor )
        content = descriptor.getContent()

        if not descriptor.isGhost():
            resolver.resolve( descriptor )
            
        store( descriptor )


class DefaultPolicyPipeline( object ):
    
    step_factories = [ PipeEnvironmentInitializer,
                       ContentSource,
                       ContentPrepPipe,
                       DirectoryViewDeploy,
                       ContentProcessPipe ]
    
            

        
        
        
