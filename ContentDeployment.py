##################################################################
#
# (C) Copyright 2002-2005 Kapil Thangavelu <k_vertigo@objectrealms.net>
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


#################################
# container for pluggable transports

class ContentDeployment( OrderedFolder ):

    meta_type = 'Content Deployment'

    manage_options = (

        {'label':'Targets',
         'action':'manage_main'},

        {'label':'Overview',
         'action':'overview'},
        
        ) + App.Undo.UndoSupport.manage_options

    overview = DTMLFile('ui/ContentDeploymentOverview', globals())
    
    all_meta_types = IFAwareObjectManager.all_meta_types
    _product_interfaces = ( IDeploymentTarget, )

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    def getProtocolTypes(self):
        return getProtocolNames()

    security.declarePrivate('deploy')
    def deploy(self, structure):
        for target in self.objectValues('Deployment Target'):
            target.transport( structure )

InitializeClass( ContentDeployment )


#################################
# all transports/protocols/thingies moved to transport package
