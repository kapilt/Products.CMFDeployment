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
Purpose: Transfer Deployed Content to Deployment Server
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 9/10/2002
$Id$
"""

from Products.CMFDeployment.DeploymentInterfaces import IDeploymentProtocol
from Products.CMFDeployment.lib import pexpect
from Products.CMFDeployment.DeploymentExceptions import ProtocolError
from cStringIO import StringIO



class RsyncSshProtocol(object):

    __implements__ = IDeploymentProtocol

    def execute(self, target, structure):
        
        host = target.getHost()
        user = target.getUser()
        pass_ = target._password
        local_directory = structure.getMountPoint()
        remote_directory = target.getDirectory()

        #################################
        command = "rsync"

        short_noarg_options = [
            "a", # archive mode
            "z", # compress
            "t", # preserve mod times
            "q", # quiet
            "C", # ignore cvs files
            #"r", # recurse
            #"p", # preserve permissions
            #"u", # update, don't overwrite new files, i don't need this
            ]

        short_arg_options = [("e", "ssh")]

        # mainly aggressive deletion options
        # for retraction. Also some partial options
        long_options = [
            "--delete", # delete files which don't exist on the sender
            #"--ignore-existing", #ignore files that already exist on the reciever
            #"--existing", # only update files that already exist
            #"--delete-after", # delete after transferring files
            #"--ignore-errors"  # delete even if errors in transfer
            #"--force",  # force deletion of non empty dirs

            ]

        short = "-%s"%''.join(short_noarg_options)
        short_arg_list = []
        for k, v in short_arg_options:
            short_arg_list.append('-%s %s' % (k, v))
        short_arg = ' '.join(short_arg_list)
        long_options = "%s"%' '.join(long_options)
        all_options = ' '.join( (short, short_arg, long_options) )
        #################################
        

        rendered_command = "%s %s %s %s"%(
            command,
            all_options,
            local_directory,
            "%s@%s:%s"%( user, host, remote_directory)
            )

        log = StringIO()
        conn = pexpect.spawn(rendered_command)
        conn.setlog(log)
        try:
            conn.expect_exact(['password:', 'Enter passphrase'])
        except pexpect.EOF:
            conn.kill(1)
            log.seek(0)
            raise ProtocolError, log.read()
        conn.sendline(pass_)
        conn.expect(pexpect.EOF, 30) # 30 s timeout
        
        if conn.isalive():
            conn.kill(1)

        if conn.exitstatus != 0:
            log.seek(0)
            raise ProtocolError, log.read()
