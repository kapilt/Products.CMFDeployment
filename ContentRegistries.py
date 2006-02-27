##################################################################
#
# (C) Copyright 2006 Kapil Thangavelu <k_vertigo@objectrealms.net>
#                    Gael Le Mignot <gael@pilotsystems.net>
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
    
implements merging of registries into a deployment

Author: Gael Le Mignot <gael@pilotsystems.net>
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

from DeploymentExceptions import InvalidRegistry

from ContentDirectoryViews import DirectoryViewRule, ContentDirectoryView

try:
    from Products.ResourceRegistries.tools.BaseRegistry import BaseRegistryTool
    HAS_REGISTRY = True
except ImportError:
    # We need to be plone 2.0 compliant, too
    BaseRegistryTool = None
    HAS_REGISTRY = False 

log = LogFactory('Registries')

class RegistryRule( DirectoryViewRule ):

    meta_type = "Registry Rule"
    security = ClassSecurityInfo()
    
    security.declareProtected(CMFCorePermissions.ManagePortal, ('manage_settings') )
    manage_settings = DTMLFile('ui/RegistryRuleEditForm', globals())
        
InitializeClass( RegistryRule )


class ContentRegistry(ContentDirectoryView):
    """
    implements merging of registries into a deployment
    """

    meta_type = 'Content Registry'

    security = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'addRegistryRuleForm')    
    Addregistryruleform = DTMLFile('ui/ContentDirectoryAddViewRuleEditForm', globals())
        
    security.declareProtected(CMFCorePermissions.ManagePortal, 'addRegistryRule')
    def addRegistryRule(self, id, view_path, source_path, deployment_path, RESPONSE=None):
        """
        add a registry to the listing of deployable registries, after
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
        if self.isConflictingRegistry( view_path ):
            raise InvalidRegistry("View Path already exists")
        
        if not self.isValidRegistry( view_path ):
            raise InvalidRegistry("%s is not valid"%str(view_path))

        self._setObject( id,
                         RegistryRule( id,
                                            view_path,
                                            source_path,
                                            deployment_path )
                         )

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getContentRegistryMap')
    def getRegistryMap(self):
        d = {}
        for rr in self.objectValues():
            d[rr.view_path] = ( rr.source_path, rr.deployment_path )
        return d

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editContentRegistries')
    def editContentRegistries(self, entries, RESPONSE=None):
        """
        edit the directory views
        """
        for e in entries:
            if self.isValidRegistry(e.view_path):
                if not (e.source_path.strip() and e.deploy_path.strip()):
                    del self._view_map[e.view_path.strip()]
                else:
                    self._view_map[e.view_path.strip()] = (e.source_path.strip(), e.deploy_path.strip())
            else:
                raise InvalidRegistry("%s is not valid"%str(e.view_path))
                
        if RESPONSE is not None:
            RESPONSE.redirect('directory_view_settings')
            
    security.declarePrivate('getContent')
    def getContent(self):
        """
        Get the content descriptors for the registry.

        We explicitly setup descripitors with their content
        paths since we're remapping. the default content path
        is based on physical path relative to the deployment root.
        """
        res = []

        mp = self.getDeploymentPolicy().getContentOrganization().getActiveStructure().getCMFMountPoint()
        base_path = '/'.join(mp.getPhysicalPath())
        
        for rr in self.objectValues():
            r = self.getRegistry(rr.view_path)
            content = r.getEvaluatedResources(self)
            source_path, deploy_path = rr.source_path, rr.deployment_path 

            uris = self.getDeploymentPolicy().getDeploymentURIs()
            vhost_path = uris.vhost_path
            
            # get rid of trailing and leading slashes and join to base path
            source_path = extend_relative_path(clstrip('/'.join( (vhost_path, base_path, '/'.join(filter(None, source_path.split('/'))))), '/'))
            deploy_path = '/'.join(filter(None, deploy_path.split('/')))

            # XXX the escaping seems weak.. - use a std lib func, and allow for multiple source paths.
            skin_name = self.getCurrentSkinName().replace(' ', '%20')
            
            for c in content:
                inline = getattr(c, "getInline", None) and c.getInline() or False
                if inline:
                    continue
                d = ContentDescriptor(c)
                c.registry = r
                d.setContentPath(deploy_path)
                d.setFileName(c.getId())
                
                v = "%s/%s/%s"%(source_path, skin_name, c.getId())
                d.setSourcePath('/'.join(filter(None,v.split('/'))))
                d.setRenderMethod('')
                
                res.append(d)
                
        return res

    security.declarePrivate('isValidRegistry')
    def isValidRegistry(self, path):
        """
        check to see if path is a portal_skin relative path
        leading to a directory view or objectmanager.
        """
        root = getToolByName(self, 'portal_url').getPortalObject()
        components = filter(None, path.split('/'))
        
        d = root
        for c in components:
            if hasattr(aq_base(d), c):
                d = getattr(d, c)
            else:
                return 0
        if isinstance(aq_base(d), BaseRegistryTool):
            return 1
        return 0

    security.declarePrivate('isConflictingRegistry')
    def isConflictingRegistry(self, view_path):
        """
        see adddirectory view for details
        """
        for rr in self.objectValues():
            if rr.view_path == view_path:
                return 1
        return 0

    security.declarePrivate('getRegistry')
    def getRegistry(self, path):
        """
        returns the registry given by the portal root
        relative 'path'
        """
        
        root = getToolByName(self, 'portal_url').getPortalObject()
        components = filter(None, path.split('/'))

        d = root
        for c in components:
            if hasattr(aq_base(d), c):
                d = getattr(d, c)
            else:
                raise InvalidRegistry(
                    "registry does not exist %s of %s"%(c, path)
                    )
            
        return d

    security.declarePrivate('cookRegistryObject')
    def cookRegistryObject(self, descriptor):
        obj = descriptor.getContent()
        registry = obj.registry.__of__(self)
        rendered, content_type = registry[ obj.getId() ]
        descriptor.setRendered( rendered )
    


InitializeClass(ContentRegistry)
