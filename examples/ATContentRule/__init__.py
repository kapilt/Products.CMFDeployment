##################################################################
#
# (C) Copyright 2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
$Id: $
"""

from Products.Archetypes import public as atapi
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.DeploymentInterfaces import IContentRule

from AccessControl import ClassSecurityInfo
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
    self._setObject(id, atrule)
    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')
    
addArchetypeContentRuleForm = DTMLFile('ui/ArchetypeContentRuleAddForm', globals())

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
                         addArchetypeContentRule ),
        visibility = None
        )
        
