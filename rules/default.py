"""
$Id$
"""

from Products.CMFCore.Expression import Expression
from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentRule

addContentRuleForm = DTMLFile('ui/MimeExtensionMappingAddForm', globals())

def addContentRule(self, id, extension_expression, condition, view_method, ghost=0, RESPONSE=None):
    """ """
    mapping = MimeExtensionMapping(id=id,
                                   extension_expression=extension_expression,
                                   condition=condition,
                                   view_method=view_method,
                                   ghost=ghost)

    self._setObject(id, mapping)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_main')

xml_export_template = """
<mime id="%(id)s"
      product="%(product)s"
      factory="%(factory)s"
      filter_expr="%(filter_expr)s"
      ext_expr="%(ext_expr)s"
      view_method="%(view_method)s" />
"""


class MimeExtensionMapping(SimpleItem):

    meta_type = 'Mime Extension Mapping'

    view_method = ''

    __implements__ = (IContentRule,)

    manage_options = (
        {'label':'Mapping',
         'action':'editMappingForm'},
        {'label':'All Mappings',
         'action':'../manage_main'},
        {'label':'Mastering',
         'action':'../../overview'}
        )
    
    editMappingForm = DTMLFile('ui/MimeExtensionMappingEditForm', globals())

    def __init__(self, id, extension_expression, condition, view_method, ghost):
        self.id = id
        self.extension = Expression(extension_expression)
        self.extension_text = extension_expression
        self.condition = Expression(condition)
        self.condition_text = condition
        self.view_method = view_method.strip()
        self.ghost = ghost
        self.title = condition
        
    def isValid(self, descriptor, context):
        return not not self.condition(context)

    def getExtension(self, context):
        """
        get the extension if any for the content
        """
        return self.extension(context)

    def process(self, descriptor, context):
        """
        process a content descriptor, applying the rules specified by
        this deployment rule. 
        """
        extension = self.getExtension( context )
        descriptor.setExtension( extension )
        if self.ghost:
            descriptor.setGhost( True )
            descriptor.setRenderMethod( None ) # xxx redundant
        descriptor.setRenderMethod( self.view_method )
        return descriptor

    def editMapping(self, extension_expression, condition, view_method, ghost=0, RESPONSE=None):
        """ """
        self.extension = Expression(extension_expression)
        self.extension_text = extension_expression
        self.condition = Expression(condition)
        self.condition_text = condition
        self.view_method = view_method.strip()
        self.ghost = not not ghost
        self.title= condition

        if RESPONSE is not None:
            RESPONSE.redirect('../manage_main')


    #################################
    def toXml(self):

        d = { 'id':self.id,
              'view_method':self.view_method,
              'ext_expr':self.extension_text,
              'filter_expr':self.condition_text,
              'product':'CMFDeployment',
              'factory':'addMimeMapping' }
             
        return xml_export_template%d
             
    
