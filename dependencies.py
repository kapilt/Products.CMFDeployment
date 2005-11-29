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

from incremental import getIncrementalIndexId


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
        
    def addObject( self, descriptor ):
        #print "Dependencies: ADD OBject: ", descriptor
        if not descriptor in self._queue:
            self._queue.append( descriptor )
            self._p_changed = 1
        
InitializeClass( DependencySource )

from segments import *

class DependencyManager( PipeSegment ):

    implements( IProducer )

    def __init__(self, id, policy_id=None, catalog=None):
        self.id = id
        self.policy_id = policy_id
        self.catalog= catalog
        
    def process(self, pipe, content):
        self.source= pipe.services['ContentIdentification']
        self.policy= pipe.services['DeploymentPolicy']
        self.content_map= pipe.services['ContentMap']
        self.factory = pipe.services["DescriptorFactory"]
        self.mastering = pipe.services["ContentMastering"]
        #print "dependencies: process: content: ", content
        for c in content:
            self.processDeploy(c)
        
    def processDeploy( self, descriptor ):  
        source = self.getDependencySource()
        if not source:
            return

        # deploy objects that depend on descriptor    
        
        #print "dependencies: descriptor: ", descriptor    
        for apath in self.content_map.getReverseDependencies(descriptor): 
            rid = self.catalog.getrid(apath)
            
            if rid== None:
                #the object doesn't exist anymore
                continue
                
            the_object = self.catalog.getobject(rid)
            
            #we've got URL, we have to take the descriptor corresponding
            #and add the descriptor
            content = the_object
            desc = self.factory( content )
            #print "*** dependencies: addObj1: ", desc.getContent()   
            source.addObject( desc )

        # deploy objects that are needed by descriptor
        #  - check first that they aren't already deployed
        iidx = self.getIncrementalIndex()
        
        for dep in descriptor.getDescriptors():
            if iidx.isObjectDeployed( dep ):
                continue
            #print "*** dependencies: addObj2: ", dep.getContent()
            source.addObject( dep )

    def processRemoval( self, record):
        # XXX deletion record record deps on creation
        source = self.getDependencySource()
        if not source:
            return None
        descriptors= source.getContent()
        try:
            while(True):
                descr= descriptors.next()
                #print "dependencies: on cuisine : ", descr.content_url
                self.mastering.cook(descr)
        except:
            pass
            
        descriptor= record.descriptor
        the_dependencies= self.content_map.getReverseDependencies(descriptor)
            
        for apath in the_dependencies:        
            rid = self.catalog.getrid(apath)
            
            if rid== None:
                #the object doesn't exist anymore
                continue
                
            the_object = self.catalog.getobject(rid)
            
            #we've got URL, we have to take the descriptor corresponding
            #and rerender the content
            content = the_object
            desc = self.factory( content )
            #print "dependencies: on cuisine les pred : ", desc.content_url
            self.mastering.cook(desc)
        
        #we clean the content map, deleting all the links on the descriptor
        self.content_map.clean(descriptor)
        
    def getIncrementalIndex(self):
        return getIncrementalIndexId( self.policy )
    
    def getDependencySource(self):
        sources = self.source.sources
        
        source = sources._getOb( 'dependency_source', None)
        return source
        
InitializeClass( DependencyManager )        
