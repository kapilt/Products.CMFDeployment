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
Purpose: Stores Rendered Content on the FileSystem
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id$
"""

from Interface import Base as Interface
from Log import LogFactory
from Statistics import IOStatistics

from os import sep, path, mkdir
log = LogFactory('Content Storage')

class IContentStorage(Interface):
    """
    convienent point of collecting stats, and
    centralizing storage of rendered content.

    actual storage location is determined by
    content organization. should get refactored
    over here.
    """

    def store(self, descriptor):
        """
        
        """

class ContentStorage:

    def __init__(self, ctx):
        self.stats = IOStatistics()
        self.structure = ctx.getContentOrganization().getActiveStructure()
        self.filters = ctx.getContentFilters()
        
    def getStatistics(self):
        return self.stats
    
    def __call__(self, descriptor):
        """
        store a rendered content object on the filesystem.
        """

        # sometimes we want to have content in the uri db
        # but we don't actually want to store it... either because
        # of an error during rendering or based on configuration.
        if descriptor.isGhost(): 
            return 

        descriptors = descriptor.getDescriptors()

        for descriptor in descriptors:
            content_path = self.structure.getContentPathFromDescriptor( descriptor )
            if content_path.endswith(sep):
                log.warning('invalid content path detected %s ... fixing'%content_path)
                content_path = content_path[:-1]
            self.storeDescriptor( content_path, descriptor )

        return True
    
    store = __call__
    
    def storeDescriptor(self, content_path, descriptor ):
        """
        """
        filename = descriptor.getFileName()
        location = sep.join( ( content_path, filename) )
        content = descriptor.getContent()
        rendered = descriptor.getRendered()

        # creates directories as needed below mount point
        if not self.createParentDirectories( location ):
            return
            
        self.stats( location, len(rendered) )

        rendered = self.filters.filter(descriptor, rendered, location)
        if not rendered:
            return

        log.debug("storing content %s at %s"%(descriptor.content_url, location))
        
        fh = open(location, 'w')
        try:
            fh.write(rendered)
        finally:
            fh.close()

    def createParentDirectories(self, location ):
        """
        creates parent directories as needed below mount point
        for the given location
        """
        directory = path.dirname( location )
        if path.exists( directory ):
            return True
        if not location.startswith( self.structure.mount_point ):
            log.warning( 'invalid store location %s'%(location))
            return False
        log.debug("creating parent directories for location %s"%location)
        components = directory.split(sep)
        for i in range( 2, len(components)+1 ):
            ppath = sep.join( components[:i] )
            if not path.exists( ppath ):
                mkdir( ppath )
        return True
                        
        

            

