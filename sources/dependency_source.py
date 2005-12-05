"""
$Id: basic_catalog.py 940 2005-08-16 07:50:44Z hazmat $
"""


from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

def addDependencySource( self,
                            id,
                            title='',
                            RESPONSE=''):
    """ riddle me this, why is a doc string here..
        answer: bobo
    """

    self._setObject( id, DependencySource(id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addDependencySourceForm = DTMLFile('../ui/IdentificationDependencySourceForm', globals() )

class DependencySource(SimpleItem):

    meta_type = 'Dependency Source'

    __implements__ = IContentSource

    manage_options = (
        {'label':'Source',
         'action':'source'},        
        )
    
    source = DTMLFile('../ui/ContentSourceView', globals())

    def __init__(self, id, title='retrieves content from dependency_source'):
        self.id = id
        self.title = title
        self._queue = []
        
    def getContent(self, last_time=None):
        #print "dependency_source: GET CONTENT!!!"
        return self.destructiveIter()

    def destructiveIter(self):
        for rec in self._queue:
            yield rec
        self._queue = []
        
    def addObject( self, descriptor ):
        #print "dependency_source: ADD OBject: ", descriptor.content_url
        if not descriptor in self._queue:
            
            self._queue.append( descriptor )
            self._p_changed = 1
            
            
            