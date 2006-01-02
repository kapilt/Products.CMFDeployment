from segments import *

class PolicyPipeline( Pipeline ):

    def __call__( self, policy ):
        self.process( policy )



class ContentPreparation( PipeSegment ):
    pass
    


#################################
# pipeline - todo conditional matching on record or descriptor        
# segment - uindex / dependency manager /

class DeletionPipeline( object ):

    def condition(self):

    def process( self, record ):
        pass

"""

  initializer [ policy ] -> policy
  directoryviewdeploy [ policy ] -> policy
  content source [ policy ] -> content stream
    iterator
  
  
  
"""

class DefaultPolicyPipeline( object ):
    
    step_factories = [ PipeEnvironmentInitializer,
                       ContentSource,
                       ContentPrepPipe,
                       DirectoryViewDeploy,
                       ContentProcessPipe ]
    
IncrementalPipeline = Pipeline(
    steps = ( PipeEnvironmentInitializer(),
              ContentSource(),
              ConditionalBranch(
                      
              Iterator( ( ContentPrepPipeline, ) ),
              DirectoryViewDeploy(),
              
         

        
        
        
