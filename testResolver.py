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

import unittest
from types import StringType, NoneType
#from Products.CMFDeployment.Descriptor import ContentDescriptor
#from Products.CMFDeployment.URIResolver import resolve_relative, URIResolver, uri_regex, _marker
from Descriptor import ContentDescriptor
from URIResolver import resolve_relative, URIResolver, uri_regex, _marker

class Content:

    def __init__(self, relative, content):
        self.relative = relative
        self.content = content
        self.id = relative[relative.rfind('/')+1:]

    def absolute_url(self, relative=0):
        if relative: return self.relative
        raise "bg"

    def getFileName(self):
        if getattr(self, 'isAnObjectManager', 0):
            if self.id:
                return '%s/index.html'%self.id
            return "index.html"
        return "%s.html"%self.id

class FolderContent(Content):
    isAnObjectManager = 1

class CompositeContent(FolderContent):
    isCompositeContent = 1  # hardcodejust for testing, config in organization

class ContentDB:

    root = FolderContent('/', """
    <css @import="http://www.example.com/style/site.css" />
    
    <image href="/images/bar.gif">bar</image>
    This is a test <a href="/reptiles/snake">snake</a>
    This is a test <a href="mammals/elephant">snake</a>
    This is a test <a href="./reptiles/snake">snake</a>   
    """)
    
    #################################
    reptiles = FolderContent("/reptiles", """
    This is a test <a href="snake">snake</a>   
    This is a test <a href="./lizard">snake</a>   
    """)
    
    snake = Content("/reptiles/snake", """
    <a href="/">Root</a>
    This is a test <a href="../mammals/elephant">snake</a>
    This is a test <a href="./snake">snake</a>   
    This is a test <a href="./lizard">snake</a>   
    """)
                  
    lizard = Content("/reptiles/lizard", """
    This is a test <a href="snake">snake</a>   
    This is a test <a href="http://www.example.com/reptiles/snake">snake</a>   
    """)
    
    #################################
    mammals  = FolderContent("/mammals", "")
    elephant = Content("/mammals/elephant","""
    """)
    
    whale = Content("/mammals/whale", """
    """)


    loch_ness= CompositeContent("/reptiles/loch_ness", """
    This is a test <a href="snake">snake</a>   
    This is a test <a href="./lizard">lizard</a>   
    """)

    #################################
    images = FolderContent("/images", "")
    bar_image = Content("/images/bar.gif", "")
    style = FolderContent("/style", "")
    style_image = Content("/style/site.css", "")


class DescriptorDB:
    pass

def setupDescriptors():
    for i, c in ContentDB.__dict__.items():
        if not isinstance(c, Content):
            continue

        d = ContentDescriptor(c)
        d.content_url = c.absolute_url(relative=1)
        d.content_folderish_p = getattr(c, 'isAnObjectManager', 0)
        d.composite_content_p = getattr(c, 'isCompositeContent', 0)
        
        d.setRendered(c.content)
        d.setExtension(c.getFileName())
        setattr(DescriptorDB, i, d)

setupDescriptors()

def getDescriptor(name=None):
    if name is not None:
        return getattr(DescriptorDB, name)
    return filter(lambda x: isinstance(x, ContentDescriptor),
                  DescriptorDB.__dict__.values())


class BaseResolverTests(unittest.TestCase):
    
    def setUp(self):

        resolver = URIResolver( id='resolver',
                                source_host='http://www.example.com',
                                mount_path='/',
                                target_path='/deploy'
                                )

        self.resolver = resolver

        for d in getDescriptor():
            self.resolver.addResource(d)

    def tearDown(self):
        self.resolver = None


class ResolveURITests(BaseResolverTests):

    def testAddResource(self):
        d = getDescriptor('root')
        c = d.getContent()         
        self.assertEqual('/deploy/index.html', self.resolver[c.absolute_url(1)])

    def testAddResource2(self):

        for d in getDescriptor():
            c = d.getContent()
            segments = filter(None, c.absolute_url(relative=1).split('/'))
            if segments:
                segments.pop()
            segments.append(d.getFileName())
            segments.insert(0, self.resolver.target_path)
            self.assertEqual('/'.join(segments), self.resolver[c.absolute_url(1)])

    def testResolverURI(self):
        # identity
        r = getDescriptor('root')
        uri = r.getContent().absolute_url(1)
            
        nu = self.resolver.resolveURI(uri, uri, 1)
        self.assertEqual(nu, '/deploy/index.html')

    def testResolverURI2(self):
        # absolute intern
        r = getDescriptor('root')
        curi = r.getContent().absolute_url(1)
        uri = 'http://www.example.com/reptiles/snake'
        
        nu = self.resolver.resolveURI(uri, curi, 1)        
        self.assertEqual(nu, '/deploy/reptiles/snake.html')

    def testResolverURI3(self):
        # absolut extern
        r = getDescriptor('root')
        curi = r.getContent().absolute_url(1)
        uri = 'http://www.foobar.com/reptiles/snake'
        
        nu = self.resolver.resolveURI(uri, curi, 1)
        self.assertEqual(nu, None)

    def testResolverURI4(self):
        # ftp
        r = getDescriptor('root')
        curi = r.getContent().absolute_url(1)
        uri = 'ftp://www.slashdot.org/backend.rss'
        
        nu = self.resolver.resolveURI(uri, curi, 1)
        self.assertEqual(nu, None)        

    def testResolverURI5(self):
        # anchor
        r = getDescriptor('root')
        curi = r.getContent().absolute_url(1)
        uri = '#top'
        
        nu = self.resolver.resolveURI(uri, curi, 1)
        self.assertEqual(nu, None)

    def testResolverURI6(self):
        # test relative name from folder
        r = getDescriptor('root')
        curi = r.getContent().absolute_url(1)
        uri = 'mammals/elephant'
        
        nu = self.resolver.resolveURI(uri, curi, 1)
        self.assertEqual(nu, '/deploy/mammals/elephant.html')

    def testResolverURI7(self):
        # test .. relative on root
        r = getDescriptor('root')

        curi = r.getContent().absolute_url(1)
        uri = '../mammals/elephant'

        nu = self.resolver.resolveURI(uri, curi, 1)
        self.assertEqual(nu, _marker)

    def testResolverURI8(self):
        # relative .. from non folder
        r = getDescriptor('snake')
        curi = r.getContent().absolute_url(1)
        uri = '../mammals/elephant'

        nu = self.resolver.resolveURI(uri, curi, 0)
        self.assertEqual(nu, '/deploy/mammals/elephant.html')

    def testResolverURI9(self):
        # relative .. from non-root folder
        r = getDescriptor('reptiles')
        curi = r.getContent().absolute_url(1)
        uri = './snake'

        nu = self.resolver.resolveURI(uri, curi, 1)
        self.assertEqual(nu, '/deploy/reptiles/snake.html')

    def testResolverURI10(self):
        # relative . from non folder
        r = getDescriptor('lizard')
        curi = r.getContent().absolute_url(1)
        uri = './snake'

        nu = self.resolver.resolveURI(uri, curi, 0)
        self.assertEqual(nu, '/deploy/reptiles/snake.html')

    def testResolverURI11(self):
        # relative . from non folder + default view

        r = getDescriptor('lizard')
        curi = r.getContent().absolute_url(1)
        uri = './snake/view'

        nu = self.resolver.resolveURI(uri, curi, 0)
        self.assertEqual(nu, '/deploy/reptiles/snake.html')

    def testResolverURL12(self):
        # relative name from non folder
        r = getDescriptor('lizard')
        curi = r.getContent().absolute_url(1)        
        uri = 'snake'

        nu = self.resolver.resolveURI(uri, curi, 0)
        self.assertEqual(nu, '/deploy/reptiles/snake.html')


class ResolverTests(BaseResolverTests):

    def testResolve(self):

        d = getDescriptor('snake')
        self.resolver.resolve(d)
        rendered_target = d.getRendered()

        expected = (            
            '/deploy/index.html',
            '/deploy/mammals/elephant.html',
            '/deploy/reptiles/snake.html',
            '/deploy/reptiles/lizard.html'
            )
            
        uris = uri_regex.findall(rendered_target)        
        self.assertEqual(len(uris), len(expected))

        for u in uris:
            assert u in expected

    def testResolve2(self):
        # test replacement algorithm

        d = getDescriptor('lizard')
        self.resolver.resolve(d)
        rendered_target = d.getRendered()

        expected = (            
            '/deploy/reptiles/snake.html',
            '/deploy/reptiles/snake.html',
            )
            
        uris = uri_regex.findall(rendered_target)        
        self.assertEqual(len(uris), len(expected))

        for u in uris:
            assert u in expected        

    def testResolve3(self):
        # test folder resolve

        d = getDescriptor('reptiles')
        self.resolver.resolve(d)
        rendered_target = d.getRendered()

        expected = (            
            '/deploy/reptiles/snake.html',
            '/deploy/reptiles/lizard.html',
            )            

        uris = uri_regex.findall(rendered_target)        
        self.assertEqual(len(uris), len(expected))

        for u in uris:
            assert u in expected
            
    def testResolve4(self):
        # composite content test
        d = getDescriptor("loch_ness")
        self.resolver.resolve(d)
        rendered_target = d.getRendered()

        expected = (            
            '/deploy/reptiles/snake.html',
            '/deploy/reptiles/lizard.html',
            )            

        uris = uri_regex.findall(rendered_target)        
        self.assertEqual(len(uris), len(expected))

        for u in uris:
            assert u in expected
        
class RelativeResolutionTests(unittest.TestCase):

    def testFromDocument(self):

        content_url = 'http://www.example.com/foo/bar/doc.html'
        relative_url = '../../cat/food.html'
        folderish_p = 0
        expected_url = '/cat/food.html'
        
        url = resolve_relative(content_url, relative_url, folderish_p)
        self.assertEqual(expected_url, url)

    def testFromDocument2(self):

        content_url = 'http://www.example.com/foo/bar/baz.html'
        relative_url = './bar.html'
        folderish_p = 0
        expected_url = '/foo/bar/bar.html'        

        url = resolve_relative(content_url, relative_url, folderish_p)
        self.assertEqual(expected_url, url)
        
    def testFromDocument3(self):
        
        content_url = 'http://www.example.com/foo/bar.html'
        relative_url = '../foo/../zebra.html'        
        folderish_p = 0
        expected_url = '/zebra.html'

        url = resolve_relative(content_url, relative_url, folderish_p)
        self.assertEqual(expected_url, url)
        
    def testFromDocument4(self):

        content_url = 'http://www.example.com/foo/index.html'
        relative_url = '../zebra.html'
        folderish_p = 0
        expected_url = '/zebra.html'

        url = resolve_relative(content_url, relative_url, folderish_p)
        self.assertEqual(expected_url, url)

    def testFromFolder2(self):

        content_url = 'http://www.example.com/foo'
        relative_url = '../orion.html'
        folderish_p = 1
        expected_url = '/orion.html'

        url = resolve_relative(content_url, relative_url, folderish_p)
        self.assertEqual(expected_url, url)

    def testFromFolder3(self):

        content_url = 'http://www.example.com/foo/bar'
        relative_url = '../orion.html'
        folderish_p = 1
        expected_url = '/foo/orion.html'

        url = resolve_relative(content_url, relative_url, folderish_p)
        self.assertEqual(expected_url, url)

    def testFromFolder4(self):

        content_url = 'http://www.example.com/foo/bar'
        relative_url = './orion.html'
        folderish_p = 1
        expected_url = '/foo/bar/orion.html'

        url = resolve_relative(content_url, relative_url, folderish_p)
        self.assertEqual(expected_url, url)

        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RelativeResolutionTests))
    suite.addTest(unittest.makeSuite(ResolveURITests))
    return suite

if __name__ == '__main__':
    unittest.main()
