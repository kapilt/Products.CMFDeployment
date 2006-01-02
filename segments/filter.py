"""
$Id$
"""

class ContentFilterSegment( object ):

    def process( self, pipe, brain ):

        restricted = self.getRestrictedId( pipe )
        mount_length = self.getMountPointPathLength( pipe )
        portal = self.getPortal( pipe )
        
        path = brain.getPath()
        for rst in restricted:
            if rst in path:
                return None

        ec = getFilterExprContext( c, portal )

        for f in self.getFilters( pipe ):
            if isinstance( f, ContentFilter) and not f.filter(fc):
                log.debug('Filtered Out (%s) (%s)->(%s)'%(f.getId(), c.portal_type, c.getPath()))
                return None
            elif not f(c):
                log.debug('Scripted Out (%s) (%s)->(%s)'%(s.getId(), c.portal_type, c.getPath()))
                return None
        return f
        
        
    def getRestrictedIds(self, pipe):
        pass

    def getMountPointPathLength( self, pipe ):
        pass

    def getPortal(self, pipe):
        pass
        
        

        
