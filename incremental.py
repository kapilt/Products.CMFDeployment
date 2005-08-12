"""
ROUGH DRAFT

defines the operation of the incremental pipeline for deployment.

deploying content on an incremental basis is a straight forward though
complex process. the naive initial implementation in cmfdeployment 1.0,
merely deployed content created/modified since the last deployment
run. real world experience quickly proved this to be fatally flawed for
a number of reasons.

  - content often have interdependencies that need to be modeled
    in an incremental deployment system.

  - the engine needed to process content deletions, previously the
    deployment engine dealt only with publishing.


the incremental engine uses the following components, arranged as shown
in the diagram of an execution pipeline below.

  Dependency Manager

   Responsible for processing a descriptor's specified dependencies
   and reverse dependencies to ensure their included in the deployment.

  IncrementalPolicyIndex

   A plugin zcatalog index, installed into the portal catalog, and used
   to track when a deployed piece of content is deleted, and then
   adds a deletion record to the policy's deletion source [below]

  Plugin Content Sources

   AlwaysDeployed Source

    returns content marked to be deployed every run. 

   Deletion Source

    a content source for deletion records.

   Dependency Source

    a source for deletions, as injected by the dependency manager.

   the dependency plugin content source is injected to during
   the pipeline execution. a duplicate eliminating filter needs
   to be utilized in the pipeline execution ( earlier the better ).

  Pipeline Invariant
  
    - deployed content filtered out will trigger deletion descriptor
      creation.

 ------

 Incremental Pipeline Diagram 

 Content Sources --<                  catalog | deletions | dependencies
     +                                             +              +
     +                                             +              +
  Filters                                          +              + 
     +                                             +              +
     +                                             +              +
  Content Rules                                    +              +
     +                                             +              +
     +                                             +              +
  Dependency Manager  ---------------------------------------------
     +                                             +
     +                                             +
  Resolver                                         +
     +                                             +
     +                                             +
  ContentMap -----------------------------IncrementalIndex
  

Todo

 - api for cleaning state from a descriptor [ and children ]
   to make ready for serialization.

     
$Id$
"""


from Namespace import *
from BTrees.Length import Length
from BTrees.IOBTree import IOBTree
from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface

#################################
# pipeline processing of deletion records
#
#  - get and inject dependencies into queue
#
#  - remove from resolver
#
#  - remove from storage

class DeletionRecord( object ):
    """
     models a content record ..

     really a deletion descriptor
     
     processed by deletion pipeline
    """

    def __init__(self, descriptor ):
        self.descriptor = descriptor


class DeletionSource( SimpleItem ):
    """
    stores records for content deleted through the portal lifecycle.
    """

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

    def manage_beforeDelete( self, item, container):
        # check on removal of incremental index
        pass

class PolicyIncrementalIndex( SimpleItem ):
    """
    abuses the catalog plugin index interface to get events for content
    deletion also stores the info re the set of objects deployed by the
    corresponding policy.
    """
    
    meta_type = "Policy Incremental Index"
    
    __implements__ = PluggableIndexInterface

    manage_options = (

        {'label':'Overview',
         'action':'index_overview'},

        {'label':'Index',
         'action':'idx/manage_workspace'}

        )

    security = ClassSecurityInfo()

    index_overview = DTMLFile('zmi/IncrementalIndexView', globals())    

    def __init__(self, id, extra, caller=None):
        self.id = id
        self.policy_id = ""
        self._length = Length()
        self._index = IOBTree()

    def getId(self):
        return self.id

    def getEntryForObject( self, documentId, default=None):
        return self._index.get( documentId, default )

    def index_object( self, documentId, obj, threshold=None):
        # policy execution directly populates through the
        # recordObject api.
        return

    def unindex_object( self, documentId):
        if not self._index.has_key(documentId):
            return
        
        dtool = getToolByName( self, 'portal_deployment')
        policy = dtool._getOb( self.policy_id )

        sources = policy.getContentSources()
        deletion_source = sources._getOb('deletion_source', None)
        
        if deletion_source is None:
            return

        content = self.getObjectFor( documentId )
        rules = policy.getContentRules()
        factory = DescriptorFactory( policy )
        descriptor = factory( content )

        if not rules.prepare( descriptor ):
            # should still construct minimal deletion record
            return

        record = DeletionRecord( descriptor )
        deletion_source.addRecord( record )
        
        del self._index[documentId]
        self._length(-1)

    def _apply_index( request, cid=""):
        # XXX return emtpy ruleset?
        return None

    def numObjects(self):
        return self._length()

    def clear(self):
        # i can't do that jim ;-)
        return

    #################################
    def isObjectDeployed( self, object ):
        path = '/'.join( object.getPhysicalPath() )
        rid = self.getrid( path )
        return not not rid
    
    def getObjectFor( self, documentId ):
        return self.getobject( documentId )
    
    def recordObject(self, object):
        catalog = self.aq_parent
        path = '/'.join( object.getPhysicalPath() )
        key = catalog.uids.get( path, None )
        
        if key is None:
            # not sure if we should do this.. 
            pcatalog = getToolByName(self, 'portal_catalog')
            pcatalog.indexObject( pcatalog )

            key = catalog.uids.get( path )
            assert key is not None
            
        self._index[ key ] = path
