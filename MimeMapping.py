##################################################################
#
# (C) Copyright 2002-2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
# All Rights Reserved
#
# This file is part of CMFDeployment.
#
# CMFDeployment is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CMFDeployment is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CMFDeployment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
Purpose: Mime Mappings are used to map extensions onto content objects
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
License: GPL
Created: 8/10/2002
$Id: $
"""

from OFS.ObjectManager import IFAwareObjectManager

from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import SecureModuleImporter, getEngine

from Namespace import *
from ExpressionContainer import ExpressionContainer
from DeploymentInterfaces import IContentRule

addMappingForm = DTMLFile('ui/MimeExtensionMappingAddForm', globals())

def addMimeMapping(self, id, extension_expression, condition, view_method, ghost=0, RESPONSE=None):
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
             
    

class MimeMappingContainer(ExpressionContainer, IFAwareObjectManager):

    meta_type = 'Mime Mapping Container'

    manage_options = (
        {'label':'Mappings',
         'action':'manage_main'},

        {'label':'Mastering',
         'action':'../overview'},        

        {'label':'Policy',
         'action':'../../overview'}
        )

    all_meta_types = IFAwareObjectManager.all_meta_types
    _product_interfaces = ( IContentRule, )
    
    def __init__(self, id, title=''):
        self.id = id
        self.title = title or id
        
    def addMimeMapping(self, *args, **kw):
        return self.manage_addProduct['CMFDeployment'].addMimeMapping(*args, **kw)

def getMimeExprContext(object, portal):
    
    data = {
        'object':       object,
        'portal':       portal,
        'nothing':      None,
        'request':      getattr( object, 'REQUEST', None ),
        'modules':      SecureModuleImporter,
        'deploy':       DeploymentMimeUtilities.__of__(object)
        }

    return getEngine().getContext(data)    
    
class MimeUtilities(Implicit):

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    
    __allow_access_to_unprotected_subobjects__ = 1

    def has_index(self, obj):
        return not not getattr(aq_base(obj), 'index_html', None)
    
InitializeClass(MimeUtilities)
DeploymentMimeUtilities = MimeUtilities()

#def registerMimeContextMethod(name, context_method):#
#
#    assert isinstance(name, str)
#    assert not _MimeUtilities.__dict__.has_key(name),"duplicate registration %s"%name           
#    _MimeUtilities.__dict__[name]=context_method
    
