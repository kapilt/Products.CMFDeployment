"""
XXX todo - make all handling of child descriptors utilize an accessor that gets nested
           descriptors.
$Id$
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.DeploymentInterfaces import IContentRule
from Products.CMFDeployment import utils

from atcontent import ArchetypeContentRule

def addATCompositeRule(self, id, extension_expression, condition, view_method, ghost=0, aliases=(), RESPONSE=None):
    """
    add an archetype rule
    """
    atrule = ATCompositeRule(id,
                             extension_expression=extension_expression,
                             condition=condition,
                             view_method=view_method,
                             ghost=ghost,
                             aliases=aliases)

    self._setObject(id, atrule)
    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')
    
addATCompositeRuleForm = DTMLFile('../ui/ContentRuleATCompositeAddForm', globals())

class ATCompositeRule( ArchetypeContentRule ):

    meta_type = "AT Composite Rule"
    xml_factory = "addATCompositeRule"

    def process(self, descriptor, context):

        descriptor = ArchetypeContentRule.process( self, descriptor, context )
        factory = DescriptorFactory( self.getDeploymentPolicy() )
        mastering = self.getContentMastering()

        for child in descriptor.getContent().contentValues():
             cdescriptor = factory( child )
             if mastering.prepare( cdescriptor ):
                 cdescriptor.setFileName( utils.guess_filename( cdescriptor.getContent() ) )
                 descriptor.addChildDescriptor( cdescriptor )

    def getXReverseDependencies( self, descriptor, context ):

        dependencies = ArchetypeContentRule.getReverseDependencies( self, descriptor, context )
        # for composite content, we explicitly redeploy contained objects
        # only because some composite implementations don't index contained objects
        dependencies.extend( descriptor.getContent().contentValues() )
        return dependencies
    
InitializeClass(ATCompositeRule)
