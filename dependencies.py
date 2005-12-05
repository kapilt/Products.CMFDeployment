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
from Products.CMFCore.utils import getToolByName

from incremental import getIncrementalIndexId



from segments import *

class DependencyManager( PipeSegment ):

    implements( IProducer )
        
    def process(self, pipe, content):
        self.policy= pipe.services['DeploymentPolicy']
        self.content_map= self.policy.getContentMap()
        self.factory = pipe.services["DescriptorFactory"]
        self.mastering = self.policy.getContentMastering()
        self.policy_id = self.policy.getId()
        self.catalog= getToolByName(self.policy, "portal_catalog")
        stats = pipe.services["TimeStatistics"]      
        mstats = pipe.services["MemoryStatistics"]
        stats ('Deploying dependencies', relative='View deployed')
        mstats('Deploying dependencies')

        for c in content:
            self.processDeploy(c)
        
        return content
        
    def processDeploy( self, descriptor ): 
        source = self.policy.getDependencySource()
        if not source:
            return

        # deploy objects that depend on descriptor    
        
        for apath in self.content_map.getReverseDependencies(descriptor): 
            rid = self.catalog.getrid(apath)
            
            if rid== None:
                #the object doesn't exist anymore
                continue
                
            content = self.catalog.getobject(rid)
            
            desc = self.factory( content )
            self.mastering.prepare(desc)
            source.addObject( desc )

        # deploy objects that are needed by descriptor
        #  - check first that they aren't already deployed
        iidx = self.getIncrementalIndex()
        
        for dep in descriptor.getDescriptors():
            if iidx.isObjectDeployed( dep ):
                continue
            self.mastering.prepare(dep)
            source.addObject( dep )
            
        
    def getIncrementalIndex(self):
        return getIncrementalIndexId( self.policy )
    
        
InitializeClass( DependencyManager )        
