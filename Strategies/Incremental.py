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
Purpose: Default Strategy for Policy Execution
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
License: GPL
Created: 10/10/2002
$Id$
"""

from common import *
from DateTime import DateTime

def IncrementalStrategy(self):
    #################################
    #
    source     = self.getContentIdentification()
    structure  = self.getContentOrganization()
    mastering  = self.getContentMastering()
    deployer   = self.getContentDeployment()
    views      = self.getContentDirectoryViews()
    registries = self.getContentRegistries()
    resolver   = self.getDeploymentURIs()
    history    = self.getDeploymentHistory()
    
    store = ContentStorage(self)
    stats = TimeStatistics()
    mstats = MemoryStatistics()

    descriptors = []
    w = descriptors.append

    log.debug('setting up structure')
    views.mountDirectories(structure.getActiveStructure())
    registries.mountDirectories(structure.getActiveStructure())
    structure.mount()

    # these need to get an aggregator facade
    stats('structure mounting')
    mstats('structure mounting')

    mount_point = structure.getActiveStructure().getCMFMountPoint()
    mount_path = mount_point.getPhysicalPath()
    mlen = len('/'.join(mount_path))
    mount_url_root = mount_point.absolute_url(1)

    uri_resolver = resolver.clone(persistent=1)
    
    # should setup an edit method for this
    uri_resolver.mount_path = mount_url_root
    uri_resolver.source_host = self.REQUEST['SERVER_URL']
    uri_resolver.mlen = len(mount_url_root)
    
    log.debug('setting up mastering')    
    mastering.setup()
    #stats('mastering setup')

    # incremental time
    last_time = history.getLastTime()

    descriptor_factory = DescriptorFactory(self)

    gc_counter = 0
    gc_threshold = 25

    try:
        
        log.debug('retrieving content')
        content = source.getContent(mount_length=mlen)
        stats('retrieving content')
        mstats('content retrieval')
        
        log.debug('processing content loop %d'%len(content))
        
        for ci in content:

            # this datetime parse is expensive... using a specialized dt index
            # would be better.
            if not last_time is None and DateTime(ci.ModificationDate) < last_time:
                continue
            
            co = ci.getObject()
            d = descriptor_factory(co) 
            if not mastering.prepare(d):
                try: co._p_deactivate()
                except: pass
                continue                        
            uri_resolver.addResource(d)            
            w(d)

            try: co._p_deactivate()
            except: pass
                
            gc_counter += 1
            if gc_threshold%gc_counter == 0:
                log.debug('garbage collecting')
                self._p_jar._incrgc()

        gc_counter = 0
        
        # add in content from directory views

        # handle directory view merging...        
        directory_contents = views.getContent()
        map(uri_resolver.addResource, directory_contents)        
        for dvo in directory_contents:
            views.cookViewObject(dvo)
            uri_resolver.resolve(dvo)
            store(dvo)

        # handle registries merging...        
        directory_contents = registries.getContent()
        map(uri_resolver.addResource, directory_contents)        
        for ro in directory_contents:
            registries.cookViewObject(ro) # FIXME ?
            uri_resolver.resolve(ro)
            store(ro)

        # we now return you to your regularly scheduled deployment        
        stats('1st pass, content prep', relative='retrieving content')
        mstats('content filtering/prep')
        log.debug('mastering content %d'%len(descriptors))

        for d in descriptors:

            ci = d.getContent()
            #log.debug('%s mastering content (%s) '%(str(ci.absolute_url(1)), str(ci.portal_type)))
                
            mastering.cook(d)
            stats( 'cook time' )

            if not d.isGhost():
                uri_resolver.resolve(d)
                stats( 'resolve time' )
            
            store(d)
            stats( 'storage time' )

            # ghostify the object
            try: ci._p_deactivate()
            except: pass

            # check mem pressure
            gc_counter += 1
            if gc_counter % gc_threshold == 0:
                log.debug('garbage collecting')
                self._p_jar._incrgc()

            stats('cache fiddle time')
            
            del d

        mstats('content rendering')
        stats('2nd pass, content cook/store', relative='1st pass, content prep')

        del uri_resolver # save for incremental deployments
        del descriptors 

    finally:
        mastering.tearDown()
        structure.unmount()
        #uri_resolver._p_changed=1
        
    log.debug('deploying content')
    deployer.deploy(structure.getActiveStructure())

    stats.stop()
    mstats.stop()
    
    block = stats.pprint() + '\n\n' +mstats.pprint()
    return block
