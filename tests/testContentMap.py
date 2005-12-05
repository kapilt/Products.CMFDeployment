"""
Purpose: Unittests for testing ContentMap.py
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 11/14/2005
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

from Products.CMFDeployment import ContentMap
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment.Descriptor import DescriptorFactory

def setupContentTree( portal ):
    portal.portal_catalog.indexObject( portal )

    portal.invokeFactory('Folder', 'news')
    portal.news.invokeFactory('Document','index_html')
    
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
    <a href="/portal/news/index_html">My Self aliased</a>
    <a href=".">My Self</a>
    
    # test anchor link inside of page
    <a href="#furtherdown">Down the page</a>
    
    this is some more text
    
    <a name="furtherdown"></a>
    here is stuff that is further down the page.
    </body>
    </html>
    '''
    portal.news.index_html.edit(text_format='html', text=news_index_content)

class MyContentMap(PloneTestCase):
    
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
        
        setupContentTree(self.portal)
        
        self.policy = deployment_tool.getPolicy('plone_example')
        self.catalog= getToolByName(self.policy, "portal_catalog")
        self.factory= DescriptorFactory( self.policy )
        self.mastering= self.policy.getContentMastering()
        
        get_transaction().commit(1)
        
    def testAddContentMap(self):   
        self.policy.execute()
        
        uid= '/'.join( self.portal.news.index_html.getPhysicalPath() )     
        structure = self.policy.getContentOrganization()
        views     = self.policy.getContentDirectoryViews()
        views.mountDirectories(structure.getActiveStructure())
        structure.mount()
        mount_point = structure.getActiveStructure().getCMFMountPoint()
        mount_path = mount_point.getPhysicalPath()
        mlen = len('/'.join(mount_path)) 
        content = self.policy.getContentIdentification().getContent(mount_length=mlen)
        
        for ci in content:
            if (ci.getPath() == uid):
                co = ci.getObject()      
                descriptor= self.factory( co )
                self.mastering.prepare( descriptor )
                result= self.policy.getContentMap().getReverseDependencies(descriptor)
                self.assertEqual(result,['/portal/Members/test_user_1_', '/portal/news', '/portal/news/index_html'], "Result should be ['/portal/Members/test_user_1_', '/portal/news', '/portal/news/index_html']")
        
    def testCleanContentMap(self):
        self.policy.execute()
    
        uid= '/'.join( self.portal.news.index_html.getPhysicalPath() )     
        structure = self.policy.getContentOrganization()
        views     = self.policy.getContentDirectoryViews()
        views.mountDirectories(structure.getActiveStructure())
        structure.mount()
        mount_point = structure.getActiveStructure().getCMFMountPoint()
        mount_path = mount_point.getPhysicalPath()
        mlen = len('/'.join(mount_path)) 
        content = self.policy.getContentIdentification().getContent(mount_length=mlen)
        
        for ci in content:
            if (ci.getPath() == uid):
                co = ci.getObject()      
                descriptor= self.factory( co )
                self.mastering.prepare( descriptor )
                result= self.policy.getContentMap().clean(descriptor)
        my_dict = dict(self.policy.getContentMap().content_map.items())
        values = my_dict['/css/plone.css']
        self.assertEqual(values, ['/portal/Members/test_user_1_', '/portal/news'], 'Index_html should have been deleted')
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite= unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MyContentMap))
        return suite    
