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
Purpose: Renders Content For Deployment
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id: $
"""

from Namespace import *

from DeploymentExceptions import InvalidSkinName
from MimeMapping import MimeMappingContainer, getMimeExprContext
from utils import file2string

from Log import LogFactory

log = LogFactory('Mastering')

class ContentMastering(Folder):

    meta_type = 'Content Mastering' 

    manage_options = (

        {'label':'Overview',
         'action':'overview'},
        
        {'label':'Skin',
         'action':'skin'},

        {'label':'User',
         'action':'user'},

        {'label':'MimeMapping',
         'action':'mime/manage_main'},        

        {'label':'Policy',
         'action':'../overview'}

        )

    overview = DTMLFile('ui/ContentMasteringOverview', globals())
    skin     = DTMLFile('ui/ContentMasteringSkin', globals())
    root     = DTMLFile('ui/ContentMasteringRoot', globals())
    user     = DTMLFile('ui/ContentMasteringUser', globals())
    
    def __init__(self, id):
        
        self.id = id
        self.skn_name = None

    def editRoot(self, enable, server, server_path, port, protocol, RESPONSE=None):
        """ """
        
        self.site_root.edit(enable, server, server_path, protocol, port)

        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    def editSkin(self, enable, skin_name, RESPONSE=None):
        """ """
        
        skin_tool = getToolByName(self, 'portal_skins')
        skin = skin_tool.getSkinByName(skin_name.strip())
        
        if skin is None:
            raise InvalidSkinName("%s is not a valid skin"%str(skin_name))

        self.site_skin.edit(enable, skin_name)

        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    def editUser(self, enable, user, udb_path, RESPONSE=None):
        """ """

        self.site_user.edit(enable, user, udb_path)

        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    def manage_afterAdd(self, item, container):

        ob = MimeMappingContainer('mime')
        self._setObject('mime', ob)

        ob = SiteChainUser()
        self._setObject('site_user', ob)

        ob = SiteChainSkin()
        self._setObject('site_skin', ob)

    #################################
    def prepare(self, descriptor):
        """
        prepare a descriptor for deployment by finding and applying a
        deployment/content/mime rule for it.
        """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        c = descriptor.getContent()
        ctx = getMimeExprContext(c, portal) 
        mappings = self.mime.objectValues()
        for m in mappings:
            if m.isValid(descriptor, ctx):
                m.process( descriptor, ctx )
                return True
        log.debug('no mime mapping (%s)->(%s)'%(str(c.portal_type), descriptor.content_url))
        return None

    def cook(self, descriptor):
        """
        render the contents of a descriptor and its child descriptors
        """

        if descriptor.isGhost():
            return

        # get child descriptors if any
        descriptors = descriptor.getDescriptors()

        for descriptor in descriptors:
            self.renderContent( descriptor )

    def renderContent( self, descriptor ):
            
        c = descriptor.getContent()
        vm = descriptor.getRenderMethod()

        if vm is None: # XXX redundant
            descriptor.setGhost(1)
            return
        
        render = getattr(c, vm, None) or getattr(c, '__call__', None)
                                                 
        if render is None:
            try:
                log.error(" couldn't find render method for %s"%( str(descriptor.content_url), str(c.getPortalTypeName()) ))
            except Exception, e:
                print e
                      
        # this is just a tad verbose..
        #log.debug('rendering %s %s %s'%(c.getId(), vm, str(render)))

        try: 
            if getattr(aq_base(render), 'isDocTemp', 0):
                descriptor.setRendered(apply(render, (self, self.REQUEST)))
            elif hasattr(aq_base(c), 'precondition'): # test if its a file object
                descriptor.setRendered(file2string(c))
                descriptor.setBinary(1)
            else:
                descriptor.setRendered(render())
        except:
            log.error('Error While Rendering %s'%(str(c.getPhysicalPath())))
            descriptor.setGhost(1) # ghostify it        

    #################################
    def setup(self):
        #self.site_root.lock()
        self.site_skin.lock()
        self.site_user.lock()
        
    def tearDown(self):
        #self.site_root.unlock()
        self.site_skin.unlock()
        self.site_user.unlock()


class SiteChainSkin(SimpleItem):
    """

    changes the skin mid request,

    """

    meta_type = 'Site Chain Skin'
    id = 'site_skin'
    
    _v_active = None
    _v_saved_skin_data = None

    enable = 1    
    
    def __init__(self):
        self.skin_name = None 

    def edit(self, enable, skin_name):
        
        self.enable = not not int(enable)
        self.skin_name = skin_name

    def lock(self):

        if not self.enable or self._v_active or not self.skin_name:
            log.debug('deployment skin not enabled')
            return

        portal = getToolByName(self, 'portal_url').getPortalObject()
        skins  = getToolByName(self, 'portal_skins')
        
        req = getattr(self, 'REQUEST', {})
        self._v_saved_skin_data = portal._v_skindata
        portal._v_skindata = (req,
                              skins.getSkinByName(self.skin_name),
                              {})
        self._v_active = 1
        
    def unlock(self):

        if not self._v_active:
            return

        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal._v_skindata = self._v_saved_skin_data

        self._v_saved_skin_data = None
        self._v_active = None
        
    def manage_afterAdd(self, item, container):
        self.skin_name  = getToolByName(self, 'portal_skins').getDefaultSkin()	

class InvalidUserDatabase(AttributeError): pass

class SiteChainUser(SimpleItem):
    """
    sign on a user during the course of a request.
    this user will be used during the mastering process.
    """

    meta_type = 'Site Chain User'
    id = 'site_user'
    enable = 0
    userid = None
    udb_path = None
    
    def edit(self, enable, user, udb_path):
        
        self.enable = not not enable        
        self.userid = user
        
        try:
            udb = self.unrestrictedTraverse(udb_path)
            assert udb.id == 'acl_users'
        except:
            raise InvalidUserDatabase(" invalid user database ")
        
        self.udb_path = udb_path
        
    def lock(self):

        if not self.enable or not self.userid or not self.udb_path:
            log.debug('not chaining user')
            return
        
        from AccessControl import User
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SpecialUsers import system

        # we can restore the existing user latter if need be, we don't for now.
        current_user = getSecurityManager().getUser()
        current_udb_path  = aq_parent(aq_inner(current_user)).getPhysicalPath()
        current_userid = current_user.getId()

        # get the new user
        udb = self.unrestrictedTraverse(self.udb_path)
        user = udb.getUser(self.userid).__of__(udb)

        # sign on the new user
        try: req = self.REQUEST
        except: req = None
        newSecurityManager(req, user) 
        
    def unlock(self):
        pass

            
