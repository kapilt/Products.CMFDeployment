
from Products.CMFDeployment.DeploymentInterfaces import IContentRule
from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile, InitializeClass

def addArchetypeContentRule(self,
                            id,
                            RESPONSE = None
                            ):
    """
    """

addArchetypeContentRuleForm = DTMLFile('ui/ArchtypesContentRuleAddForm', globals())

class ArchetypesContentRule(SimpleItem):

    meta_type = "Archetypes Content Rule"
    
    __implements__ = IContentRule

    security = ClassSecurityInfo()

    def isValid(self, context):
        return True

    def process(self, descriptor, context):
        return True

    def toXml(self):
        return ''
    

InitializeClass(ArchetypesContentRule)

def initialize(context):

    context.registerClass(
        ArchetypesContentRule,
        permission = 'Add Content Rule',
        constructors = ( addArchetypeContentRuleForm,
                         addArchetypeContentRule )
        visibility = None
        )
        
