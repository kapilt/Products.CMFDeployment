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
        self.factory = None # descriptor factory

    def process( self, pipe, content ):

        rules = pipe.services["ContentRules"]
        factory = self.getFactory( pipe )

        descriptor = factory( content )

        if not rules.prepare( descriptor ):
            try: content._p_deactivate()
            except: pass
            return OUTPUT_FILTERED

        return descriptor

    def getFactory(self, pipe):
        if self.factory:
            return self.factory
        factory_class = pipe.services["DescriptorFactory"]
        # this could be trimmed down ..
        self.factory = factory_class( pipe.services["DeploymentPolicy"] )
        return self.factory
