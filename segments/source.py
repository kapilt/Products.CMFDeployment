"""
$Id$
"""

from core import Producer

class ContentSource( Producer ):

    def process( self, pipe, ctxobj ):
        for source in pipe.services["ContentIdentification"].sources.objectValues():
            for content in source.getContent():
                yield content
