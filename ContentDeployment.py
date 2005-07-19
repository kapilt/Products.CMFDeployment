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
Purpose: Defines Mechanisms and Data needed
         to transport content from zope server
         fs to deployment target(s).

Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id$
"""

from Namespace import *
from DeploymentInterfaces import *
from DeploymentExceptions import *
from Protocols import getProtocolNames, getProtocol

class DeploymentTarget(SimpleItem):

    __implements__ = IDeploymentTarget

    meta_type = 'Deployment Target'
    
    security = ClassSecurityInfo()
    
    manage_options = (
        
        {'label':'Settings',
         'action':'deployment_settings'},

        {'label':'Targets',
         'action':'../manage_main'},

        {'label':'Policy',
         'action':'../overview'},

        {'label':'Tool',
         'action':'../../overview'}
        )

    deployment_settings = DTMLFile('ui/DeploymentTargetSettingsForm', globals())

    def __init__(self, id):
        self.id = id
        self._user = None
        self._password = None
        self.host = None
        self.protocol = None

    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def edit(self,
             user,
             password,
             password_confirm,
             host,
             protocol,
             remote_directory,
             RESPONSE=None):
        """ """
        self._user = user
        
        if password and password_confirm == password:
            self._password = password
        elif password:
            raise CredentialError(" passwords do not match ")

        self.host = host.strip()

        if not protocol in getProtocolNames():
            raise ProtocolError(" Invalid Protocol %s"%protocol)

        self.protocol = protocol
        self.remote_directory = remote_directory.strip()

        if RESPONSE is not None:
            RESPONSE.redirect('deployment_settings')

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getUser')
    def getUser(self):
        return self._user

    # XXX fs dtml can access this
    #security.declarePrivate('getPassword')
    #def getPassword(self):
    #    return self._password

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getHost')
    def getHost(self):
        return self.host

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getProtocol')
    def getProtocol(self):
        return getProtocol(self.protocol)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getDirectory')
    def getDirectory(self):
        return self.remote_directory


class ContentDeployment(Folder):

    meta_type = 'Content Deployment'

    manage_options = (

        {'label':'Overview',
        'action':'overview'},

        {'label':'Targets',
         'action':'manage_main'},

        {'label':'Policy',
         'action':'../overview'},
        
        )

    overview = DTMLFile('ui/ContentDeploymentOverview', globals())
    addDeploymentTargetForm = DTMLFile('ui/DeploymentTargetAddForm', globals())
    
    all_meta_types = (
        {'name':DeploymentTarget.meta_type,
         'action':'addDeploymentTargetForm'},
         
        )

    def __init__(self, id):
        self.id = id

    def addDeploymentTarget(self,
                            id,                            
                            user,
                            password,
                            password_confirm,
                            host,
                            remote_directory,
                            protocol,
                            RESPONSE=None):
        """ """
        ob = DeploymentTarget(id)
        self._setObject(id, ob)
        ob = self._getOb(id)
        ob.edit(user, password, password_confirm, host, protocol, remote_directory)

        if RESPONSE is not None:
            RESPONSE.redirect("%s/manage_workspace"%id)

    def getProtocolTypes(self):
        return getProtocolNames()
        
    def deploy(self, structure):
        for target in self.objectValues('Deployment Target'):
            protocol = target.getProtocol()
            protocol.execute(target, structure)

    
## moved to Protocols package
