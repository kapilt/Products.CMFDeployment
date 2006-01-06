"""
$Id$
"""

from core import Filter, OUTPUT_FILTERED

class ContentRuleMatch( Filter ):
    """
    prepares a piece of content to be deployed, determines matching
    rulel, creates descriptor, and adds to uri resolver.
    """

    def __init__(self):
        self.prepared = []
        self.factory = None

    def getDescriptorFactory(self, pipe):
        if self.factory:
            return self.factory
        factory_class = pipe.services["DescriptorFactory"]
        policy  = pipe.services["DeploymentPolicy"]
        self.factory = factory_class(policy)
        return self.factory
        
    def process( self, pipe, content ):

        factory = self.getDescriptorFactory( pipe )
        rules = pipe.services["ContentRules"]
        resolver = pipe.services['URIResolver']
        
        descriptor = factory( content )

        if not rules.prepare( descriptor ):
            try: content._p_deactivate()
            except: pass
            return OUTPUT_FILTERED

        resolver.addResource( descriptor )
        return descriptor
