"""
Purpose: Unittests for testing the strategy of the policy
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 11/22/2005
$Id: $
"""
import os, sys

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
from Products.ZCatalog import ZCatalog, Vocabulary
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex, PLexicon
from Products.ZCTextIndex.Lexicon import Splitter
from Products.ZCTextIndex.Lexicon import CaseNormalizer, StopWordRemover
from Products.PluginIndexes.TextIndex.TextIndex import TextIndex
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog import ZCatalog
from Products.CMFDeployment import pipeline
from Products.CMFDeployment import dependencies
from Products.CMFDeployment import ContentMap
from Products.CMFDeployment.Descriptor import DescriptorFactory


class TestDefaultStrategy(PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner()
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('ATContentRule')
        installer.installProduct('CMFDeployment')
        
        policy_file = os.path.join(DeploymentProductHome,'examples','policies', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        self.policy = deployment_tool.getPolicy('plone_example')
        self.catalog_tool = getToolByName(self.portal, "portal_catalog")  
        
        self.portal.invokeFactory('Folder', 'folderwithindex')
        self.folderwithindex = self.portal.folderwithindex
        
   ##################################     
   # def testSetStrategy(self): 
   #     #################################
   #     #We check if the strategy is really the DefaultPolicyStrategy
   #     strategy = self.policy.getDeploymentStrategy()
   #     strategy.setStrategy('defaultpolicypipeline') 
   #     result= strategy.strategy_id     
   #     self.assertEqual(result, 'defaultpolicypipeline', "Strategy should be defaultpolicypipeline")
        
    #################################
    def testDefaultStrategyExecution(self):
        #################################
        #Set the strategy
        strategy = self.policy.getDeploymentStrategy()
        strategy.setStrategy('defaultpolicypipeline')
        
        #################################
        #Creates the ContentMap and add it to the policy
        resolver= self.policy.getDeploymentURIs()
        one_map= ContentMap.ContentMap(resolver) 
        self.policy._setOb('ContentMap', one_map)
        
        #################################
        #Creates the dependencySource and add it to the policy
        id_dep= "pouetDepSource"
        title_dep= "The Dependency Source"
        dependency_source= dependencies.DependencySource(id_dep, title_dep)
        sources= self.policy.getContentSources()
        sources._setOb('dependency_source', dependency_source)
        
        #################################
        #Creates the Deletion Source and add it to the policy
        deletion_source= incremental.DeletionSource("pouetDeletion")
        sources._setOb('deletion_source', deletion_source)  
        deleted_records= deletion_source._records   
        
        #################################
        #Execute the policy (Deploy the content)
        self.policy.execute()
        
        #################################
        #Add an index and its name
        extra= self.policy.getId()
        self.catalog_tool.manage_addIndex('plone_example_incremental_idx', 'PolicyIncrementalIndex', extra)
        self.catalog_tool.manage_addColumn('plone_example_incremental_idx')
        #Index an object with the new index plone_example_incremental_idx
        self.catalog_tool.indexObject(self.portal.folderwithindex, ['plone_example_incremental_idx'])
        
        ################################
        #Create the Policy Pipeline
        policy_id= self.policy.getId()
        catalog = self.catalog_tool
        a_dependency_manager= dependencies.DependencyManager("PouetDepManager", policy_id, catalog)
        new_steps= (pipeline.PipeEnvironmentInitializer(),
                    pipeline.ContentSource(),
                    pipeline.ContentPreparation(),
                    pipeline.DirectoryViewDeploy(),
                    pipeline.ContentProcessPipe(),
                    pipeline.ContentTransport(),
                    a_dependency_manager
                    )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.PolicyPipeline()
        new_pipeline.steps= new_steps  
        new_pipeline.process(self.policy)
        
        #Unindex the object
        self.catalog_tool.unindexObject(self.portal.folderwithindex)  
        
        #################################
        #taking the content that has been deleted in deletion source
        sources= new_pipeline.services['ContentIdentification'].sources
        deletion_source = sources._getOb('deletion_source', None)
        deleted_records= deletion_source.getContent()
        
        #take the reverse dependencies of the deleted_records
        #no need to clean the deletion source and the dep. source
        #one_map.pprint()
        try:
            while (True):
                record = deleted_records.next()
                #print "\ntest pouet: record: ", record.descriptor.getContent()
                a_dependency_manager.processRemoval(record)
        except:         
            #check if dependency source and deletion source are empty
            deleted_records= deletion_source._records
            self.assertEqual(deleted_records, [], 'Deletion source should be empty')
            
            dependency_source = sources._getOb('dependency_source', None)
            dependencies_source= dependency_source._queue
            self.assertEqual(dependencies_source, [], 'Dependency Source should be empty') 
    
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDefaultStrategy))
    return suite

if __name__ == '__main__':
    unittest.main()
