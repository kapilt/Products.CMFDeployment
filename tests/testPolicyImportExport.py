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
Purpose: Unitests for Polixy Xml Import Export
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 12/29/2002
$Id: $

"""

import os, sys, timeif __name__ == '__main__':    execfile(os.path.join(sys.path[0], 'framework.py'))
    
from Testing import ZopeTestCasefrom Products.PloneTestCase.PloneTestCase from PloneTestCaseZopeTestCase.installProduct('CMFDeployment')

import unittest
from types import StringType, NoneType
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import DeploymentProductHome

class PolicyImportExportTests( ZopeTestCase.ZopeTestCase ):

    def afterSetUp(self): 
        pass
        
    def beforeTearDown(self):
        pass

    def testImport(self):
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'plone.xml') 
        fh = open( policy_file )

        


def test_suite():
    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(ResolverTests))
    return suite

if __name__ == '__main__':
    framework() 
