
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment import DeploymentTool
from Products.CMFCore.DirectoryView import addDirectoryViews


def install(self):
    out = StringIO()
    skinstool = getToolByName(self, 'portal_skins')

    ob = DeploymentTool.DeploymentTool()
    self._setObject(ob.getId(), ob)

    if 'deployment_templates' not in skinstool.objectIds():
        addDirectoryViews(skinstool, 'skins', DeploymentProductHome)
        out.write("Added 'deployment_templates' directory view to portal_skins\n")

    skins = skinstool.getSkinSelections()
    if 'Plone Deployment' not in skins:
        path=[elem.strip() for elem in \
              skinstool.getSkinPath('Plone Default').split(',')]
        path.insert(path.index('custom')+1, 'deployment_templates')
        skinstool.addSkinSelection('Plone Deployment', ','.join(path))
    else:
        out.write("Plone Deployment skin already setup\n")

    portal = self.portal_url.getPortalObject()
    portal.portal_catalog.indexObject( portal )

    return out.getvalue()
