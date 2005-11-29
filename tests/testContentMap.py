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

class MyContentMap(PloneTestCase):
    
    def afterSetUp(self):
        pass       
        
    def testContentMap1(self):
        #before doing those tests, you got to change the
        #method getReverseDependencies
        one_map= ContentMap.ContentMap()
        one_map.addContentMap("pouet", "/pouet/ici/")
        result= one_map.getReverseDependencies("pouet")
        self.assertEqual(result,['/pouet/ici/'], 'Result should be /pouet/ici/')

        
    def testContentMap2(self):
        one_map= ContentMap.ContentMap()
        one_map.addContentMap("pouet", "/pouet/ici/")
        result= one_map.getReverseDependencies("pouette")
        self.assertEqual(result,[], 'Result should be None')
        
    def testContentMap3(self):
        one_map= ContentMap.ContentMap()
        one_map.addContentMap("pouet", "/pouet/ici/")
        one_map.addContentMap("pouet", "/pouet/parla/")
        result= one_map.getReverseDependencies("pouet")
        self.assertEqual(result,['/pouet/ici/', '/pouet/parla/'], "Result should be ['/pouet/ici/', '/pouet/parla/']")
        
    def testContentMap4(self):
        one_map= ContentMap.ContentMap()
        one_map.addContentMap("pouet", "/pouet/ici/")
        one_map.addContentMap("pouet", "/pouet/parla/")
        one_map.addContentMap("bonjour","/bonjour/bienvenue/")
        one_map.addContentMap("pouet", "/pouet/pouetpouet/")
        one_map.pprint()
        
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite= unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MyContentMap))
        return suite    
