"""
$Id$
"""

from core import Filter

class ContentRuleMatch( Filter ):
    """
    prepares a piece of content to be deployed, determines matching
    rulel, creates descriptor, and adds to uri resolver.
    """

    def __init__(self):
        self.prepared = []

    def process( self, pipe, content ):
        factory = pipe.services["DescriptorFactory"]
        rules = pipe.services["ContentRules"]
        resolver = pipe.services['URIResolver']
        
        descriptor = factory( content )

        if not rules.match( descriptor ):
            try: content._p_deactivate()
            except: pass
            return

        resolver.addResource( descriptor )
        return descriptor
