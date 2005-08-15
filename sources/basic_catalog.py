"""
$Id$
"""


from Products.CMFDeployment.Namespaces import *
from Products.CMFDeployment.Interfaces import IContentSource

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

addPortalCatalogSourceForm = DTMLFile('../ui/IdentificationPortalCatalogSourceForm', globals() )

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
