##################################################################
#
# (C) Copyright 2002-2006 Kapil Thangavelu <k_vertigo@objectrealms.net
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
Purpose:
    
implements merging of directory views into a deployment

you pick a directory view, as a path relative to the portal_skins
tool and a path relative to the deploymnt root to map it to,
and whether the contents should be cooked or used as is...

content in directory views does get matched to the mimes
system, the id is used directly as the filename.

# 7/27/2005 - not sure that the following is still true, prolly not,
# due to the use of portal skin relative path as a uniqueness factor
# in the dv handling, which is explictly checked.
# you can merge a single directory view more than once if need be.

we reimplement some of content mastering here, as the semantics
needed for fs types are much different than normal content objects..
of course i'm doing this while sleepy so refactoring latter is an option ;-)

Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
$Id$
License: GPL

"""

import types

from Globals import HTML
from AccessControl import getSecurityManager
from OFS.OrderedFolder import OrderedFolder

from Products.CMFCore.utils import getToolByName

from Namespace import *
from Log import LogFactory
from Descriptor import ContentDescriptor
from URIResolver import clstrip, extend_relative_path

from DeploymentExceptions import InvalidDirectoryView

log = LogFactory('Directory Views')

class DirectoryViewRule( SimpleItem ):

    meta_type = "Directory View Rule"
    security = ClassSecurityInfo()
    
    manage_options = (
        
        {'label':'Settings',
         'action':'manage_settings'},
        
        )

    security.declareProtected(CMFCorePermissions.ManagePortal, ('manage_settings') )
    manage_settings = DTMLFile('ui/DirectoryViewRuleEditForm', globals())

    def __init__(self, id, view_path, source_path, deployment_path ):
        self.id = id
        self.view_path = view_path.strip()
        self.source_path = source_path.strip()
        self.deployment_path = deployment_path.strip()
        self.setTitle()
        
    def setTitle(self, *args):
        self.title = "%s -> %s -> %s"%( self.view_path,
                                                        self.source_path,
                                                        self.deployment_path )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def edit(self, view_path, source_path, deployment_path, RESPONSE=None):
        cdv = self.getParentNode()
        if not cdv.isValidDirectoryView( view_path.strip() ):
            raise InvalidDirectoryView("%s is not valid"%str(view_path)) 
        self.view_path = view_path.strip()
        self.source_path = source_path.strip()
        self.deployment_path = deployment_path.strip()
        self.setTitle()

        if RESPONSE is not None:
            cdv = self.getParentNode()
            return RESPONSE.redirect("%s/manage_main"%cdv.absolute_url())
        
InitializeClass( DirectoryViewRule )


class ContentDirectoryView(OrderedFolder):
    """
    implements merging of directory views into a deployment
    """

    meta_type = 'Content DirectoryView'

    security = ClassSecurityInfo()

    manage_options = (
        
        {'label':'Settings',
         'action':'manage_main'},

        {'label':'Policy',
         'action':'../overview'},

        )

    all_meta_types = (
        {'name':DirectoryViewRule.meta_type,
         'action':'addDirectoryViewRuleForm'},
         
        )

    #security.declareProtected(CMFCorePermissions.ManagePortal, 'directory_view_settings')
    #directory_view_settings = DTMLFile('ui/ContentDirectoryViewEditForm', globals())
    
    security.declareProtected(CMFCorePermissions.ManagePortal, 'addDirectoryViewRuleForm')    
    addDirectoryViewRuleForm = DTMLFile('ui/ContentDirectoryAddViewRuleEditForm', globals())
        
    def __init__(self, id):
        self.id = id

    security.declareProtected(CMFCorePermissions.ManagePortal, 'addDirectoryViewRule')
    def addDirectoryViewRule(self, id, view_path, source_path, deployment_path, RESPONSE=None):
        """
        add a directory view to the listing of deployable skin directories, after
        verifying the the view_path. 
        
        view_path - dv path relative to portal_skin
        deployment_path - path to deploy to relative to d. root
        source_path - the path that directory view appears relative to mount root,
           when doing uri resolution.
        """

        # XXX is this really nesc, i think not the functionality is self
        # contained to this module, we should allow deployments of the
        # view path multiple times, also needs mod in policy export.dtml
        view_path = view_path.strip()
        if self.isConflictingDirectoryView( view_path ):
            raise InvalidDirectoryView("View Path already exists")
        
        if not self.isValidDirectoryView( view_path ):
            raise InvalidDirectoryView("%s is not valid"%str(view_path))

        self._setObject( id,
                         DirectoryViewRule( id,
                                            view_path,
                                            source_path,
                                            deployment_path )
                         )

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getContentDirectoryViewMap')
    def getDirectoryViewMap(self):
        d = {}
        for dvr in self.objectValues():
            d[dvr.view_path] = ( dvr.source_path, dvr.deployment_path )
        return d

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editContentDirectoryViews')
    def editContentDirectoryViews(self, entries, RESPONSE=None):
        """
        edit the directory views
        """
        for e in entries:
            if self.isValidDirectoryView(e.view_path):
                if not (e.source_path.strip() and e.deploy_path.strip()):
                    del self._view_map[e.view_path.strip()]
                else:
                    self._view_map[e.view_path.strip()] = (e.source_path.strip(), e.deploy_path.strip())
            else:
                raise InvalidDirectoryView("%s is not valid"%str(e.view_path))
                
        if RESPONSE is not None:
            RESPONSE.redirect('directory_view_settings')
            
    security.declarePrivate('getContent')
    def getContent(self):
        """
        Get the content descriptors for the directory views.

        We explicitly setup descripitors with their content
        paths since we're remapping. the default content path
        is based on physical path relative to the deployment root.
        """
        res = []
        
        mp = self.getDeploymentPolicy().getContentOrganization().getActiveStructure().getCMFMountPoint()
        base_path = '/'.join(mp.getPhysicalPath())
        
        for dvr in self.objectValues():
            dv = self.getDirectoryView(dvr.view_path)
            content = dv.objectValues()
            source_path, deploy_path = dvr.source_path, dvr.deployment_path 

            uris = self.getDeploymentPolicy().getDeploymentURIs()
            vhost_path = uris.vhost_path
            
            # get rid of trailing and leading slashes and join to base path
            source_path = extend_relative_path(clstrip('/'.join( (vhost_path, base_path, '/'.join(filter(None, source_path.split('/'))))), '/'))
            deploy_path = '/'.join(filter(None, deploy_path.split('/')))
            
            for c in content:
                d = ContentDescriptor(c)
                d.setContentPath(deploy_path)
                d.setFileName(c.getId())
                # XXX reconsider some of this manip
                v = "%s/%s"%(source_path, c.getId())
                d.setSourcePath('/'.join(filter(None,v.split('/'))))
                d.setRenderMethod('')
                res.append(d)
                
        return res

    security.declarePrivate('isValidDirectoryView')
    def isValidDirectoryView(self, path):
        """
        check to see if path is a portal_skin relative path
        leading to a directory view or objectmanager.
        """
        skins = getToolByName(self, 'portal_skins')
        components = filter(None, path.split('/'))
        
        d = skins
        for c in components:
            if hasattr(aq_base(d), c):
                d = getattr(d, c)
            else:
                return 0
        if hasattr(aq_base(d), '_isDirectoryView'):
            return 1
        elif getattr(aq_base(d), 'isAnObjectManager'):
            return 1
        return 0

    security.declarePrivate('isConflictingDirectoryView')
    def isConflictingDirectoryView(self, view_path):
        """
        see adddirectory view for details
        """
        for dvr in self.objectValues():
            if dvr.view_path == view_path:
                return 1
        return 0

    security.declarePrivate('getDirectoryView')
    def getDirectoryView(self, path):
        """
        returns the directory view given by the portal skin
        relative 'path'
        """
        
        skins = getToolByName(self, 'portal_skins')
        components = filter(None, path.split('/'))

        d = skins
        for c in components:
            if hasattr(aq_base(d), c):
                d = getattr(d, c)
            else:
                raise InvalidDirectoryView(
                    "directory view does not exist %s of %s"%(c, path)
                    )
            
        assert not d is skins
        return d

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getSettings')
    def getSettings(self):
        return self._view_map.items()

    security.declarePrivate('mountDirectories')
    def mountDirectories(self, structure):
        """
        if a directory view is deployed onto a new directory
        in the deployment, it needs to be attached to the
        deployment structure. this amounts to a limited
        form of structure remapping.
        """
        
        for dvr in self.objectValues():
            components = filter(None, dvr.deployment_path.split('/'))
            
            if not components:
                continue # merging into root

            # for each of the components traverse from the structure
            # root directory, adding subdirs as needed.
            d = structure.getRootDirectory()
            
            for c in components:
                if hasattr(aq_base(d), c):
                    d = getattr(d, c)
                else:
                    d.addDirectory(c)

    security.declarePrivate('cookViewObject')
    def cookViewObject(self, descriptor):
        cook(self, descriptor)

InitializeClass(ContentDirectoryView)


    
    
_fs_cookers = {}

def fs_dtml_cooker(self, descriptor, object):

    if object.meta_type.startswith('Filesystem'):
        object._updateFromFS()
    
    security = getSecurityManager()
    security.addContext(self)

    portal = getToolByName(object, 'portal_url').getPortalObject()

    try:
        r = HTML.__call__(object, None, portal)
        descriptor.setRendered(r)
    finally:
        security.removeContext(self)

def fs_image_cooker(self, descriptor, object):

    descriptor.setBinary(1)
    descriptor.setRendered(object._data)

def fs_zpt_cooker(self, descriptor, object):

    descriptor.setRendered(object())

def fs_file_cooker(self, descriptor, object):

    suffix = object.content_type.split('/')[0]
    if suffix in ('image', 'audio', 'video'):
        descriptor.setBinary(1)
    descriptor.setRendered(object._readFile(0))

def file_cooker(self, descriptor, object):

    descriptor.setBinary(1)
    if isinstance(object.data, types.StringType):
        data = object.data
    else:
        data = str(object.data)
    descriptor.setRendered(data)


_fs_cookers['Filesystem Image'] = fs_image_cooker
_fs_cookers['Filesystem DTML Method'] = fs_dtml_cooker
_fs_cookers['Filesystem Page Template'] = fs_zpt_cooker
_fs_cookers['Filesystem File'] = fs_file_cooker
# for instance space directory views
_fs_cookers['Image'] = file_cooker
_fs_cookers['DTML Method'] = fs_dtml_cooker
_fs_cookers['Page Template'] = fs_zpt_cooker
_fs_cookers['File'] = file_cooker

def registerDVRenderer( meta_type, renderer ):
    _fs_cookers[ meta_type ] = renderer

def cook(self, descriptor):

    object = descriptor.getContent()

    global _fs_cookers
    mt = getattr(object, 'meta_type', None)
    render = _fs_cookers.get(mt)
    
    if render is None:
        descriptor.setGhost(1)
        log.warning("couldn't find cooker for %s meta_type for %s id"%(mt,object.getId()))
        return

    try:
        render(self, descriptor, object)
    except:
        log.warning("error while render skin object %s"%str(object.getPhysicalPath()))
        descriptor.setGhost(1)

    return
