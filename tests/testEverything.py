"""
Purpose: Unittests for testing incremental, pipeline and dependencies
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 11/16/2005
$Id: $
"""
import os, sys, time, shutil
from stat import ST_MTIME

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


TESTDEPLOYDIR = os.path.join( DeploymentProductHome, 'tests', 'deploy')

# these two settings operate together
LEAVE_DEPLOY_DIR=True
CLEAN_DEPLOY_DIR=True

class TestEverything (PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner()
        
        if os.path.exists( TESTDEPLOYDIR ) and CLEAN_DEPLOY_DIR:
            shutil.rmtree( TESTDEPLOYDIR )
        
        if not os.path.exists( TESTDEPLOYDIR ):
            os.mkdir( TESTDEPLOYDIR )
        
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
        
        structure = self.policy.getContentOrganization().getActiveStructure()
        structure.mount_point = TESTDEPLOYDIR
        
        get_transaction().commit(1)
          
        
    def testDeployFolder(self):  
        self.portal.invokeFactory('Folder', 'folderwithindex')
        folderwithindex = self.portal.folderwithindex
        folderwithindex.edit(title="my folder")
        
        self.policy.execute()
        
        location = os.sep.join( ( TESTDEPLOYDIR, "folderwithindex") )
        self.assertEqual(os.path.exists(location), True, "Location should be folderwithindex")
    
    def testDeployDocument(self):
        self.testDeployFolder()
        folderwithindex = self.portal.folderwithindex
        folderwithindex.invokeFactory('Document', 'docwithindex')
        docwithindex = folderwithindex.docwithindex
        
        self.policy.execute()
        
        location = os.sep.join( ( TESTDEPLOYDIR, "folderwithindex", "docwithindex.html") )
        self.assertEqual(os.path.exists(location), True, "Location should be docwithindex.html")
    
    def testDeployImage(self):
        logo = self.portal['logo.jpg']
        content = str(logo)
        self.portal.invokeFactory('Image', 'vera.jpg')
        self.portal['vera.jpg'].edit(file=content)
        
        self.policy.execute()
        
        location = os.sep.join( ( TESTDEPLOYDIR, "vera.jpg") )
        self.assertEqual(os.path.exists(location), True, "Location should be vera.jpg")
    
    def testDeleteDocument(self):
        self.testDeployDocument()
        self.portal.folderwithindex.manage_delObjects(["docwithindex"])
        
        self.policy.execute()
        
        location = os.sep.join( ( TESTDEPLOYDIR, "folderwithindex", "docwithindex.html") )
        self.assertEqual(os.path.exists(location), False, "Location shouldn't exist")
    
    def testDeleteFolder(self):
        self.testDeployFolder()
        self.portal.manage_delObjects(["folderwithindex"])
        
        self.policy.execute()
        
        location = os.sep.join( ( TESTDEPLOYDIR, "folderwithindex") )
        self.assertEqual(os.path.exists(location), False, "Location shouldn't exist")
    
    def testDeleteImage(self):
        self.testDeployImage()
        self.portal.manage_delObjects(["vera.jpg"])
        
        self.policy.execute()
        
        location = os.sep.join( ( TESTDEPLOYDIR, "vera.jpg") )
        self.assertEqual(os.path.exists(location), False, "Location shouldn't exist")
        
    def testDependentContent(self):
        self.portal.portal_catalog.indexObject( self.portal )

        self.portal.invokeFactory('Document','index_html')
        self.portal.invokeFactory('Document','pouet')
        
        news_index_content = '''\
        <html>
        <body>
        # relative url
        <a href="../about">About Us</a>
        # absolute url
        <a href="/portal/about/contact">Jobs - You Wish!</a>    
        # javascript url
        <a href="javascript:this.print()">Print Me</a>    
        # mailto url
        <a href="mailto:deployment@example.com">Print Me</a>    
        # test self referencing content
        <a href="./index_html"> My Self </a>
        <a href="/portal/pouet">My Self aliased</a>
        <a href=".">My Self</a>
        # test anchor link inside of page
        <a href="#furtherdown">Down the page</a>
        this is some more text
        <a name="furtherdown"></a>
        here is stuff that is further down the page.
        </body>
        </html>
                '''
        self.portal.index_html.edit(text_format='html', text=news_index_content)
    
        self.policy.execute()
        
        pathname = os.sep.join( ( TESTDEPLOYDIR, "index.html") )
        pathname2 = os.sep.join( ( TESTDEPLOYDIR, "pouet.html") )

        mtime1 = os.stat(pathname)[ST_MTIME]

        self.portal.pouet.edit(text_format='html', text=news_index_content)
        time.sleep(10.0)

        self.policy.execute()
        
        mtime2 = os.stat(pathname)[ST_MTIME]
       
        self.assertNotEqual(mtime1,mtime2,'Modification time did not change')
        
    def XtestDependentContent(self):
        self.portal.portal_catalog.indexObject( self.portal )

        self.portal.invokeFactory('Document','index_html')
        self.portal.invokeFactory('Document','pouet')
        
        news_index_content = '''\
        <html>
        <body>
        # relative url
        <a href="../about">About Us</a>
        # absolute url
        <a href="/portal/about/contact">Jobs - You Wish!</a>    
        # javascript url
        <a href="javascript:this.print()">Print Me</a>    
        # mailto url
        <a href="mailto:deployment@example.com">Print Me</a>    
        # test self referencing content
        <a href="./index_html"> My Self </a>
        <a href="/portal/pouet">My Self aliased</a>
        <a href=".">My Self</a>
        # test anchor link inside of page
        <a href="#furtherdown">Down the page</a>
        this is some more text
        <a name="furtherdown"></a>
        here is stuff that is further down the page.
        </body>
        </html>
                '''
        self.portal.index_html.edit(text_format='html', text=news_index_content)
    
        self.policy.execute()
        
        pathname = os.sep.join( ( TESTDEPLOYDIR, "index.html") )
        pathname2 = os.sep.join( ( TESTDEPLOYDIR, "pouet.html") )

        mtime1 = os.stat(pathname)[ST_MTIME]

        self.portal.pouet.edit(text_format='html', text=news_index_content)
        time.sleep(10.0)

        self.policy.execute()
        
        mtime2 = os.stat(pathname)[ST_MTIME]
       
        self.assertNotEqual(mtime1,mtime2,'Modification time did not change')
        
    def testDependentContent2(self):
        self.portal.portal_catalog.indexObject( self.portal )
        self.portal.invokeFactory('Document','index_html')
        self.portal.invokeFactory('Document','pouet')
        self.portal.invokeFactory('Document', 'foo')
        
        news_index_content = '''\
        <html>
        <body>
        # relative url
        <a href="../about">About Us</a>
        # absolute url
        <a href="/portal/about/contact">Jobs - You Wish!</a>    
        # javascript url
        <a href="javascript:this.print()">Print Me</a>    
        # mailto url
        <a href="mailto:deployment@example.com">Print Me</a>    
        # test self referencing content
        <a href="./index_html"> My Self </a>
        <a href="/portal/pouet">My Self aliased</a>
        <a href=".">My Self</a>
        # test anchor link inside of page
        <a href="#furtherdown">Down the page</a>
        this is some more text
        <a name="furtherdown"></a>
        here is stuff that is further down the page.
        </body>
        </html>
        '''
        self.portal.index_html.edit(text_format='html', text=news_index_content)
        self.portal.foo.edit(text_format='html', text='du texte')
        self.policy.execute()
        
        pathname = os.sep.join( ( TESTDEPLOYDIR, "foo.html") )
        #pathname2 = os.sep.join( ( TESTDEPLOYDIR, "pouet.html") )
        mtime1 = os.stat(pathname)[ST_MTIME]

        self.portal.pouet.edit(text_format='html', text=news_index_content)
        time.sleep(10.0)
        self.policy.execute()
        mtime2 = os.stat(pathname)[ST_MTIME]
       
        self.assertEqual(mtime1,mtime2,'Modification time did change')
    
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEverything))
    return suite

if __name__ == '__main__':
    unittest.main()
