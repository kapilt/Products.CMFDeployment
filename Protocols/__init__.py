##################################################################
#
# (C) Copyright 2002 Kapil Thangavelu <kvthan@wm.edu>
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
Purpose: Transfer Deployed Content to Deployment Server
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
License: GPL
Created: 9/10/2002
CVS: $Id: __init__.py,v 1.2 2003/01/09 07:58:59 k_vertigo Exp $
"""
# deployment protocol implementation directory

#################################
# simple global protocol registry    

_protocols = {}
def registerProtocol(name, protocol):
    global _protocols
    _protocols[name]=protocol

def getProtocolNames(context=None):
    global _protocols
    return _protocols.keys()

def getProtocol(name):
    global _protocols
    return _protocols[name]()

#################################
# protocol implementation

import RsyncSSH

registerProtocol('rsync_ssh', RsyncSSH)
