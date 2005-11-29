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

Purpose: Simple History storage... to be expanded
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
$Id$

"""
from Namespace import *
from time import time
from BTrees.OIBTree import OISet
from BTrees.Length import Length

class DeploymentHistoryContainer(Folder):

    all_meta_types = ()
    
    meta_type = 'Deployment History Container'

    manage_options = (
        
        {'label':'History',
         'action':'history_overview'},

        {'label':'Policy',
         'action':'../overview'},
        )

    security = ClassSecurityInfo()

    history_overview = DTMLFile('ui/DeploymentHistoryOverview', globals())

    def __init__(self, id):
        self.id = id
        self._records = OISet()
        self._record_length = Length(0)

    #security.declarePrivate('addHistory')
    #def addHistory(self):
    #    h = DeploymentHistory( str(self._record_length()) )
    #    self._records.insert(h)
    #    self._record_length.change(1)
    #    return h

    security.declarePrivate('attachHistory')
    def attachHistory(self, history):
        hid = str(self._record_length())
        history.id = hid
        self._records.insert(history)
        self._record_length.change(1)
        print "DeploymentHistory: attachHistory: ", self._records
        if self._record_length() > 0:
            print "time du 2: ", self._records[0].bobobase_modification_time()
        if self._record_length() > 1:
            print "time du 1: ", self._records[1].bobobase_modification_time()
        if self._record_length() > 2:
            print "time du 0: ", self._records[2].bobobase_modification_time()
        
    security.declareProtected(Permissions.view_management_screens, 'getHistories')
    def getHistories(self):
        return tuple(self._records)

    security.declarePrivate('getLastTime')
    def getLastTime(self):
        if self._record_length() == 0:
            return None
        print "### DeploymentHistory: getLastTime: ", self._records
        print "time du 2: ", self._records[0].bobobase_modification_time()
        if self._record_length() > 1:
            print "time du 1: ", self._records[1].bobobase_modification_time()
        if self._record_length() > 2:
            print "time du 0: ", self._records[2].bobobase_modification_time()
        return self._records[self._record_length()-1].bobobase_modification_time()

    security.declarePrivate('makeHistory')
    def makeHistory(self):
        return DeploymentHistory('Not Recorded')
        
    def __bobo_traverse__(self, REQUEST, name=None):

        try:
            hid = int(name)
            return self._records[hid].__of__(self)
        except:
            return getattr(self, name)

InitializeClass(DeploymentHistoryContainer)

class DeploymentHistory(SimpleItem):

    meta_type = 'Deployment History'

    manage_options = ()

    security = ClassSecurityInfo()    

    index_html = DTMLFile('ui/HistoryView', globals())
    
    def __init__(self, id):
        self.id = id
        self.creation_time = DateTime()
        self.timeTime = str(int(self.creation_time.timeTime()))
        self.logs = []
        self.statistics = None
        self.last_modification_time = DateTime()
        
    def update_last_modification_time (self):
        self.last_modification_time = DateTime()
        
    def recordStatistics(self, stats_display):
        self.statistics = stats_display

    def log(self, msg, level):
        self.logs.append(msg)

    security.declarePublic('row_display')
    def row_display(self):
        
        return 'Deployed %s (<a href="%s">More Info</a>)'%(
            self.creation_time.fCommonZ(),
            self.id
            )

InitializeClass(DeploymentHistory)

    
