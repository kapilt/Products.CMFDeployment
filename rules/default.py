"""
$Id$
"""

from Products.CMFCore.Expression import Expression
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import PortalFolder

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

class RuleConfigurator( object ):

    def importRule(self, ctx, **kw):
        md = {}
        md['extension_expression'] = kw.get('ext_expr', '')
        md['condition'] = kw.get('filter_expr', '')
        md['view_method'] = kw.get('view_method', '')
        md['ghost'] = kw.get('ghost', '')
        md['id'] = kw.get('id', '')

        return addContentRule( ctx, **md )

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
        descriptor.setFileName( extension )
        if self.binary:
            descriptor.setBinary( binary )

        # The view method needs to be an expresison now
        if self.view_method:
            vm = Expression(self.view_method)
            vm = vm( expr_context )
        else:
            vm = ""
        
        descriptor.setRenderMethod( vm )
    
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
        
    def isValid(self, content, context):
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

    def getDependencies( self, descriptor, context ):
        """
        get the to be deployed content's dependencies
        """
        return ()

    def getReverseDependencies( self, descriptor, context ):
        """
        get the objects which in turn depend on this object for them
        to be deployed, processed when content is about to be
        deleted.
        """
        content = descriptor.getContent()
	parent = content.aq_inner.aq_parent
            
        
        if not isinstance( parent, (PortalContent, PortalFolder) ):
           return ()
        rdeps = [parent,]

        try: # archetypes reference support ( like plone2.1 related items)
            schema = content.Schema()
            rdeps.extend( content.getBRefs() )
        except AttributeError:
            pass
        
        return rdeps

    def process(self, descriptor, context):
        """
        process a content descriptor, applying the rules specified by
        this deployment rule. 
        """
        extension = self.getExtension( context )
        descriptor.setFileName( extension )
        if self.ghost:
            descriptor.setGhost( True )
            descriptor.setRenderMethod( None ) # xxx redundant
            
        # The view method needs to be an expresison now
        if self.view_method:
            vm = Expression(self.view_method)
            vm = vm( context )
        else:
            vm = ""       
        descriptor.setRenderMethod( vm )
    
        for cdesc in self.getChildDescriptors( descriptor, context ):
            descriptor.addChildDescriptor( cdesc )

        dependencies = self.getDependencies( descriptor, context )
        descriptor.setDependencies( dependencies )

        reverse_dependencies = self.getReverseDependencies( descriptor, context )
        descriptor.setReverseDependencies( reverse_dependencies )

        descriptor.rule_id = self.getId()
        
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

    edit = editMapping

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
             

    
