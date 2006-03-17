"""
$Id$
"""

from Products.CMFCore.Expression import Expression
from Products.CMFCore.PortalContent import PortalContent

try: # in plone 2.1
    from Products.CMFCore.PortalFolder import PortalFolderBase
except: # 2.0
    from Products.CMFCore.PortalFolder import PortalFolder as PortalFolderBase

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.DeploymentInterfaces import IContentRule
from Products.CMFDeployment.utils import SerializablePlugin

addContentRuleForm = DTMLFile('../ui/MimeExtensionMappingAddForm', globals())

def addContentRule(self, id, extension_expression, condition, view_method, ghost=0, aliases=(), RESPONSE=None):
    """ add content rule """

    mapping = ContentRule(id=id,
                          extension_expression=extension_expression,
                          condition=condition,
                          view_method=view_method,
                          ghost=ghost,
                          aliases=aliases)

    self._setObject(id, mapping)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_main')


xml_export_template = """
<rule id="%(id)s"
      product="%(product)s"
      factory="%(factory)s"
      condition="%(condition)s"
      ext_expr="%(filename)s"
      view_method="%(view_method)s" />
"""


class BaseRule( SerializablePlugin ):

    meta_type = "Base Rule"

    icon_path = "linkTransparent.gif"

    # zmi icon
    def icon(self):
        return getToolByName(self, 'portal_url')(relative=1)+'/'+self.icon_path


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

    def edit(self,  extension_expression, view_method, RESPONSE=None):
        """
        edit the child view
        """
        self.extension_text = extension_expression
        self.extension = Expression( extension_expression )
        self.view_method = view_method
        #self.binary = not not binary
        
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

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
    
class ContentRule( OrderedFolder, BaseRule ):

    meta_type = 'Content Rule'

    xml_template = xml_export_template
    xml_factory  = "addContentRule"
    
    view_method = ''

    __implements__ = (IContentRule,)

    manage_options = (
        {'label':'Mapping',
         'action':'editMappingForm'},
#        {'label':'Child Views',
#         'action':'manage_main'},
        ) + App.Undo.UndoSupport.manage_options
    
    editMappingForm = DTMLFile('../ui/MimeExtensionMappingEditForm', globals())

    addChildViewForm = DTMLFile('../ui/ChildViewRuleAddForm', globals())

    all_meta_types = (
        {'name':ChildView.meta_type,
         'action':'addChildViewForm'},
        )

    aliases = ()
    icon = BaseRule.icon

    def __init__(self, id, extension_expression, condition, view_method, ghost, aliases):
        self.id = id
        self.extension = Expression(extension_expression)
        self.extension_text = extension_expression
        self.condition = Expression(condition)
        self.condition_text = condition
        self.view_method = view_method.strip()
        self.ghost = ghost
        aliases = filter(None, [a.strip() for a in aliases ] )
        self.aliases = aliases
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
            
        
        if not isinstance( parent, (PortalContent, PortalFolderBase) ):
           return []
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
        
        if self.aliases:
            descriptor.aliases = self.aliases
    
        for cdesc in self.getChildDescriptors( descriptor, context ):
            descriptor.addChildDescriptor( cdesc )

        reverse_dependencies = self.getReverseDependencies( descriptor, context )
        descriptor.setReverseDependencies( reverse_dependencies )

        descriptor.rule_id = self.getId()
        
        return descriptor

    def editMapping(self, extension_expression, condition, view_method, ghost=0, aliases=(), RESPONSE=None):
        """ """
        self.extension = Expression(extension_expression)
        self.extension_text = extension_expression
        self.condition = Expression(condition)
        self.condition_text = condition
        self.view_method = view_method.strip()
        self.ghost = not not ghost
        self.title= condition
        aliases = filter(None, [a.strip() for a in aliases ] )
        self.aliases =  aliases or ()

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
    def getInfoForXml(self):
        d = BaseRule.getInfoForXml(self)
        del d['attributes']['title']
        d.update( { 'view_method':self.view_method,
                    'filename':self.extension_text,
                    'aliases': list( self.aliases ),
                    'condition':self.condition_text } )
        return d
             

    
