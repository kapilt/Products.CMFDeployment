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
$Id: $
"""

from Interface import Base as Interface
from Log import LogFactory
from Statistics import IOStatistics

from os import sep, path
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
        # but we don't actually want to store it...
        if descriptor.isGhost(): 
            return 
        
        content_path = self.structure.getContentPathFromDescriptor(
                                                         descriptor
                                                         )
        descriptors = descriptor.getDescriptors()

        # if we have child descriptors assume its a sub contained content
        # for now.. XXX the underlying issue is that the structure is
        # already generated and now we possibly need to push new directories
        # into the structure.

        if content_path.endswith(sep):
            #log.debug('EGAGS')
            content_path = content_path[:-1]

        if not path.exists(content_path):
            if not os.path.startswith( self.structure.mount_point ):
                log.warning( 'content directory %s does not exist for %s'%(content_path, descriptor.content_url))
                return
            # xxx nested content, not supported.. but it would break here.
            os.mkdir( content_path )
        return self.storeDescriptor( content_path, descriptor )

    store = __call__
    
    def storeDescriptor(self, content_path, descriptor ):

        filename = descriptor.getFileName()
        location = sep.join( ( content_path, filename) )
        content = descriptor.getContent()
        rendered = descriptor.getRendered()

        #log.debug('storing location  %s, format %s size %d'%(location,
        #                                                     descriptor.getContent().Format(),
        #                                                     len(rendered)
        #                                             )
        #          )
        
        
        self.stats( location, len(rendered) )

        rendered = self.filters.filter(descriptor, rendered, location)
        
        if not rendered:
            return

        try:         
            if content.Format().split('/')[0]=='text':
                fh = open(location, 'w')
            else:
                fh = open(location, 'wb')
        except:
	    log.error("Could not open file for storage %s %s"%(location, descriptor.getContent().getPortalTypeName()))
	    return
        try:
            fh.write(rendered)
        finally:
            fh.close()
            

