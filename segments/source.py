from core import IProducer, PipeSegment

class ContentSource( PipeSegment ):

    implements( IProducer )

    def process( self, pipe, ctxobj ):
        for source in pipe.services["ContentIdentification"].sources.objectValues():
            for content in source.getContent():
                yield content
