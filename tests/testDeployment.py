##################################################################
#
# (C) Copyright 2002-2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
# All Rights Reserved
#
# This file is part of CMFDeployment.
#
# CMFDeployment is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CMFDeployment is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CMFDeployment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
Purpose: Unitests for Site Export
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 12/29/2002
$Id: $

"""

import os, sys, time, shutil, commandsif __name__ == '__main__':    execfile(os.path.join(sys.path[0], 'framework.py'))
    
from Testing import ZopeTestCasefrom Products.CMFPlone.tests.PloneTestCase import PloneTestCase
ZopeTestCase.installProduct('CMFDeployment')

import unittest
from StringIO import StringIO
from types import StringType, NoneType
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import DeploymentProductHome


TESTDEPLOYDIR = os.path.join( DeploymentProductHome, 'tests', 'deploy')


def setupContentTree( portal ):

    portal.invokeFactory('Folder', 'news')
    portal.news.invokeFactory('Document','index_html')
    
    news_index_content = """\
    <html>
    <body>
    # relative url
    <a href="../about">About Us</a>
    
    # absolute url
    <a href="/about/contact/index_html">Contact Us</a>
    <a href="/about/contact">Jobs - You Wish!</a>    
    
    # test self referencing content
    <a href="./index_html"> My Self </a>
    <a href="/news">My Self aliased</a>
    <a href=".">My Self</a>
    
    </body>
    </html>
    """
    
    portal.news.index_html.edit(text_format='html', text=news_index_content)
    portal.invokeFactory('Folder', 'about')
    
    
    portal.about.invokeFactory( 'Document', 'index_html')
    about_index_content = """\
    <html><body>
    Case Studies
    
    case studies... <a href="/logo.gif"> Logo </a>
    we eaten at millions of mcdonalds...

    Dig our Cool JavaScript 
    <javascript src="/plone_javascripts.js"/>
    <img src="/vera.jpg"> logo </src>
    <img src="../vera.jpg"> logo </src>    
    </body>
    </html>
    """    
    
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
        event_url="http://darpa.gov")
        
    portal.events.invokeFactory('Event', 'cignex_sprint')
    portal.events.cignex_sprint.edit(
        title='Cignex Sprint',
        description="fun in the fog",
        location="Austria, EU",
        contact_name="jon stewart",
        contact_email="dubya@dailyshow.com",
        event_url="http://hazmat.gov")    
        
    logo = portal['logo.jpg']
    content = str(logo)
    portal.invokeFactory('Image', 'vera.jpg')
    portal['vera.jpg'].edit(file=content)
    

    
class DeploymentTests( PloneTestCase ):

    def afterSetUp(self): 
        self.loginPortalOwner()
        setupContentTree(self.portal)
        
        if not os.path.exists( TESTDEPLOYDIR ):
            os.mkdir( TESTDEPLOYDIR )

        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('CMFDeployment')

        policy_file = os.path.join( DeploymentProductHome, 'examples', 'plone.xml') 
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        policy = deployment_tool.getPolicy('plone_example')
        structure = policy.getContentOrganization().getActiveStructure()
        structure.mount_point = TESTDEPLOYDIR
        fh.close()
        get_transaction().commit(1)
        
    def beforeTearDown(self):
        if os.path.exists( TESTDEPLOYDIR ):
            pass
            #shutil.rmtree( TESTDEPLOYDIR )

    def testDeploy(self):
        # push the content to the fs
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.plone_example.execute()
        
        status, output = commands.getstatusoutput(
            "grep -rn deploy_link_error %s/*"%TESTDEPLOYDIR
            )
            
        if status:
            raise AssertionError, "Could not verify content %s"%(output)
            
        lines = output.strip().split('\n')
        if not lines:
            return
            
        for line in lines:
            print line
                

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DeploymentTests))
    return suite

if __name__ == '__main__':
    framework() 
