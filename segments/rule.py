"""
$Id$
"""

from core import PipeSegment

class ContentRuleMatch( PipeSegment ):
    """
    prepares a piece of content to be deployed, determines matching
    rulel, creates descriptor, and adds to uri resolver.
    """
    
    implements( IProducerConsumer )

    def __init__(self):
        self.prepared = []

    def process( self, pipe, context ):
        return self.processContent( c )

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
        return descriptor


    def getContent( self, ctxobj ):
        return ctxobj.getObject()
