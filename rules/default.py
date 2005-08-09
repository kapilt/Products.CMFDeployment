"""
$Id$
"""

from Products.CMFCore.Expression import Expression
from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentRule

addContentRuleForm = DTMLFile('../ui/MimeExtensionMappingAddForm', globals())

def addContentRule(self, id, extension_expression, condition, view_method, ghost=0, RESPONSE=None):
    """ add content rule """
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

class BaseRule( SimpleItem ):

    meta_type = "Base Rule"

def addChildView(self, id, extension_expression, view_method, binary=False, RESPONSE=None):
    """
    add child view
    """
    cview = ChildView( id )
    self._setObject( id, cview)
    cview.edit( extension_expression, view_method, binary )
    
    if RESPONSE is not None:
        RESPONSE.redirect('manage_main')
    
class ChildView( BaseRule ):

    meta_type = "Child View Rule"

    settings_form = DTMLFile('../ui/ChildViewRuleEditForm', globals())

    manage_options = (
        {'label':'Settings',
         'action':'settings_form'},
        ) + BaseRule.manage_options

    def __init__(self, id, extension_expression=''):
        self.id = id
        self.extension = Expression(extension_expression)
        self.extension_text = extension_expression
        self.view_method = ''
        self.binary = False

    def edit(self,  extension_text, view_method, binary):
        self.extension_text = extension_text
        self.extension = Expression( extension_text )
        self.view_method = view_method
        self.binary = not not binary

    def process( self, descriptor, expr_context):
        extension = self.extension( expr_context )
        descriptor.setExtension( extension )
        if self.binary:
            descriptor.setBinary( binary )
        descriptor.setRenderMethod( self.view_method )
    
InitializeClass( ChildView )
    
class MimeExtensionMapping( OrderedFolder, BaseRule ):

    meta_type = 'Mime Extension Mapping'

    view_method = ''

    __implements__ = (IContentRule,)

    manage_options = (
        {'label':'Mapping',
         'action':'editMappingForm'},
        {'label':'Child Views',
         'action':'manage_main'},
        ) + App.Undo.UndoSupport.manage_options
    
    editMappingForm = DTMLFile('../ui/MimeExtensionMappingEditForm', globals())

    addChildViewForm = DTMLFile('../ui/ChildViewRuleAddForm', globals())

    all_meta_types = (
        {'name':ChildView.meta_type,
         'action':'addChildViewForm'},
        )

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

    def getChildDescriptors( self, descriptor, expr_context ):

        if not len( self.objectIds()  ):
            raise StopIteration

        factory = DescriptorFactory( self.getDeploymentPolicy() )
        content = descriptor.getContent()

        for cview in self.objectValues( ChildView.meta_type ):
            descriptor = factory( content )
            cview.process( descriptor, expr_context)
            yield descriptor

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

        for cdesc in self.getChildDescriptors( descriptor, context ):
            descriptor.addChildDescriptor( cdesc )
            
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
            RESPONSE.redirect('manage_workspace')

    #################################
    def addChildView(self, id, extension_expression, view_method, binary=False, RESPONSE=None):
        """
        add child view
        """
        return addChildView( self, id, extension_expression,
                             view_method, binary, RESPONSE)

    #################################
    def toXml(self):

        d = { 'id':self.id,
              'view_method':self.view_method,
              'ext_expr':self.extension_text,
              'filter_expr':self.condition_text,
              'product':'CMFDeployment',
              'factory':'addMimeMapping' }
             
        return xml_export_template%d
             

    
