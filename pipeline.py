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

    def __call__( self ):

        deletion_pipeline = self.constructDeletionPipeline()
        content_pipeline = self.constructContentPipeline()
        dv_pipeline = self.constructDirectoryViewPipeline()

        policy_pipeline = PolicyPipeline( 
            steps = (
               segments.environment.PipeEnvironmentInitializer(),
#               dv_pipeline,
#               deletion_pipeline,
               content_pipeline,
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
        pidx_id = getPolicyIndexId( policy )
        catalog.manage_addIndex( pidx_id,
                                 incremental.PolicyIncrementalIndex.meta_type )

        import sources
        sources.deletion.addDeletionSource( policy,
                                            DefaultConfiguration.DeletionSource)
        

        
    def beginPolicyRemoval( self, policy ):
        """
        remove any non contained instance objects associated with policy.
        ie. policy incremental index
        """

        catalog = getToolByName( policy, 'portal_catalog' )
        pidx_id = getPolicyIndexId( policy )
        catalog.manage_delIndex( ids=[ pidx_id ] )
              

    #################################
    # private methods for easy subclass construction
    def constructContentPipeline( self ):
        return PipeExecutor(
            
            steps = (
                segments.source.ContentSource(),
                segments.filter.ContentFilter(),
                segments.rule.ContentRuleMatch(),
                segments.resolver.ResolverDatabase(),
                segments.dependency.DeployDependencyInjector(),
                segments.render.ContentRender(),
                segments.resolver.ResolveContent,
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


def getPolicyIndexId( policy ):
    pidx_id = "%s-%s"%(policy.getId(), "policy_index")
    return pidx_id


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
                  

