##################################################################
#
# (C) Copyright 2002-2004 Kapil Thangavelu <k_vertigo@objectrealms.net
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

##################################
# simple global protocol registry    

import Default
import Incremental


class StrategyDatabase:

    def __init__(self):
        self._strategies = {}

    def registerStrategy(self, name, protocol):
        self._strategies[name]=protocol

    def getStrategyNames(self, context=None):
        return self._strategies.keys()

    def getStrategy(self, name):
        return self._strategies[name]


_strategies = StrategyDatabase()

registerStrategy = _strategies.registerStrategy
getStrategyNames = _strategies.getStrategyNames
getStrategy = _strategies.getStrategy

registerStrategy('default', Default.DefaultStrategy)
registerStrategy('incremental', Incremental.IncrementalStrategy)

