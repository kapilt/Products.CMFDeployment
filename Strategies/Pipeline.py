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
Purpose: DefaultPolicyPipeline Strategy for Policy Execution
Author: lucie
License: GPL
Created: 11/18/2005
"""

#from common import *
from Products.CMFDeployment import dependencies, pipeline
from Products.CMFCore.utils import getToolByName

def DefaultPolicyPipelineStrategy(self):

    steps= (pipeline.PipeEnvironmentInitializer(),
                pipeline.ContentSource(),
                pipeline.ContentPreparation(),
                pipeline.DirectoryViewDeploy(),
                dependencies.DependencyManager(),
                pipeline.ContentProcessPipe(),
                pipeline.ContentDeletionPipeline(),
                #pipeline.ContentTransport(),
                pipeline.ContentWatchEnd()
                )
    #Create a pipeline and Add steps in it
    new_pipeline = pipeline.PolicyPipeline()
    new_pipeline.steps= steps  
    
    stat_block= new_pipeline.process(self)
    
    return stat_block
    
