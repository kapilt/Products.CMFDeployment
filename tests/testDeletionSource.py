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
from Products.CMFDeployment import pipeline
from Products.CMFDeployment import ContentMap


class TestDeletionSource(PloneTestCase):
    
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
        
        
    def testDeletionSource(self):
        #################################
        #Add the ContentMap to the policy
        resolver= self.policy.getDeploymentURIs()
        one_map= ContentMap.ContentMap(resolver) 
        self.policy._setOb('ContentMap', one_map)
        
        #################################
        #Creates the Deletion Source and add it to the policy
        sources= self.policy.getContentSources()
        deletion_source= incremental.DeletionSource("pouetDeletion")
        sources._setOb('deletion_source', deletion_source)  
        deleted_records= deletion_source._records
        
        #################################
        #Create the Policy Pipeline first
        new_steps= (pipeline.PipeEnvironmentInitializer(), #OK pipeline
                    pipeline.ContentSource(), #OK
                    pipeline.ContentPreparation(), #OK pipesegment
                    pipeline.DirectoryViewDeploy(), #OK pipesegment
                    pipeline.ContentProcessPipe(), #OK pipesegment
                    pipeline.ContentTransport() #OK pipesegment 
                    )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.PolicyPipeline()
        new_pipeline.steps= new_steps
        #Try to process each step     
        new_pipeline.process(self.policy)
    
        #################################
        #Add an index and its name
        extra= self.policy.getId()
        self.catalog_tool.manage_addIndex('plone_example_incremental_idx', 'PolicyIncrementalIndex', extra) 
        self.catalog_tool.manage_addColumn('plone_example_incremental_idx')
        #Index an object with the new index plone_example_incremental_idx
        self.catalog_tool.indexObject(self.folderwithindex, ['plone_example_incremental_idx'])   
        #Unindex the object
        self.catalog_tool.unindexObject(self.folderwithindex)  
        
        #################################
        #checking if content deleted is in deletion source
        sources= new_pipeline.services['ContentIdentification'].sources
        deletion_source = sources._getOb('deletion_source', None) 
        result= deletion_source.getContent()   
        result_id= result.next().descriptor.getId()
        self.assertEqual('folderwithindex', result_id, 'Deletion Record should be folderwithindex instance')
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDeletionSource))
    return suite

if __name__ == '__main__':
    unittest.main()
