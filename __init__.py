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
Purpose: Initialize and Register the Deployment Tool
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
License: GPL
Created: 8/10/2002
CVS: $Id: __init__.py,v 1.4 2003/02/28 05:03:22 k_vertigo Exp $
"""

import DeploymentTool
import utils
from Products.CMFCore.utils import ToolInit

tools = (DeploymentTool.DeploymentTool,)

import ContentOrganization
import ContentMastering
import ContentDeployment
import ContentIdentification
import DeploymentStrategy
import Descriptor

methods = {
    'ContentDeploymentProtocolIds':ContentDeployment.getProtocolNames,
    'ContentDeploymentStrategyIds':DeploymentStrategy.getStrategyNames
    }

def initialize(context):

    ToolInit('CMF Deployment',
             tools=tools,
             product_name='CMFDeployment',
             icon='tool.png').initialize(context)

    utils.registerIcon('policy.png')
    utils.registerIcon('identify.png')
    utils.registerIcon('protocol.png')     

    context.registerHelp()
     
