##################################################################
#
# (C) Copyright 2002-2006 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
Purpose: Update Intra Content URL References
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id$
"""

import re
import types
import string
import pprint

from urlparse import urlparse

from Log import LogFactory
from BTrees.OOBTree import OOBTree

log = LogFactory('URIResolver')

class ResolutionError(Exception): pass

_marker = []

LINKING_ERROR_REPLACEMENT = 'deployment_linking_error'


class URIResolver:
    """

    Creates a database of urls such that it can replace
    urls in rendered content to reflect new locations.

    uri database maps
    
     source_absolute_relative -> target_absolute_relative
    
     - target_absolute_relative = target_path + content_path_relative_to_mount_point
     - source_absolute_relative = content.absolute_relative(1)

    replaced url types

      all replaced urls are found with the url_regex below. it will find href and src
      urls. 

      - absolute - http://
      - relative - ../foo, bar/baz
      - absolute relative /foo/bar

    instances of this class need to be persisted for incremental deployments,
    to preserve the url database.

    XXX test url get args in links    
    """
    
    # XXX VHOST HACK FIX - REMOVE ME
    # if you don't have a proper virtual host setup.. than you can set this
    # and it will be added to the url    
    vhost_path = '' 
    link_error_url = 'deploy_link_error'
    ext_resolver = None
    external_resolver_path = None
    
    def __init__(self,
                 id='',
                 source_host='http://localhost',
                 mount_path = '/',
                 target_path='/',
                 link_error_url='deploy_link_error'):
        
        self.id = id
        self.source_host = source_host
        self.target_path = target_path
        self.mount_path = mount_path
        self.link_error_url = link_error_url
        self.mlen = len(mount_path)
        self.uris = OOBTree()

    def setupExternalResolver(self):
        if not self.external_resolver_path or not '.' in self.external_resolver_path :
            return
        module_name, from_list = rsplit( self.external_resolver_path, '.', 1)
        try:
            module = __import__( module_name, globals(), locals(), [from_list])
            ext_resolver = getattr( module, from_list )
            if isinstance(ext_resolver, types.ClassType):
                self.ext_resolver = ext_resolver()
            elif isinstance( ext_resolver, types.FunctionType):
                self.ext_resolver = ext_resolver

            if self.ext_resolver:
                assert callable( self.ext_resolver )                
        except (ImportError, AttributeError, AssertionError):
            self.ext_resolver = None
        

    def addResource(self, descriptor):

        for descriptor in descriptor.getDescriptors():
            self._addResource( descriptor )

    def removeResource( self, descriptor ):
        for descriptor in descriptor.getDescriptors():
            self._removeResource( descriptor )
            
    def _removeResource(self, descriptor):
        relative_url = descriptor.getSourcePath() or descriptor.content_url
        if not relative_url.startswith('/'):
            relative_url = '/'+relative_url
        del self.uris[relative_url]
        for alias in descriptor.getAliases():
            alias_url = normalize( relative_url + '/' + alias, '/')
            if self.uris.has_key(alias_url):
                del self.uris[ alias_url ]
        
    def _addResource(self, descriptor):

        relative_url = descriptor.getSourcePath() or descriptor.content_url

        content_path = descriptor.getContentPath()
        
        if relative_url[0] != '/':
            relative_url = '/'+relative_url
        
        if content_path is None:
            mlen = len(self.mount_path)
            if not self.mount_path.startswith('/'):
                mlen += 1
                
            # minus last path segment
            # find the path segment            
            url_context  = relative_url[:relative_url.rfind('/')]
            content_path = url_context[mlen:]

        content_path = normalize('/'.join( (self.target_path,
                                            content_path,
                                            descriptor.getFileName() ) ),
                                 '/'
                                 )

        log.debug("add %s -> %s"%(relative_url, content_path))
        self.uris[relative_url]=content_path

        if descriptor.isContentFolderish():
            self.uris[relative_url+'/']=content_path

        # lets add in the generic CMF view method as well
        self.uris[normalize(relative_url+'/view', '/')] = content_path

        for alias in descriptor.getAliases():
            self.uris[ normalize( relative_url+'/'+alias, '/')] = content_path
        
    def resolveURI(self, u, content_url, content_folderish_p, default=_marker, content=None):
        """
        determine a replacement for a url u, found in the body
        of a rendered content object with content_url.

        u - url to be replaced
        content_url - url of content where u was found
        content_folderish_p - is the content a folderish object
        default - value to be returned if replacement not needed

        returns None if url doesn't need replacement. returns default
        if replacement not found.
        """

        rnu = None
        
        if not u:
            return

        # absolute url
        elif u.startswith('http'):

            # extern check
            if not u.find(self.source_host) >= 0:
                return

            # within mount check
            if u.count(self.mount_path) == 0:
                nu = None

            # convert to absolute_relative and lookup
            nu = self.uris.get( urlparse(u)[2], default)

        # absolute relative /
        elif u.startswith('/'):
            #nu = self.uris.get('%s/%s'%(self.source_host,u), default)
            nu = self.uris.get(u, default)
            
        # relative with .||.. prefix
        elif u.startswith('.'):
            rnu = resolve_relative(
                content_url,
                u,
                content_folderish_p)

            nu = self.uris.get(rnu, default)
            
        # anchor link
        elif u.startswith('#'):
            return

        # non http browser protocols XXX optimize me
        elif u.startswith('mailto:'):
            return
        elif u.startswith('ftp:'):
            return
        elif u.startswith('nntp:'):
            return
        elif u.startswith('ldap:'):
            return
        elif u.startswith('imap:'):
            return
        elif u.startswith('gopher:'):
            return
        elif u.startswith('pop:'):
            return
        elif u.startswith('aol:'):
            return
        elif u.startswith('mms:'):
            return
        elif u.startswith('javascript:'):
            return    
        # possibly a relative url
        else:            
            rnu = resolve_relative(content_url, u, content_folderish_p)
            nu = self.uris.get(rnu, default)
        # try some basic acquisition tricks, and assure that the acquired
        # object is resolvable in the uri db.
        if nu is _marker and content:
            nu = self._resolveAcquired( content, u, rnu )
        return nu

    def _resolveAcquired(self, content, url, relative_url ):
        # if we acquire the object by id directly then and its being deployed
        # then go ahead with the resolution
        if relative_url:
            url = relative_url
        parts = url.split('/')
        if not parts[-1]:
            del parts[-1]
        oid = parts[-1]
        object = getattr( content, oid, None )

        # Ok, on Plone 2.1, we can get a view object here.
        # We don't want it, we want a real object.
        
        if isinstance( object, (types.FunctionType, types.MethodType)):
            oid = parts[-2]
            object = getattr( content, oid, None )
            
        if not object:
            return _marker
        return  self.uris.get("/"+object.absolute_url(1), _marker)
    
    def resolve(self, descriptor):

        """
        regex to find all uris.
        classify as either
          - content relative - ../foo
          - absolute relative - /portal/content
          - absolute - http://foobz:8080/baz/blurbie
          
          XXX need to add handling of absolute folder with ending slash [CHP]
          
        relative uris, convert to absolute uris

        XXX for folder types, we replace to the view  not the
        folder path, it be nice to go to the path.

        # XXX
        # if we have a link reference to
        # non deployable content
        # we need some sort of policy decision
        """

        for descriptor in descriptor.getDescriptors():
            if descriptor.isBinary() or descriptor.isGhost():
                continue
            self._resolveDescriptor( descriptor )

    def _resolveDescriptor(self, descriptor ):


        r = descriptor.getRendered()
        uris = unique( filter( lambda u: u[1], (url_regex.findall(r) +\
                                                css_regex.findall(r))
                                                ) )
        content_folderish_p = descriptor.content_folderish_p and not \
                              descriptor.composite_content_p
        
        content_url = descriptor.getSourcePath() or descriptor.getContentURL()
        
        count = 0
        total_count = 0
        
        for l, u in uris:
            
            total_count += 1            
            nu = self.resolveURI(u, content_url, content_folderish_p, content=descriptor.getContent())
            
            if nu is _marker and self.ext_resolver is not None:
                nu = self.ext_resolver( u, content_url, content_folderish_p, _marker, descriptor )
                
            if nu is _marker:
                log.warning('unknown url (%s) from %s'%(u, content_url))
                nu = self.link_error_url
                
            elif nu is None:
                count+=1
                continue
            else:
                count += 1

            r = r.replace(l, l.replace(u, nu))
            
        #log.debug('resolved %d intern references of %d total refs'%(
        #                                                  count, total_count))
        descriptor.setRendered(r)

    def getURIs(self):
        return self.uris.items()


    def __getitem__(self, key):
        return self.uris[key]

    def pprint(self):
        pprint.pprint(dict(self.uris.items()))
            

def rsplit( value, sep, max=0):
    if max == 0:
        return value.split(sep)
    # naive.. could also do rfind, but for small size this is fine
    res = value.split(sep)
    if len(res) <= max:
        return res
    join_val = sep.join( res[:-max] )
    res[:-max] = [join_val]
    return res

def extend_relative_path(path):
    "extend '..' path"
    path_list = path.strip().split('/')
    mark = '..'
    while path_list.count(mark):
        index = path_list.index(mark)
        del path_list[index]
        del path_list[index-1]
    return '/'.join(path_list)

def clstrip(string, character):
    # specialized (c)haracter (l)eft strip, leaves one occurence
    idx = 0
    while 1:
        if string[idx]==character:
            idx += 1
        else:
            break
    if idx > 1:
        return string[idx-1:]
    return string

def normalize(string, character):
    # slightly different version of above, it removes duplicates inline as well
    # so ///f/a/t/////a -> /f/a/t/adef normalize(string, character):
    # it always inserts a char to start with 
    res = filter(None, string.split(character))
    res.insert(0, '')
    return character.join(res)

def unique(lst):
    d = {}
    for l in lst:
        d[l]=None
    return d.keys()


####################################

def resolve_relative(content_url, relative_url, content_folderish_p=0):
    """
    content_url - url of the content we are resolving from
    relative_url - 
    content_folderish_p - is the content a folderish object, 
                          if the content is folderish we remove
                          1 initial path segment
                          ie from foo_folder ../bar.txt
                          means get it from the parent folder
                          whereas foo_folder/doc ../bar.txt
    

    """
    
    # (addressing scheme, network location, path, query, fragment identifier)
    info = urlparse(content_url)
    content_path = info[2]
    
    path_steps = filter(None, content_path.split('/'))
    steps = filter(None, relative_url.split('/'))

    
    if steps[0] == '..':
        # move back two if not folder or one if a folder
        steps.pop(0)
        move = 1 + (not content_folderish_p)
        if not path_steps:
            # broken relative url referencing past root            
            return None        
        path_steps = path_steps[:-move]
    elif steps[0] == '.' and not content_folderish_p:
        steps.pop(0)
        path_steps.pop(-1)
    elif not content_folderish_p:
        path_steps.pop(-1)

    for s in steps:
        if s == '..':            
            if not path_steps:
                # broken relative url referencing past root
                return None                    
            path_steps.pop(-1)
        elif s == '.':
            pass
        else:
            path_steps.append(s)

    path_steps.insert(0,'')
    resolved = '/'.join(path_steps)
    
    return resolved

url_regex = re.compile("""(?P<url>(?:href=|src=|@import)\s*["']\s*(.*?)["'])""")
test_uri_regex = re.compile('''(?:href=|src=|@import)\s*["']\s*(.*?)["']''')
css_regex  = re.compile("""(?P<url>url\(['"]{0,1}\s*(.*?)['"]{0,1}\))""")
test_css_regex  = re.compile("""url\(['"]{0,1}\s*(?P<url>.*?)['"]{0,1}\)""")
