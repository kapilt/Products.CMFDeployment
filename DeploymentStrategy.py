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
Purpose: Facade to aggregate the different pluggable strategies behind
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
License: GPL
Created: 8/10/2002
CVS: $Id: DeploymentStrategy.py,v 1.3 2003/02/28 05:03:21 k_vertigo Exp $
"""

import pprint

from Namespace import *
from Statistics import TimeStatistics, MemoryStatistics
from ContentStorage import ContentStorage
from URIResolver import URIResolver
from Log import LogFactory
from Descriptor import ContentDescriptor

from Strategies import getStrategyNames, getStrategy

log = LogFactory('Strategy')

class DeploymentStrategy(SimpleItem):

    meta_type = 'Deployment Strategy'

    default_strategy = 'default'

    manage_options = (

        { 'label':'Settings',
          'action':'deployment_strategy_overview' },

        { 'label':'Policy',
          'action':'../../manage_workspace'}
        )

    security = ClassSecurityInfo()

    deployment_strategy_overview = DTMLFile('ui/DeploymentStrategyOverview', globals())
    
    def __init__(self, id):
        self.id =id
        self.strategy_id = None

    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def setStrategy(self, strategy_id='', RESPONSE=None):
        """ """
        if strategy_id in getStrategyNames():
            self.strategy_id = strategy_id

        if RESPONSE:
            RESPONSE.redirect('deployment_strategy_overview')

    security.declarePrivate('getStrategy')
    def getStrategy(self):
        
        strategy_id = self.strategy_id or self.default_strategy
        return getStrategy(strategy_id)
        
InitializeClass(DeploymentStrategy)    

