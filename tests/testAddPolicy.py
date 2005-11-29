"""
Purpose: Unittests for testing when we add a policy
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 11/22/2005
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
from Products.ZCatalog import ZCatalog, Vocabulary
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog import ZCatalog
from Products.CMFDeployment import pipeline
from Products.CMFDeployment import dependencies
from Products.CMFDeployment import ContentMap
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
    
    portal.invokeFactory('Folder', 'about') 
    portal.about.invokeFactory( 'Document', 'index_html')
    about_index_content = '''
    <html><body>
    Case Studies
    
    case studies... <a href="/portal/logo.jpg"> Logo </a>
    we eaten at millions of mcdonalds...

    Dig our Cool JavaScript 
    <javascript src="/portal/plone_javascripts.js"/>
    <img src="/portal/vera.jpg"> logo </src>
    <img src="../vera.jpg"> logo </src>   
    <a href="/portal/news/index_html">Lucie</a>
    </body>
    </html>
    '''
    portal.about.index_html.edit(text_format="html", text=about_index_content)
    portal.about.invokeFactory('Document', 'contact')
    
    portal.invokeFactory('Folder','events')
    portal.events.invokeFactory( 'Event', 'Snow Sprint')
    portal.events['Snow Sprint'].edit( 
        title='Snow Sprint',
        description="fun not in the sun",
        location="Austria, EU",
        contact_name="jon stewart",
        contact_email="dubya@dailyshow.com",
        event_url="/portal/news/index_html")
            
    portal.events.invokeFactory('Event', 'cignex_sprint')
    portal.events.cignex_sprint.edit(
        title='Cignex Sprint',
        description="fun in the fog",
        location="Austria, EU",
        contact_name="jon stewart",
        contact_email="dubya@dailyshow.com",
        event_url="http://hazmat.gov")

class TestAddPolicy(PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner()
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('ATContentRule')
        installer.installProduct('CMFDeployment')
        #setupContentTree(self.portal)

        
   #################################     
    def testAddPolicy(self): 
        policy_file = os.path.join(DeploymentProductHome,'examples','policies', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        self.policy = deployment_tool.getPolicy('plone_example')

                
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAddPolicy))
    return suite

if __name__ == '__main__':
    unittest.main()
