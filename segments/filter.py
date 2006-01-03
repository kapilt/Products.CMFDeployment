"""
$Id$
"""

from core import Filter, OUTPUT_FILTERED

class ContentFilter( Filter ):

    def process( self, pipe, content ):
        restricted = self.getRestrictedId( pipe )
        mount_length = pipe.variables['mount_length']
        
        portal = self.getPortal( pipe )
        
        path = "/".join( content.getPhysicalPath() )[mount_length:]
        for rst in restricted:
            if rst in path:
                return None

        ec = getFilterExprContext( content, portal )

        for f in self.getFilters( pipe ):
            if isinstance( f, ContentFilter) and not f.filter(fc):
                log.debug('Filtered Out (%s) (%s)->(%s)'%(f.getId(), c.portal_type, c.getPath()))
                return OUTPUT_FILTERED
            elif not f(content):
                log.debug('Scripted Out (%s) (%s)->(%s)'%(s.getId(), c.portal_type, c.getPath()))
                return OUTPUT_FILTERED
        return content
        
    def getRestrictedIds(self, pipe):
        structure = pipe.services['ContentOrganization'].getActiveStructure()
        return tuple( structure.restricted )

    def getPortal(self, pipe):
        return pipe.services['ContentOrganization'].portal_url.getPortalObject()
        
        

        
