##################################################################
#
# (C) Copyright 2002-2006 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
Purpose: Mime Mappings are used to map extensions onto content objects
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id$
"""

from Namespace import *
from DeploymentInterfaces import IContentRule

class MimeMappingContainer(OrderedFolder):

    meta_type = 'Mime Mapping Container'

    manage_options = (

        {'label':'Mappings',
         'action':'manage_main'},

        {'label':'Mastering',
         'action':'../overview'},        

        {'label':'Policy',
         'action':'../../overview'}
        )

    _product_interfaces = ( IContentRule, )
    
    def __init__(self, id, title=''):
        self.id = id
        self.title = title or id

    def all_meta_types(self):
        """Delegate the call passing our allowed interfaces"""
        return OrderedFolder.all_meta_types(self, interfaces=self._product_interfaces)
        
    def addMimeMapping(self, *args, **kw):
        return self.manage_addProduct['CMFDeployment'].addContentRule(*args, **kw)

    def addContentRule(self, *args, **kw):
        return self.manage_addProduct['CMFDeployment'].addContentRule(*args, **kw)


InitializeClass( MimeMappingContainer )    
