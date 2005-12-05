"""
Purpose: Unittests for testing pipeline.py
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 10/25/2005
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
from Products.CMFDeployment.DeploymentPolicy import DeploymentPolicy
from Products.CMFDeployment.ExpressionContainer import getDeployExprContext
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import pipeline, ContentMap, dependencies
from Products.CMFDeployment.tests.testDeployment import setupContentTree

class MyPipeline(PloneTestCase):
    
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
        
        setupContentTree(self.portal)  
        
        catalog_tool = getToolByName(self.portal, "portal_catalog")  
        index= self.policy.getId() + '_incremental_idx'
        
    def testCreatePipeline(self):
        steps= (pipeline.PipeEnvironmentInitializer(),
                pipeline.ContentSource(),
                pipeline.ContentPreparation(),
                pipeline.DirectoryViewDeploy(),
                dependencies.DependencyManager(),
                pipeline.ContentProcessPipe(),
                pipeline.ContentDeletionPipeline(),
                pipeline.ContentTransport(),
                pipeline.ContentWatchEnd()
                )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.Pipeline()
        new_pipeline.steps= steps 
        new_pipeline.process(self.policy)
        
    def testCreatePolicyPipeline(self):
        steps= (pipeline.PipeEnvironmentInitializer(),
                pipeline.ContentSource(),
                pipeline.ContentPreparation(),
                pipeline.DirectoryViewDeploy(),
                dependencies.DependencyManager(),
                pipeline.ContentProcessPipe(),
                pipeline.ContentDeletionPipeline(),
                pipeline.ContentTransport(),
                pipeline.ContentWatchEnd()
                )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.PolicyPipeline()
        new_pipeline.steps= steps 
        new_pipeline.process(self.policy)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite= unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MyPipeline))
        return suite    
