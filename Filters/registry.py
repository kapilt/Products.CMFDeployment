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
Purpose: Filter Registry
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id: $
"""
import inspect

_filter_scripts = {}

class InvalidFilter(Exception): pass

def listFilters():
    return _filter_scripts.keys()

def registerFilter(name, filter):

    argspec = inspect.getargspec(filter)

    if not len(argspec[0]) == 3:
        raise InvalidFilter("invalid filter, wrong signature")
    if _filter_scripts.has_key(name):
        raise InvalidFilter("filter with %s already exists"%name)
    
    _filter_scripts[name] = filter

def getFilter(name):
    # raises GetItemError if not found
    return _filter_scripts[name]

    
