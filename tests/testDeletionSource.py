"""
Purpose: Unittests for testing incremental.py
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 10/28/2005
$Id: $
"""
import os, sys, time, shutil

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('CMFDeployment')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('ATContentRule')

from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment.DeploymentPolicy import DeploymentPolicy
from Products.CMFDeployment.ExpressionContainer import getDeployExprContext
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import incremental
from Products.CMFDeployment.tests.testDeployment import setupContentTree
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog import ZCatalog
from Products.CMFDeployment import pipeline
from Products.CMFDeployment import ContentMap

TESTDEPLOYDIR = os.path.join( DeploymentProductHome, 'tests', 'deploy')

# these two settings operate together
LEAVE_DEPLOY_DIR=True
CLEAN_DEPLOY_DIR=True


class TestDeletionSource(PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner()
        
        if os.path.exists( TESTDEPLOYDIR ) and CLEAN_DEPLOY_DIR:
            shutil.rmtree( TESTDEPLOYDIR )
        
        if not os.path.exists( TESTDEPLOYDIR ):
            os.mkdir( TESTDEPLOYDIR )
        
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('ATContentRule')
        installer.installProduct('CMFDeployment')
        
        self.portal.invokeFactory('Folder', 'folderwithindex')
        self.folderwithindex = self.portal.folderwithindex
        
        policy_file = os.path.join(DeploymentProductHome,'examples','policies', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        self.policy = deployment_tool.getPolicy('plone_example')
        setupContentTree(self.portal)
        self.catalog_tool = getToolByName(self.portal, "portal_catalog")    
        
        structure = self.policy.getContentOrganization().getActiveStructure()
        structure.mount_point = TESTDEPLOYDIR
        
        get_transaction().commit(1)
        
    def testDeletionSource(self):
        self.policy.execute()
        #Delete the object
        self.portal.manage_delObjects(["about"]) 
        
        #################################
        #checking if content deleted is in deletion source
        deletion_source = self.policy.getDeletionSource()
        result= deletion_source.getContent()
        tab= []
        try:
            while True: 
                result_id= result.next().descriptor.getId()
                tab.append(result_id)
        except StopIteration:
            self.assertEqual(tab, ['index_html', 'contact', 'about'], 'Deletion Record should be about instance')
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDeletionSource))
    return suite

if __name__ == '__main__':
    unittest.main()
