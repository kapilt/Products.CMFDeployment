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
Purpose: utilize ordered folder if available to provide for
          explicit ordering of expressions (filter, mime).
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003          
$Id: $
"""

try:
    from Products.OrderedFolder.OrderedFolder import OrderedFolder
except:
    from OFS.Folder import Folder as OrderedFolder

class ExpressionContainer(OrderedFolder):
    pass
