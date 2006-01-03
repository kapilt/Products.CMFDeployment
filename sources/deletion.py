"""
$Id$
"""


from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

def addDeletionSource( self, id, title="", RESPONSE=None):
    """ add a deletion source
    """
    source = DeletionSource( id, title )
    self._setObject( id, source )

    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')

addDeletionSourceForm = DTMLFile('../ui/SourceDeletionForm', globals())

class DeletionSource( SimpleItem ):
    """
    stores records for content deleted through the portal lifecycle.
    """

    __implements__ = IContentSource
    
    def __init__(self, id, title=""):
        self.id = id
        self._records = []

    def getContent( self ):
        return self.destructiveIter()
        
    def destructiveIter(self):
        for rec in self._records:
            yield rec
        self._records = []

    def addRecord( self, record ):
        self._records.append( record )
        self._p_changed = 1



    
