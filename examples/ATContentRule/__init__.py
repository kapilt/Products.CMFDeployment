"""
$Id: $
"""

from Products.Archetypes import public as atapi
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.DeploymentInterfaces import IContentRule

from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile, InitializeClass

xml_export_template = """
<mime id="%(id)s"
      product="%(product)s"
      factory="%(factory)s" />
"""

def addArchetypeContentRule(self,
                            id,
                            RESPONSE = None
                            ):
    """
    add an archetype rule
    """
    atrule = ArchetypeContentRule(id)
    self._setObject(atrule)
    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')
    
addArchetypeContentRuleForm = DTMLFile('ui/ArchtypesContentRuleAddForm', globals())

class ArchetypeContentRule(SimpleItem):

    meta_type = "Archetype Content Rule"
    
    __implements__ = IContentRule

    security = ClassSecurityInfo()

    def isValid(self, context):

        if isinstance( context, atapi.BaseContent ):
            return True

    def process(self, descriptor, context):
        content = descriptor.getContent()
        resource_descriptors = self.getSchemaResources()
        for rd in resource_descriptors:
            descriptor.addChildDescriptor( rd )
        descriptor.setRenderMethod('view')
        return descriptor

    def getSchemaResources( self, content):
        schema = content.Schema()
        content_path = content.absolute_url(1)
        for field in schema.filterFields():
            if isinstance( field, (field.ImageField, field.FileField)):
                value = field.get( instance )
            else:
                continue
            if value is None:
                continue
            descriptor = DescriptorFactory( value )
            descriptor.setRenderMethod('')

    def toXml(self):
        d = {'id':self.id,
             'product':'ATContentRule',
             'factory':'addArchetypeContentRule' }             
        return xml_export_template%d
    

InitializeClass(ArchetypeContentRule)

def initialize(context):

    context.registerClass(
        ArchetypeContentRule,
        permission = 'Add Content Rule',
        constructors = ( addArchetypeContentRuleForm,
                         addArchetypeContentRule )
        visibility = None
        )
        
