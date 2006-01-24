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
Purpose: Organizes Content in a Deployment Target Structure
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id$
"""

ContentSources        = 'sources'
ContentFilters        = 'filters'

ContentIdentification = 'ContentIdentification'
ContentOrganization   = 'ContentOrganization'
ContentMastering      = 'ContentMastering'
ContentDeployment     = 'ContentDeployment'
ContentDirectoryViews = 'ContentDirectoryViews'
ContentRegistries     = 'ContentRegistries'
ContentURIs           = 'ContentURIs'
DeploymentHistory     = 'DeploymentHistory'

DeletionSource        = 'deletion_source'
DependencySource      = 'dependency_source'

ContentTransforms     = 'transforms'

DEFAULT_CONTENT_SOURCE_ID = "portal_catalog_source"

from ContentOrganization import ContentOrganization as KlassContentOrganization
from ContentIdentification import ContentIdentification as KlassContentIdentification
from ContentMastering import ContentMastering as KlassContentMastering
from ContentDeployment import ContentDeployment as KlassContentDeployment
from DeploymentHistory import DeploymentHistoryContainer as KlassDeploymentHistory
from ContentDirectoryViews import ContentDirectoryView as KlassContentDirectoryView
from ContentRegistries import ContentRegistry as KlassContentRegistry
from ContentURI import ContentURI as KlassContentURI
from ContentTransforms import ContentTransforms as KlassContentTransforms

def add_structure(policy):

    ob = KlassContentOrganization(ContentOrganization)
    policy._setObject(ContentOrganization, ob)

def add_identification(policy):

    ob = KlassContentIdentification(ContentIdentification)
    policy._setObject(ContentIdentification, ob)

def add_mastering(policy):

    ob = KlassContentMastering(ContentMastering)
    policy._setObject(ContentMastering, ob)

def add_deployment(policy):

    ob = KlassContentDeployment(ContentDeployment)
    policy._setObject(ContentDeployment, ob)

def add_view(policy):
    
    ob = KlassContentDirectoryView(ContentDirectoryViews)
    policy._setObject(ContentDirectoryViews, ob)

def add_registry(policy):
    
    ob = KlassContentRegistry(ContentRegistries)
    policy._setObject(ContentRegistries, ob)

def add_history(policy):

    ob = KlassDeploymentHistory(DeploymentHistory)
    policy._setObject(DeploymentHistory, ob)

def add_uris(policy):
    
    ob = KlassContentURI(ContentURIs)
    policy._setObject(ContentURIs, ob)

def add_filter(policy):

    ob = KlassContentTransforms(ContentTransforms)
    policy._setObject(ContentTransforms, ob)
        
_add_funcs = [
    ( ContentOrganization, add_structure ),
    ( ContentIdentification, add_identification ),
    ( ContentMastering, add_mastering ),
    ( ContentDeployment, add_deployment ),
    ( ContentDirectoryViews, add_view ),
    ( ContentRegistries, add_registry ),
    ( DeploymentHistory, add_history ),
    ( ContentURIs, add_uris ),
    ( ContentTransforms, add_filter ),
    ]

def install(deployment_policy):
    global _funcs
    for id, f in _add_funcs:
        if id in deployment_policy.objectIds():
            continue
        f(deployment_policy)
