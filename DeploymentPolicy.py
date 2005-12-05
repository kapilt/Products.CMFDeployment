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
Purpose: Organizes Content in a Deployment Target Structure
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id$
"""

import DefaultConfiguration
import DeploymentStrategy
import Log

from Namespace import *
from Descriptor import ContentDescriptor
from ComputedAttribute import ComputedAttribute
from DeploymentInterfaces import IDeploymentPolicy
from Products.CMFCore.utils import getToolByName

class DeploymentPolicy(Folder):

    meta_type = 'Deployment Policy'

    __implements__ = IDeploymentPolicy

    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.ManagePortal)

    manage_options = (

        {'label':'overview',
         'action':'overview'},
        
        {'label':'Identification',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentIdentification},

        {'label':'Organization',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentOrganization},

        {'label':'Skins',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentDirectoryViews},

        {'label':'URIs',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentURIs},

        {'label':'Templating',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentMastering},

        {'label':'Deployment', 
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentDeployment},

        {'label':'Transforms',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentTransforms},
        
        {'label':'Strategies',
         'action':'%s/manage_workspace'%DefaultConfiguration.DeploymentStrategy},

        {'label':'History',
         'action':'%s/manage_workspace'%DefaultConfiguration.DeploymentHistory},
        
        ) 

    overview = DTMLFile('ui/PolicyOverview', globals())

    identification = DTMLFile('ui/ContentIdentification', globals())
    _active = 1
    policy_xml = DTMLFile('ui/PolicyExport', globals())

    icon = 'misc_/CMFDeployment/policy.png'
    
    def __init__(self, id):
        self.id = id 

    def getContentIdentification(self):
        return self._getOb(DefaultConfiguration.ContentIdentification)

    def getContentOrganization(self):
        return self._getOb(DefaultConfiguration.ContentOrganization)

    def getContentMastering(self):
        return self._getOb(DefaultConfiguration.ContentMastering)

    def getContentDeployment(self):
        return self._getOb(DefaultConfiguration.ContentDeployment)

    def getContentDirectoryViews(self):
        return self._getOb(DefaultConfiguration.ContentDirectoryViews)

    def getContentTransforms(self):
        return self._getOb(DefaultConfiguration.ContentTransforms)

    def getContentSources( self ):
        return self.getContentIdentification().sources

    def getContentRules( self ):
        return self.getContentMastering().mime
        
    def getContentMap( self ):
        return self._getOb(DefaultConfiguration.ContentMap)
    
    def getDependencySource( self ):
        return self.getContentSources().dependency_source
        
    def getDeletionSource( self ):
        return self._getOb(DefaultConfiguration.DeletionSource)
    
    def getDeploymentHistory(self):
        return self._getOb(DefaultConfiguration.DeploymentHistory)

    def getDeploymentStrategy(self):
        return self._getOb(DefaultConfiguration.DeploymentStrategy)

    def getDeploymentURIs(self):
        return self._getOb(DefaultConfiguration.ContentURIs)

    def getDeploymentPolicy(self):
        return self

    def setActive(self, flag, RESPONSE=None):
        self._active = not not flag
        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    def isActive(self):
        return self._active

    def execute(self, RESPONSE=None):
        """ """
        if not self.isActive():
            return

        histories = self.getDeploymentHistory()
        history = histories.makeHistory()
    
        Log.attachLogMonitor(history)
        
        try:
            try:
                strategy = self.getDeploymentStrategy().getStrategy()
                display = strategy(self)
            except:
                import sys, pdb
                ec, e, tb = sys.exc_info()
                print ec, e
                pdb.post_mortem( tb )
        finally:
            Log.detachLogMonitor(history)

        history.recordStatistics(display)
        history.update_last_modification_time()
        histories.attachHistory(history)
        
        if RESPONSE:
            return "<html><pre>%s</pre></body</html>"%display
        return True

    def manage_afterAdd(self, item, container):
        catalog_tool = getToolByName(self, "portal_catalog")
        policy_id = self.getId()
        catalog_tool.manage_addIndex(policy_id+'_incremental_idx', 'PolicyIncrementalIndex', self.id)
        catalog_tool.manage_addColumn(policy_id+'_incremental_idx')
        
        import DefaultConfiguration
        DefaultConfiguration.install(self)
    
InitializeClass(DeploymentPolicy)
