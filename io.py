"""
a new xml export/import system, utilizes a genericized form that allows for
just passing nested python types (lists,dictionaries, etc ) to the
exporter, and getting the same back from the importer.

construction in turn follows from the python data structure, and is pluggable
by registering against a handler against path into the data structure.

compatibility for the new impl is in two stages, on old xml formats
we use the old parser for a release cycle, its now depreceated.

for the new format, compatibility will be via a series of python transforms
applied the nested python data structure.

$Id$
"""

import time, types, StringIO
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from xml.sax import make_parser, ContentHandler

_marker = object()

class ImportReader( ContentHandler ):

    _types = {
        u"string" : types.StringType,
        u"int" : types.IntType,
        u"bool" : types.BooleanType,
        u"dict" : types.DictType,
        u"list" : types.ListType
        }

    subnode_types = ( types.ListType, types.DictType, types.TupleType )

    def __init__(self):
        self.buf = []
        self.root = {}
        self.current_path = ''
        self.current_type = u'string'

    def getData(self):
        return self.root
        
    def startElement( self, element_name, attrs ):
        d = {}
        for k, v in attrs.items():
            d[str(k)] = str(v)
        v_type = d.get('type')

        # everything in the new format should have a type code.

        self.current_path += ".%s"%element_name
        self.current_type = v_type

        if v_type is None:
            v_type = 'dict'

        factory = self._types[ v_type ]
        
        if factory in self.subnode_types:
            self.createData( self.current_path, v_type )

        if len(d) > 1: # has 'real' attributes
            #print d['type'], d
            assert d['type'] == 'dict'
            del d['type']
            path = self.current_path + ".attributes"
            self.createData( path, 'dict', d)
            
    def endElement( self, element_name ):
        assert self.current_path.endswith( element_name ), "%s %s"%( self.current_path, element_name )
        
        if self.buf:
            data = "".join( self.buf )
            self.createData( self.current_path, self.current_type, data)
            self.buf = []
            
        if self.current_path.rfind('.') != -1:
            idx = self.current_path.rfind('.') 
            self.current_path = self.current_path[:idx]

    def characters( self , characters ):
        self.buf.append( characters )
        
    def createData( self, path, type_code, data=_marker):
        factory = self._types[ type_code ]
        if data is not _marker:
            data = factory( data )
        else:
            data = factory()
        last, last_part = self._traverse( path )
        if last_part == 'entry':
            last.append( data )
        else:
            last[ last_part ] = data
            
    def _traverse( self, path ):
        
        last = self.root
        parts = path.split('.')
        parts.pop(0)
        last_part = parts.pop(-1)
        
        for p in parts:
            if p == 'entry':
                last = last[-1]
            else:
                last = last[ p ]
                
        return last, last_part
    
class ExportSerializer( object ):

    _values = {
        types.StringType : "dumpEntry",
        types.IntType : "dumpEntry",
        types.BooleanType : "dumpEntry",
        types.ListType : "dumpList",
        types.TupleType : "dumpList",
        types.DictType : "dumpDictionary"
        }
    
    _attrs = {
        types.StringType : "convertValue",
        types.IntType : "convertValue",
        types.BooleanType : "convertValue",
        }

    _typecode = {
        types.StringType : u"string",
        types.IntType    : u"int",
        types.BooleanType : u"bool",
        types.DictType :  u"dict",
        types.ListType : u"list"
        }

    subnode_types = ( types.ListType, types.DictType, types.TupleType )

    policy_id = u"policy"
    entry_key = u'entry'    
    attributes_key = u'attributes'

    def __init__(self, stream, encoding):
        """
        Set up a serializer object, which takes policies and outputs
        """
        logger = XMLGenerator(stream, encoding)
        self._logger = logger
        self._output = stream
        self._encoding = encoding

        self._logger.startDocument()
        attrs = AttributesNSImpl({}, {})
        self._logger.startElementNS((None, self.policy_id), self.policy_id, attrs)

        self._stack = []

    def close( self ):
        self._logger.endElementNS((None, self.policy_id), self.policy_id )
        self._logger.endDocument()

    def getValueSerializer( self, v ):
        v_type = type( v )

        serializer_name = self._values.get( v_type )
        if serializer_name is None:
            raise ValueError("invalid type for serialization %r"%v_type)

        method = getattr( self, serializer_name )
        assert isinstance( method, types.MethodType), "invalid handler for type %r"%v_type
        
        return method

    def getAttrSerializer( self, v ):
        v_type = type( v )

        serializer_name = self._attrs.get( v_type )
        if serializer_name is None:
            raise ValueError("invalid type for serialization %r"%v_type)

        method = getattr( self, serializer_name )
        assert isinstance( method, types.MethodType), "invalid handler for type %r"%v_type
        
        return method        

    def getTypeCode( self, v ):

        return self._typecode[ type( v) ]
        
    def dumpDictionary( self, key, value ):

        key = unicode( key )        
        subnodes = []

        type_code = self.getTypeCode( value )
        attr_values = { (None, u'type' ) : type_code }
        attr_names  = { (None, u'type' ) : u'type' }

        for k, v in value.get( self.attributes_key, {}).items():
            k = unicode( k )
            assert not isinstance(v, self.subnode_types )
            serializer = self.getAttrSerializer( v )
            
            attr_values[ (None, k ) ] = serializer( v )
            attr_names[ (None,  k ) ] = k

        
        attrs = AttributesNSImpl( attr_values, attr_names )

        self._logger.startElementNS( ( None, key ), key, attrs )

        for k, v in value.items():
            if k == self.attributes_key:
                continue
            serializer = self.getValueSerializer( v )
            serializer( k, v )

        self._logger.endElementNS( ( None, key ), key )
 
    def dumpList( self, key, value ):
        type_code = self.getTypeCode( value )
        attrs = AttributesNSImpl( { (None, u'type' ) : type_code },
                                  { (None, u'type' ) : u'type' } )
        self._logger.startElementNS( ( None, key ), key, attrs )

        for entry in value:
            serializer = self.getValueSerializer(  entry )
            serializer( self.entry_key, entry )
            
        self._logger.endElementNS( ( None, key ), key )

    def dumpEntry( self, key, value ):
        key = unicode( key )
        type_code = self.getTypeCode( value )
        attrs = AttributesNSImpl( { (None, u'type' ) : type_code },
                                  { (None, u'type' ) : u'type' } )
        self._logger.startElementNS( ( None, key ), key, attrs )
        serializer = self.getAttrSerializer( value )
        self._logger.characters( serializer( value ) )
        self._logger.endElementNS( ( None, key ), key )

    def convertValue( self, value ):
        return unicode( value )

    def convertBoolean( self, value ):
        return unicode( value )

    def convertInteger( self, value ):
        return unicode( value )

    def convertDateTime( self, value ):
        return unicode( self, value )



if __name__ == '__main__':
   
   d = {'identification':{'filters':[ { 'attributes': {'id':'no_members', 'expr':'python: not 1'}} ] },
        'bd':True,
        'ef':"ste",
        'xy':[1,2,3,4],
        "ze":{'fa':1,
              'ze':['a','b']}
        }

   from pprint import pprint
   from StringIO import StringIO
   from xml.dom.minidom import parseString
   
   stream = StringIO()
   serializer = ExportSerializer( stream, "utf-8")
   serializer.dumpDictionary('identification', d )
   serializer.close()

   xstr =  stream.getvalue()
   mdom = parseString( xstr )

   print mdom.toprettyxml()
   
   parser = make_parser()
   reader = ImportReader()
   parser.setContentHandler(reader)

   stream = StringIO( xstr )
   parser.parse( stream )
   data = reader.getData()
   pprint(data)


    
