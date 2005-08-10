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
descriptors are responsible for returning both dependencies and reverse
dependencies. 

there are a number of different policy considerations that need to be taken
into account when dealing with dependencies, with an eye towards modeling
default policies appropriately. policies govern how the dependencies are
handled by the system, some policy examples.

 - when an object's dependencies are modified, then the object will be
   redeployed. [ default ]

 - when one of an object's dependencies is removed, then the object will
   be have its workflow changed (with a filter preventing deployment).
   [ policy ]
   
an object's dependencies model other objects that need to be deployed
with an object. ie. a document with embedded media references, has
dependencies on those other objects.

 - a container with contained objects, a common use case is a 

reverse dependencies model the inverse relationship, if an object is
modified those objects that it depends on also need redeployment.

dependencies are provided by the content descriptor and they are dynamic.
ie they are queried from a descriptor.


Author: Kapil Thangavelu <hazmat@objectrealms.net>
$Id$
"""

from Namespace import *
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

class Dependency( object ):

    __slots__ = ( 'orid', 'policy' )

class BasePolicy( object ):

    def dependencyDeleted( self, descriptor, source, dependency ):
        pass

    def dependencyModified( self, descriptor, source, dependency ):
        pass

    def process( self, descriptor, dependency ):
        pass
    
class PolicyManager( object ):
    pass

class DependencyManager( SimpleItem ):

    def __init__(self):
        self._rdepends = IOBTree()
        self._depends  = IOBTree()

    def addEntry( descriptor ):
        dependencies = descriptor.getDependencies()
        rid = self.getCatalogRID( descriptor.getContent() )

        if not rid in self._depends:
            dstore = OOBTree()
            self._depends[rid] = dstore
        else:
            dstore = self._depends.get( rid )
        
        for d in dependencies:
            drid = self.getCatalogRID( d )

    def delEntry( self, rid ):
        
        if rid in self._depends:
            del self._depends[ rid ]

        if not rid in self._rdepends:
            return

        rdepends = self._rdepends[ rid ]
        for rd in rdepends:
            pass
            
InitializeClass( DependencyManager )        
        
            
        
