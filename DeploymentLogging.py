##################################################################
#
# (C) Copyright 2002 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
XXX THIS IS DISABLED
Purpose: ttw configured component logging
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2003
License: GPL
Created: 1/3/2003
CVS: $Id: DeploymentLogging.py,v 1.2 2003/02/28 05:03:21 k_vertigo Exp $
"""

import Log

from Namespace import *
from Products.CMFCore import CMFCorePermissions

class DeploymentLogging(SimpleItem):
    
    meta_type = 'Deployment Logging'

    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.ManagePortal)

    config_form = DTMLFile('ui/LoggingConfigurationForm', globals())

    manage_options = (

        { 'label':'Settings',
          'action':'config_form' },

        { 'label':'Policy',
          'action':'../manage_workspace'}
        )


    def __init__(self, id):
        self.id = id
        self._config = {}
        
    def editLogConfiguration(self, entries, RESPONSE=None):
        """ """
        for e in entries:
            component_name = e.get('name', '')
            record_p = int(e.get('record_p', 0))
            zlog_p = int(e.get('zlog_p', 0))
            self._config[component_name] = ( record_p, zlog)
            
        self._p_changed = 1
        
        if RESPONSE is not None:
            RESPONSE.redirect('./config_form')

    def getLogConfigurationEntries(self):
        res = []        
        for rc in Log.getRegisteredComponents():
            #print rc
            res.append( (res, Log.configuration.getConfigurationFor(rc)))
        return res

    security.declarePrivate('initializeLogging')
    def initializeLogging(self):
        for component_name in self._config.keys():
            record_p, zlog_p = self._config.get(component_name, (0,0))
            Log.configuration.setConfigurationEntry(component_name, record_p, zlog_p)

InitializeClass(DeploymentLogging)            
