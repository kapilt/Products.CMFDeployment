"""
$Id$
"""

from Products.CMFDeployment import DefaultConfiguration
from core import Producer

class ContentSource( Producer ):

    def process( self, pipe, ctxobj ):
        for source in pipe.services["ContentIdentification"].sources.objectValues():
            for content in source.getContent():
                yield content

class ContentDeletion( Producer ):

    def process( self, pipe, ctxobj ):
        source = pipe.services['DeploymentPolicy']._getOb(
            DefaultConfiguration.DeletionSource, None
            )

        if source is None:
            raise StopIteration

        for record in source.getContent():
            yield record
