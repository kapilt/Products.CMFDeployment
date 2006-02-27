
import inspect, sys
from OFS.SimpleItem import SimpleItem

source_template = """\
 <source id="%(id)s"
         title="%(title)s"
         product="%(product)s"
         factory="%(factory)s" />
"""         

class BaseSource(SimpleItem):

    meta_type = 'Base Source'
    xml_template = source_template
    xml_factory  = ""

    def toXml(self):
        data = self.getInfoForXml()
        if data is None:
            return ''
        return self.xml_template%( data )
    
    def getInfoForXml(self):
        """
        get a dictionary of info for xml formatting
        """
        
        # do a basic xml export for stateless sources
        
        # stateful sources should override
        module = inspect.getmodule( self.__class__ )
        parts = module.__name__.split('.')
        
        if 'Products' not in parts:
            return

        idx = parts.index('Products')
        product = ".".join(parts[idx+1:idx+2])
        
        d = { 'id': self.id,
              'title': self.title_or_id(),
              'product': product,
              'factory': self.xml_factory }

        return d
