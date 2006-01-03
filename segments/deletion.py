from core import PipeSegment

class DeletionSegment( PipeSegment ):

    def process( self, pipeline, descriptor ):
        storage = pipeline.services['ContentStorage']
        organization = pipeline.services['ContentOrganization']
        dependencies = pipeline.services['ContentDependencies']

        path = organization.getContentPathFromDescriptor( record )
        storage.remove( descriptor )


        

        
        
