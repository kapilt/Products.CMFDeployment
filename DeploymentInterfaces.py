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
Purpose: interfaces for the deployment system
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
License: GPL
Created: 8/10/2002
$Id: $
"""

from Interface import Base as Interface

class ICredentials(Interface):

    def getUser():
        """
        return the user name for this cred.
        """

    def getPassword():
        """
        return the password for this cred.
        """

class IHost(Interface):

    def getHost():
        """
        return a FQDN or ip
        """

class IDeploymentProtocol(Interface):
    """ represents a transport protocol """

    def execute(self, target, structure):
        """
        deploy structure to target
        """

class IDeploymentTarget(ICredentials, IHost):


    def getDirectory():
        """
        target directory
        """

    def getProtocol():
        """
        return the protocol to be used with
        this object
        """

class IContentDeployment(Interface):

    def deploy(structure):
        """
        use structure to deploy against each target
        """
    

class IContentIdentification(Interface):

    def getContent():
        """
        return the content that has been
        identified for deployment
        """

class IContentSource(Interface):

    def getContent():
        """
        returns a lazy sequence of content
        to be considered for deployment.
        realistically, these should be brains,
        exhibiting catalog metadata and a getObject
        method ;-) this is a bad interface ...
        """

class IContentFilter(Interface):

    def filter(content):
        """
        return boolean, true and the content
        continues through the filter chain
        """

class IDeploymentPolicy(Interface):


    def getContentIdentification():
        """
        return the component that
        handles identification of
        content that will be deployed
        """
        
    def getContentOrganization():
        """
        return the component that handles
        organizing content for deployment.
        """

    def getContentMastering():
        """
        return the component that handles
        cooking the content for the target
        deployment
        """

    def getContentDeployment():
        """
        return the component that handles
        deploying content to the target
        systems
        """

    def getDeploymentPolicy():
        """
        return the deployment policy
        """

    def execute():
        """
        execute the policy, see documentation
        for more information on the various
        stages of execution
        """

    def setActive(active_flag):
        """
        makes the policy and active and therefore
        executable
        """

    def isActive():
        """
        deactivate this policy
        """
