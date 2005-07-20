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
Purpose: Normalize import of common jaunx
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id$
"""


from AccessControl import ClassSecurityInfo, Permissions, getSecurityManager
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
import App.Undo
from ComputedAttribute import ComputedAttribute
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile, package_home
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from OFS.OrderedFolder import OrderedFolder
from OFS.ObjectManager import ObjectManager, IFAwareObjectManager
from Products.CMFCore.utils import UniqueObject, SimpleItemWithProperties, getToolByName
from Products.CMFCore import CMFCorePermissions

from Interface import Base as Interface
from ZODB.PersistentMapping import PersistentMapping


