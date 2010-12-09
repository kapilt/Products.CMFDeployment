"""
$Id: source.py 1135 2006-01-20 10:20:40Z hazmat $
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
                    #print "egads",  source, content
                    continue

                yield content

        dependency_source = pipe.services['DeploymentPolicy']._getOb(
            DefaultConfiguration.DependencySource, None )

        if dependency_source is None:
            raise StopIteration

        for content in dependency_source.getContent():
            if content is None:
                #print "bad dep"
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
            
