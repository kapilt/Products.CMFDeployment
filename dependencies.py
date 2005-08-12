"""

Dependencies are the heart of the incremental deployment pipeline.

they are designed to answer a simple question, ie. if i deploy object A
what other objects do i need to deploy along with it, and conversely
if i delete object B what are there objects should i delete with it.

there are many examples of dependency relationships, and the dependency
engine delegates dependency specification to other components, primarily
content rules, and obtains the spec from a descriptor. some dependency
examples.

 - a document with embedded object references ( author, files ), etc.

 - a container that displays a listing view of its contents, is dependent
   on all of them.

its important to state that cmfdeployment is only concerned with dependencies
as pertains to the object's rendered views that will be deployed, ie. strictly
ui dependencies.

also the dependency manager participates as a component in a deployment
pipeline and dependencies deployed must still pass all filters, and match
to a content rule, else they won't be deployed by the system. also its assumed
that the dependency engine is injecting dependencies into a pipeline that
has a processing segment that will stop introduction of duplicates.

dependency injection via use of a dependency content source.

a design goal is to keep the dependency manager as simple as possible, and
thus stateless as previous experiments with automatic tracking of content
have show it to be overly complex (at least without an event system ;-) ).
so descriptors are responsible for returning both dependencies and reverse
dependencies. this also eases consideration of dynamic dependencies.

Author: Kapil Thangavelu <hazmat@objectrealms.net>
$Id$
"""

from Namespace import *
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from DeploymentInterfaces import IContentSource

class DependencySource( SimpleItem ):
    """
    """
    
    meta_type = "Dependency Source"
    
    __implements__ = IContentSource
    
    def __init__(self, id, title=""):
        self.id = id
        self.title = title
        self._queue = []

    def getContent(self):
        return self.destructiveIter()

    def destructiveIter(self):
        for rec in self._queue:
            yield rec
        self._queue = []
        
    def addObject( self, object ):
        self._queue.append( object )
        self._p_changed = 1
        
InitializeClass( DependencySource )


class DependencyManager( SimpleItem ):

    def __init__(self, id, policy_id=None):
        self.id = id
        self.policy_id = policy_id
        
    def processDeploy( self, descriptor ):

        dependencies = descriptor.getDependencies()
        if not dependencies:
            return

        source = self.getDependencySource()
        if not source:
            return

        # deploy objects that depend on descriptor
        for rdep in descriptor.getReverseDependencies():
            source.addObject( rdep )

        # deploy objects that are needed by descriptor
        for dep in descriptor.getDependencies():
            source.addObject( dep )

    def processRemoval( self, record ):
        # XXX deletion record record deps on creation
        pass
    
    def getDependencySource(self):
        sources = self.getContentSources()
        source = sources._getOb( 'dependency_source', None)
        return source
        
InitializeClass( DependencyManager )        
        
            
class BasePolicy( object ):

    def dependencyDeleted( self, descriptor, source, dependency ):
        pass

    def dependencyModified( self, descriptor, source, dependency ):
        pass

    def process( self, descriptor, dependency ):
        pass

class PolicyManager( object ):
    pass

