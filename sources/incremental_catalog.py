"""
$Id: basic_catalog.py 940 2005-08-16 07:50:44Z hazmat $
"""


from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

def addIncrementalPortalCatalogSource( self,
                            id,
                            title='',
                            RESPONSE=''):
    """ riddle me this, why is a doc string here..
        answer: bobo
    """

    self._setObject( id, IncrementalPortalCatalogSource(id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addIncrementalPortalCatalogSourceForm = DTMLFile('../ui/IdentificationIncrementalPortalCatalogSourceForm', globals() )

class IncrementalPortalCatalogSource(SimpleItem):

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
        
    def getContent(self, last_time=None):
        #print "incremental_catalog: getContent"
        catalog = getToolByName(self, 'portal_catalog')
        query = {}
        if last_time is not None:
            query = {'modified': {'query':last_time, 'range':'min'}}
        objects = catalog(query)
        
        #we only take those that has been added, modified or 
        #deleted since the last  time
        
        #for those that has been added or 
        #modified we check the ModificationTime
        #for ci in objects:
        #    print " ---- incremental_cat: FOR: content: ", ci.getPath(), "----"
        
        #for those that has been deleted, we check the DeletionSource
        
        return objects
