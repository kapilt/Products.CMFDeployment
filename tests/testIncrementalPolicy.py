"""
Purpose: Unittests for testing incremental.py
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 10/28/2005
$Id: $
"""
import os, sys, time

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('CMFDeployment')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('ATContentRule')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('ZCTextIndex')

from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment.DeploymentPolicy import DeploymentPolicy
from Products.CMFDeployment.ExpressionContainer import getDeployExprContext
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import incremental
from Products.CMFDeployment.tests.testDeployment import setupContentTree
from Products.ZCatalog import ZCatalog, Vocabulary
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex, PLexicon
from Products.ZCTextIndex.Lexicon import Splitter
from Products.ZCTextIndex.Lexicon import CaseNormalizer, StopWordRemover
from Products.PluginIndexes.TextIndex.TextIndex import TextIndex
from Products.CMFDeployment.tests.testDeployment import setupContentTree
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog import ZCatalog


class MyIncrementalPolicy(PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner()
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
        
    def testIndexObject(self):         
        #Add an index and its name
        self.catalog_tool.manage_addIndex('plone_example_incremental_idx', 'PolicyIncrementalIndex')  
        self.catalog_tool.manage_addColumn('plone_example_incremental_idx')
          
        #Index an object with the new index plone_example_incremental_idx
        self.catalog_tool.indexObject(self.folderwithindex, ['plone_example_incremental_idx']) 

        uid= '/'.join( self.folderwithindex.getPhysicalPath() )
        result= self.catalog_tool.getIndexDataForUID(uid)
        self.assertEqual('plone_example_incremental_idx' in result, True, 'Plone Example Incremental should be in datas')
        
        
    def testGetIncrementalIndex(self):
        #Add an index and its name
        self.catalog_tool.manage_addIndex('plone_example_incremental_idx', 'PolicyIncrementalIndex') 
        self.catalog_tool.manage_addColumn('plone_example_incremental_idx')
           
        #Index an object with the new index plone_example_incremental_idx
        self.catalog_tool.indexObject(self.folderwithindex, ['plone_example_incremental_idx'])  

        catalog_index= incremental.getIncrementalIndexId(self.policy) # OK
        self.assertNotEqual(catalog_index, None, 'catalog index should be PolicyIncrementalIndex')                   
        
    def testDelIndex(self):
        #Add an index and its name
        self.catalog_tool.manage_addIndex('plone_example_incremental_idx', 'PolicyIncrementalIndex')  
        self.catalog_tool.manage_addColumn('plone_example_incremental_idx')
        
        #Index an object with the new index plone_example_incremental_idx
        self.catalog_tool.indexObject(self.folderwithindex, ['plone_example_incremental_idx']) 
        
        #Clear a/some index
        self.catalog_tool.manage_delIndex('plone_example_incremental_idx')
        
        indexes= self.catalog_tool.indexes()
        self.assertEqual('plone_example_incremental_idx' in indexes, False, 'Plone Example Incremental index shouldn\'t be in datas')
        
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MyIncrementalPolicy))
    return suite

if __name__ == '__main__':
    unittest.main()
