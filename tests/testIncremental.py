"""
Purpose: Unittests for testing incremental.py
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 10/28/2005
$Id$
"""
import os, sys, time, shutil

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from DateTime import DateTime

ZopeTestCase.installProduct('CMFDeployment')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('ATContentRule')

from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment import DefaultConfiguration
from Products.CMFDeployment.DeploymentPolicy import DeploymentPolicy
from Products.CMFDeployment.ExpressionContainer import getDeployExprContext
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import incremental
from Products.CMFDeployment.segments.core import PipeSegment

from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog import ZCatalog
from Products.CMFDeployment import pipeline

from testDeployment import setupContentTree

TESTDEPLOYDIR = os.path.join( DeploymentProductHome, 'tests', 'deploy')

# these two settings operate together
LEAVE_DEPLOY_DIR=True
CLEAN_DEPLOY_DIR=True


class TestIncrementalComponents(PloneTestCase):
    
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
        deletion_source = self.policy._getOb( DefaultConfiguration.DeletionSource, None )

        self.assertNotEqual( deletion_source, None, "Policy does not have a deletion source")

        result = list(  deletion_source.getContent() )

        expected = ['portal/about/index_html', 'portal/about/contact', 'portal/about']
        
        for content in result:
            assert content.content_url in expected, "unexpected deletion record"

        self.assertEqual( len( expected ), len( result ))


    def testDeletionPipeline(self):
        self.policy.execute()
        self.portal.manage_delObjects(["about"]) 
        self.policy.execute()
        about_idx = os.path.join( TESTDEPLOYDIR, 'about','index.html')
        assert not os.path.exists( about_idx )        

    def testContentModification(self):
        self.policy.execute()
        event_fs_path = os.path.join( TESTDEPLOYDIR, 'events', 'cignex_sprint.html')
        assert os.path.exists( event_fs_path )
        
        rule = self.policy.getContentMastering().mime.Event
        rule.edit( rule.extension_text,
                   "python: 'rabbit' in object.Description()",
                   rule.view_method )

        self.portal.events.cignex_sprint.reindexObject()
        self.policy.execute()
        
        assert not os.path.exists( event_fs_path ), "path still exists"

        rule.edit( rule.extension_text,
                   "python: 'Event' == object.portal_type",
                   rule.view_method )

        # interesting tidbit, this doesn't really work because of notifyModified
        # which auto sets modification date, but it works enough for the unit test
        # which just wants to set the mod date to some future point past the
        # the last deploy
        mod_time = DateTime()+3600.0/(60*60*24) # 1 hr into the future
        self.portal.events.cignex_sprint.setModificationDate( mod_time )
        self.portal.events.cignex_sprint.reindexObject(idxs=('modified',))
        
        self.policy.execute()
        assert os.path.exists( event_fs_path )        

    def testDependencySource(self):
        # some serious monkey patches...

        self.policy.execute()
        get_transaction().commit(1)
        import time; time.sleep(2)
        self.portal.about.index_html.edit('text/plain', 'hello world')
        self.portal.about.index_html.reindexObject()
        get_transaction().commit(1)
        
        class PipeObserver( PipeSegment ):

            def __init__(self):
                self.content = []

            def process( self, pipeline, descriptor ):
                self.content.append( descriptor )
                return descriptor
            
        observer = PipeObserver()
        
        def getPipeline():
            pipeline = DeploymentPolicy.getPipeline( self.policy )
            pipeline.steps[3].insert( 4, observer )
            return pipeline

        old_pipe = self.policy.getPipeline
        
        self.policy.getPipeline = getPipeline            
        self.policy.execute()
        self.policy.getPipeline = old_pipe
        
        expected = ['/portal', '/portal/about', '/portal/about/index_html']
        for ob in observer.content:
            opath =  "/".join( ob.getContent().getPhysicalPath())
            assert opath in expected
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDeletionSource))
    return suite

if __name__ == '__main__':
    unittest.main()
