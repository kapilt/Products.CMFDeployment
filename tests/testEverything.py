"""
Purpose: Unittests for testing incremental, pipeline and dependencies
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 11/16/2005
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

from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment import incremental
from Products.CMFDeployment import pipeline
from Products.CMFDeployment import dependencies
from Products.CMFDeployment import ContentMap

class TestEverything (PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner()
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('ATContentRule')
        installer.installProduct('CMFDeployment')
        
        self.portal.invokeFactory('Folder', 'folderwithindex')
        self.folderwithindex = self.portal.folderwithindex
        
        self.folderwithindex.invokeFactory('Document', 'docwithindex')
        self.docwithindex = self.folderwithindex.docwithindex
        
        policy_file = os.path.join(DeploymentProductHome,'examples','policies', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        self.policy = deployment_tool.getPolicy('plone_example')
        #setupContentTree(self.portal)
        self.catalog_tool = getToolByName(self.portal, "portal_catalog")    
        
    def testEverything(self): 
        #################################
        #Add the ContentMap to the policy
        one_map= ContentMap.ContentMap() 
        self.policy._setOb('ContentMap', one_map)      
     
        #################################
        #Creates the dependencySource and add it to the policy
        id_dep= "pouetDepSource"
        title_dep= "The Dependency Source"
        dependency_source= dependencies.DependencySource(id_dep, title_dep)
        sources= self.policy.getContentSources()
        sources._setOb('dependency_source', dependency_source)
    
        #################################
        #Add an index and its name
        extra= self.policy.getId()
        self.catalog_tool.manage_addIndex('plone_example_incremental_idx', 'PolicyIncrementalIndex', extra)
        self.catalog_tool.manage_addColumn('plone_example_incremental_idx')
        #Index an object with the new index plone_example_incremental_idx
        self.catalog_tool.indexObject(self.folderwithindex, ['plone_example_incremental_idx']) 
    
        ################################
        #Create the Policy Pipeline
        policy_id= self.policy.getId()
        new_steps= (pipeline.PipeEnvironmentInitializer(),
                    pipeline.ContentSource(),
                    pipeline.ContentPreparation(),
                    pipeline.DirectoryViewDeploy(),
                    pipeline.ContentProcessPipe(),
                    pipeline.ContentTransport(),
                    dependencies.DependencyManager("PouetDepManager", policy_id)
                    )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.PolicyPipeline()
        new_pipeline.steps= new_steps  
        new_pipeline.process(self.policy)  
        
        #################################
        #Adding the deletion source to the contentIdentification
        #create a new deletion source
        sources= new_pipeline.services['ContentIdentification'].sources
        deletion_source= incremental.DeletionSource("pouetDeletion")
        sources._setOb('deletion_source', deletion_source)
        
        #result      
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEverything))
    return suite

if __name__ == '__main__':
    unittest.main()
