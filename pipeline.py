"""
$Id$
"""

import segments

from segments.core import PolicyPipeline, PipeExecutor

from Namespace import getToolByName
import DefaultConfiguration

class PipelineFactory( object ):

    id = None

    def __call__( self ):
        raise NotImplemented

    def getId( klass ):
        return klass.id

    getId = classmethod( getId )

    def finishPolicyConstruction( self, policy ):
        raise NotImplemented

    def beginPolicyRemoval( self, policy ):
        raise NotImplemented
    

class IncrementalPipelineFactory( PipelineFactory ):
    
    id = 'incremental'
    
    class IncrementalEnvironment( segments.core.PipeSegment ):

        def process( self, pipeline, context ):
            iresolver = pipeline.services['ContentResolver']
            resolver  = pipeline.services['DeploymentPolicy'].getDeploymentURIs()
            iresolver.uris = resolver.uris

            dtime = pipeline.services['DeploymentPolicy'].getDeploymentHistory().getLastTime()
            pipeline.variables['LastDeployTime'] = dtime

            return context

    def __call__( self ):

        deletion_pipeline  = self.constructDeletionPipeline()
        processor_pipeline = self.constructContentProcessorPipeline()
        storage_pipeline   = self.constructContentStoragePipeline()
        dv_pipeline = self.constructDirectoryViewPipeline()
        reg_pipeline = self.constructRegistryPipeline()

        policy_pipeline = PolicyPipeline( 
            steps = (
               segments.environment.PipeEnvironmentInitializer(),
               self.IncrementalEnvironment(),
               segments.skin.SkinLock(),
               deletion_pipeline,
               segments.user.UserLock(),
               processor_pipeline,
               dv_pipeline,
               reg_pipeline,               
               storage_pipeline,
               segments.user.UserUnlock(),
               segments.skin.SkinUnlock(),
               segments.transport.ContentTransport()
               )
            )

        return policy_pipeline


    def finishPolicyConstruction( self, policy ):
        """
        add incremental policy index, deletion source, and dependency source
        """

        import incremental
        catalog = getToolByName( policy, 'portal_catalog' )
        pidx_id = incremental.getIncrementalIndexId( policy )
        catalog.manage_addIndex( pidx_id,
                                 incremental.PolicyIncrementalIndex.meta_type )

        import sources
        sources.deletion.addDeletionSource( policy,
                                            DefaultConfiguration.DeletionSource )
        
        sources.dependency.addDependencySource( policy,
                                                DefaultConfiguration.DependencySource )

        
    def beginPolicyRemoval( self, policy ):
        """
        remove any non contained instance objects associated with policy.
        ie. policy incremental index
        """

        import incremental
        catalog = getToolByName( policy, 'portal_catalog' )
        pidx_id = incremental.getIncrementalIndexId( policy )
        catalog.manage_delIndex( ids=[ pidx_id ] )
              

    #################################
    # private methods for easy subclass construction
    def constructContentProcessorPipeline( self ):
        return PipeExecutor(
            
            steps = (
                segments.source.ContentSource(),
                segments.unique.UniqueGuard(),
                segments.filter.ContentFilter(),
                segments.rule.ContentRuleMatch(),
                segments.resolver.ResolverDatabase(),
                segments.dependency.DeployDependencyInjector(),
                segments.core.VariableAggregator("descriptors")
                )
            )

    def constructContentStoragePipeline(self):
        # a name almost long enough to be in java ;-)
        return PipeExecutor(

            steps = (
                segments.core.VariableIterator("descriptors"),
                segments.render.ContentRender(),
                segments.deletion.RecordDeployment(),
                segments.resolver.ResolveContent(),
                segments.storage.ContentStorage()
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
        return segments.directoryview.DirectoryViewDeploy( incremental=True)

    def constructRegistryPipeline( self ):
        return segments.registry.RegistryDeploy( incremental=True)


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
                  IncrementalPipelineFactory())
                  

