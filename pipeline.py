import segments

from segments.core import PolicyPipeline, PipeExecutor



class PipelineFactory( object ):

    id = None

    def __call__( self ):
        pass

    def getId( klass ):
        return klass.id

    getId = classmethod( getId )

    def finishPolicyConstruction( self, policy ):
        pass

    def cleanupPolicyRemoval( self, policy ):
        pass
    

class IncrementalPipelineFactory( PipelineFactory ):
    
    id = 'incremental'

    def __call__( self ):

        deletion_pipeline = self.constructDeletionPipeline()
        content_pipeline = self.constructContentPipeline()
        dv_pipeline = self.constructDirectoryViewPipeline()

        policy_pipeline = PolicyPipeline( 
            steps = (
               segments.environment.PipeEnvironmentInitializer(),
               dv_pipeline,
               deletion_pipeline,
               content_pipeline,
               segments.transport.ContentTransport()
               )
            )

        return policy_pipeline

        

    def finishPolicyConstruction( self, policy ):

        import incremental

        catalog = getToolByName( policy, 'portal_catalog' )
        pidx_id = "%s-%s"%(policy.getId(), "policy_index")
        catalog.manage_addIndex( pidx_id,
                                 incremental.PolicyIncrementalIndex.meta_type )

        # XXX - add deletion source / dependency source
        
    def cleanupPolicyRemoval( self, policy ):
        pass
              

    #################################
    # private methods for easy subclass construction
    def constructContentPipeline( self ):
        return PipeExecutor(
            
            steps = (
                segments.source.ContentSource(),
                segments.filter.ContentFilter(),
                segments.rule.ContentRuleMatch(),
                segments.dependency.DeployDependencyInjector(),
                segments.render.ContentRender(),
                segments.resolver.ResolverDatabase(),
                segments.storage.ContentStorage(),
                )
            )

    def constructDeletionPipeline( self ):
        return PipeExecutor(
            steps = (
                segments.source.ContentDeletion(),
                segments.dependency.RemovalDependencyInjector(),
                segments.resolver.ResolverRemoval(),
                segments.storage.ContentRemoval()
                )
            )

    def constructDirectoryViewPipeline( self ):
        return segments.directoryview.DirectoryViewDeploy()


class PipelineDatabase( object ):

    def __init__(self):
        self._pipelines = {}

    def registerPipeline(self, name, protocol):
        self._pipelines[name]=protocol

    def getPipelineNames(self, context=None):
        return self._pipelines.keys()

    def getPipeline(self, name):
        return self._pipelines[name]


_pipelines = PipelineDatabase()

registerPipeline = _pipelines.registerPipeline
getPipelineNames = _pipelines.getPipelineNames
getPipeline = _pipelines.getPipeline

registerPipeline( IncrementalPipelineFactory.getId(),
                  IncrementalPipelineFactory)
                  

