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
import Log
import pipeline

from Namespace import *
from DeploymentInterfaces import IDeploymentPolicy

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
        
        {'label':'History',
         'action':'%s/manage_workspace'%DefaultConfiguration.DeploymentHistory},
        
        ) 

    overview = DTMLFile('ui/PolicyOverview', globals())

    identification = DTMLFile('ui/ContentIdentification', globals())
    _active = 1
    policy_xml = DTMLFile('ui/PolicyExport', globals())

    icon = 'misc_/CMFDeployment/policy.png'
    
    def __init__(self, id, title, pipeline_id):
        self.id = id
        self.title = title
        self.pipeline_id = pipeline_id

        assert pipeline_id in pipeline.getPipelineNames(), "invalid pipeline"

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
    
    def getDeploymentHistory(self):
        return self._getOb(DefaultConfiguration.DeploymentHistory)

    def getDeploymentURIs(self):
        return self._getOb(DefaultConfiguration.ContentURIs)

    def getDeploymentPolicy(self):
        return self

    security.declarePrivate('getPipeline')
    def getPipeline(self):
        factory = pipeline.getPipeline( self.pipeline_id )
        deployment_pipeline = factory()
        return deployment_pipeline

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
                pipeline = self.getPipeline()
                pipeline.process( self )
            except:
                import sys, pdb, traceback
                ec, e, tb = sys.exc_info()
                print ec, e
                print traceback.print_tb( tb )
                pdb.post_mortem( tb )
                raise e
        finally:
            Log.detachLogMonitor(history)

        #history.recordStatistics(display)
        histories.attachHistory(history)

        if RESPONSE:
            return "<html><pre>deployed</pre></body</html>"
        return True

    def manage_afterAdd(self, item, container):
        import DefaultConfiguration
        DefaultConfiguration.install(self)

        factory = pipeline.getPipeline( self.pipeline_id )
        factory.finishPolicyConstruction( self )

    def manage_beforeDelete(self, *args):

        factory = pipeline.getPipeline( self.pipeline_id )
        factory.beginPolicyRemoval( self )
        
    
InitializeClass(DeploymentPolicy)
    

