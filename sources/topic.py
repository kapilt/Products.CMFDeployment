"""
Topic Sources are containers for zmi topics, any number of zmi topics can
be included in a topic source, the results from each topic are utilized
as the values from this source.

$Id$
"""

# import check that zmi topics are present 
from Products.ZMITopic.topic import ZMITopic

from Globals import DTMLFile
from OFS.Folder import Folder
from Products.CMFDeployment.DeploymentInterfaces import IContentSource
from base import BaseSource

def addTopicSource( self,
                    id,
                    title='',
                    RESPONSE=None):

    """
    add a topic source
    """

    self._setObject( id, TopicSource( id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addTopicSourceForm = DTMLFile('../ui/SourceTopicForm', globals())

class TopicSource( Folder, BaseSource ):

    meta_type = "Topic Content Source"

    xml_factory = 'addTopicSource'
    
    __implements__ = IContentSource

    def all_meta_types(self):
        import Products
        return [m for m in Products.meta_types if m['name']=='ZMI Topic']

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    def getContent(self):
        for topic in self.objectValues():
            for res in topic.queryCatalog():
                yield res
