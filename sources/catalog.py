"""
$Id$
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

def addPortalCatalogSource( self,
                            id,
                            title='',
                            RESPONSE=''):
    """ riddle me this, why is a doc string here..
        answer: bobo
    """

    self._setObject( id, PortalCatalogSource(id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addPortalCatalogSourceForm = DTMLFile('../ui/SourceCatalogForm', globals() )

class PortalCatalogSource(SimpleItem):

    meta_type = 'Catalog Content Source'

    __implements__ = IContentSource

    manage_options = (
        {'label':'Source',
         'action':'source'},        
        )
    
    source = DTMLFile('../ui/ContentSourceView', globals())

    def __init__(self, id, title='retrieves content from portal_catalog'):
        self.id = id
        self.title = title
        
    def getContent(self):
        catalog = getToolByName(self, 'portal_catalog')
        objects = catalog()
        return objects


def addIncrementalCatalogSource( self,
                                 id,
                                 title='',
                                 RESPONSE=''):
    """ add an incremental catalog source
    """

    self._setObject( id, IncrementalCatalogSource(id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addIncrementalCatalogSourceForm = DTMLFile('../ui/SourceIncrementalCatalogForm', globals() )

class IncrementalCatalogSource(SimpleItem):

    meta_type = 'Incremental Catalog Content Source'

    __implements__ = IContentSource

    manage_options = (
        {'label':'Source',
         'action':'source'},        
        )
    
    source = DTMLFile('../ui/ContentSourceView', globals())

    def __init__(self, id, title='retrieves content from portal_catalog'):
        self.id = id
        self.title = title
        
    def getContent(self):
        """
        return all content modified/created since the last deployment.
        """
        catalog = getToolByName(self, 'portal_catalog')
        last_deployment_time = self.getDeploymentHistory().getLastTime()
        
        if last_deployment_time is not None:
            query = {'modified': {'query':last_time, 'range':'min'} }
        else:
            query = {}
            
        objects = catalog(**query)
        
        return objects