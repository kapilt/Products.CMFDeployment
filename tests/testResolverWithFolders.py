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
Purpose: Unitests for URIResolver
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 12/29/2002
$Id: $
"""

import os, sys, timeif __name__ == '__main__':    execfile(os.path.join(sys.path[0], 'framework.py'))from Testing import ZopeTestCasefrom Products.CMFPlone.tests.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('CMFDeployment')

import unittest
from types import StringType, NoneType
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.URIResolver import resolve_relative, URIResolver, test_uri_regex, test_css_regex, _marker
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment.MimeMapping import getMimeExprContext


class ResolveFolderURITests(PloneTestCase):

    def afterSetUp(self): 
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('CMFDeployment')
        self.loginPortalOwner()
        self.portal.invokeFactory('Folder', 'folderwithindex')
        self.portal.invokeFactory('Folder', 'folderwithoutindex')
        self.folderwithindex = self.portal.folderwithindex         
        self.folderwithoutindex = self.portal.folderwithoutindex         
        self.folderwithindex.invokeFactory('Document', 'index_html')         
        
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        
        self.policy = policy = deployment_tool.getPolicy('plone_example')
        self.rules = policy.getContentMastering().mime
        self.resolver = self.policy.getDeploymentURIs()
        self.resolver.source_host = 'http://www.example.com'
        self.resolver.mount_path = '/portal'
        self.resolver.target_path = '/deploy'
        
    def beforeTearDown(self):
        self.rules = None
        self.folderwithindex = None
        self.folderwithoutindex = None
        self.policy = None

    def testSimpleFolderWithIndexURIResolution(self):
        factory = DescriptorFactory( self.policy )
        descriptor = factory( self.folderwithindex )
        context = getMimeExprContext( self.folderwithindex, self.portal)
        descriptor = self.rules.Folder.process( descriptor, context )
        mastering = self.policy.getContentMastering()
        mastering.setup()
        mastering.cook( descriptor )
        mastering.tearDown()

        rendered = descriptor.getRendered()
        import pdb; pdb.set_trace();
        self.resolver.addResource( descriptor )
        
        content_url = descriptor.getSourcePath() or descriptor.getContentURL()        
        marker = object()

        result = self.resolver.resolveURI( 'http://www.example.com/portal/folderwithindex/',
                                      content_url,
                                      True,
                                      marker
                                      )

        self.assertNotEqual( result, marker )
        self.assertNotEqual( result, self.resolver.link_error_url )
        self.assertEqual( result, '/deploy/folderwithindex/index.html')
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResolveFolderURITests))
    return suite

if __name__ == '__main__':
    framework() 
