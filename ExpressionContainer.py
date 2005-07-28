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
Author: kapil thangavelu <k_vertigo@objectrealms.net> 
$Id$
"""

from OFS.OrderedFolder import OrderedFolder
from Products.PageTemplates.Expressions import SecureModuleImporter, getEngine

from Namespace import Implicit, ClassSecurityInfo, InitializeClass


class ExpressionContainer(OrderedFolder):
    pass

def getDeployExprContext(object, portal):
    
    data = {
        'object':       object,
        'portal':       portal,
        'nothing':      None,
        'request':      getattr( object, 'REQUEST', None ),
        'modules':      SecureModuleImporter,
        'deploy':       DeploymentMimeUtilities.__of__(object)
        }

    return getEngine().getContext(data)    
    
class MimeUtilities(Implicit):

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    
    __allow_access_to_unprotected_subobjects__ = 1

    def has_index(self, obj):
        return not not getattr(aq_base(obj), 'index_html', None)


InitializeClass(MimeUtilities)
DeploymentMimeUtilities = MimeUtilities()

def registerDeploymentExprMethod(name, context_method):
    assert isinstance(name, str)
    assert not _MimeUtilities.__dict__.has_key(name),"duplicate registration %s"%name           
    _MimeUtilities.__dict__[name]=context_method
