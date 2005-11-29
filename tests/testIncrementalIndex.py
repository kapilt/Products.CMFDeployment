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

class MyIncremental(SecurityRequestTest):
    
    def setUp(self):
        SecurityRequestTest.setUp(self)
        
        catalog = ZCatalog.ZCatalog('portal_catalog')
        self.root._setObject('portal_catalog', catalog)
        self.cat = ct = self.root.portal_catalog
        self.cmf = self.cat.manage_addProduct['CMFDeployment']
        zc = ct.manage_addProduct['ZCatalog']
        zc.manage_addVocabulary('Vocabulary',
                                'test vocabulary',
                                globbing=1 )
        ct._setObject('lexicon',
                      PLexicon('lexicon', '',
                               Splitter(),
                               CaseNormalizer(),
                               StopWordRemover())
                      )
        
    def testPolicyIncremental(self):
        #Creating an Index OK
        self.cmf.manage_addPolicyIncrementalIndex(
                                     'searchable_text', #id
                                     idx_type = TextIndex.meta_type,
                                     value_expr = 'object/SearchableText'
                                     )
        
        #Get plugin indexes OK
        plugin_indexes= self.cmf.getIndexTypes() #returns a list of plugin indexes
        self.assertEqual(len(plugin_indexes), 9, ('index types query should have found 9 objects'))  
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MyIncremental))
    return suite

if __name__ == '__main__':
    unittest.main()
