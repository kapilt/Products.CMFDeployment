"""

Segments for changing user during deployment to configured deployment user,
and changing it back after deployment.

$Id$
"""

from core import PipeSegment

class UserLock( PipeSegment ):

    def process( self, pipe, context ):
        rules = pipe.services['ContentRules']
        rules.site_user.lock()

class UserUnlock( PipeSegment ):

    def process( self, pipe, context ):
        rules = pipe.services['ContentRules']
        rules.site_user.unlock()
        
