from core import PipeSegment

class ContentRender( PipeSegment ):

    def process( self, pipe, descriptor):
        rules = pipe.services["ContentRules"]
        store = pipe.services["ContentStorage"]
        
        rules.cook( descriptor )
        return descriptor
    
        if not descriptor.isGhost():
            resolver.resolve( descriptor )
            
        store( descriptor )
