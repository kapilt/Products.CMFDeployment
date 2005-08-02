"""
$Id$
"""

from Namespace import *
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

class Dependency( object ):

    __slots__ = ( 'orid', 'policy' )

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
            
        
        
            
        
