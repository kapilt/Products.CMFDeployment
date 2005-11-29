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
from Products.CMFDeployment import pipeline
from Products.CMFDeployment import ContentMap
from Products.CMFDeployment.tests.testDeployment import setupContentTree

class MyPipeline(PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner() #Use if you need to manipulate the portal object itself.
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
        
        #################################
        #Add the ContentMap to the policy
        resolver= self.policy.getDeploymentURIs()
        one_map= ContentMap.ContentMap(resolver) 
        self.policy._setOb('ContentMap', one_map) 
        
    def testCreatePipeline(self):
        new_steps= (pipeline.PipeEnvironmentInitializer(), #OK pipeline
                    pipeline.ContentSource(), #OK
                    pipeline.ContentPreparation(), #OK pipesegment l.146 match
                    pipeline.DirectoryViewDeploy(), #OK pipesegment
                    pipeline.ContentProcessPipe(), #OK pipesegment
                    pipeline.ContentTransport() #OK pipesegment 
                    )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.Pipeline()
        new_pipeline.steps= new_steps
        #Try to process each step     
        new_pipeline.process(self.policy)
        
    def testCreatePolicyPipeline(self):
        new_steps= (pipeline.PipeEnvironmentInitializer(), #OK pipeline
                    pipeline.ContentSource(), #OK
                    pipeline.ContentPreparation(), #OK pipesegment l.146 match
                    pipeline.DirectoryViewDeploy(), #OK pipesegment
                    pipeline.ContentProcessPipe(), #OK pipesegment
                    pipeline.ContentTransport() #OK pipesegment 
                    )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.PolicyPipeline()
        new_pipeline.steps= new_steps
        #Try to process each step     
        new_pipeline.process(self.policy)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite= unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MyPipeline))
        return suite    
