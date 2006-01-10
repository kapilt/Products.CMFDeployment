"""
$Id$
"""

from Products.CMFDeployment import DefaultConfiguration
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

from core import Producer

class ContentSource( Producer ):

    def process( self, pipe, ctxobj ):
        for source in pipe.services["ContentIdentification"].sources.objectValues():
            for content in source.getContent():
                if isinstance( content, AbstractCatalogBrain ):
                    content = content.getObject()

                if content is None:
                    print "egads",  source, content
                    continue

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
            
