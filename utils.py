##################################################################
#
# (C) Copyright 2002 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
Purpose: general utility functions
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
License: GPL
Created: 8/10/2002
CVS: $Id: utils.py,v 1.4 2003/02/28 05:03:22 k_vertigo Exp $
"""



import OFS, App

def registerIcon(filename):
    """
    verbatim from mailing list post
    http://zope.nipltd.com/public/lists/zope-archive.nsf/ByKey/EF7C85E6A2AA8FDA
    """    
    # A helper function that takes an image filename (assumed
    # to live in a 'www' subdirectory of this package). It 
    # creates an ImageFile instance and adds it as an attribute
    # of misc_.MyPackage of the zope application object (note
    # that misc_.MyPackage has already been created by the product
    # initialization machinery by the time registerIcon is called).

    setattr(OFS.misc_.misc_.CMFDeployment, 
            filename, 
            App.ImageFile.ImageFile('www/%s' % filename, globals())
            )



def file2string(o):
    """ transform a zope file object into a string """
    
    (start,end) = (0,o.getSize())
    data = o.data
    if type(data) is type(''): #StringType
        return data[start:end]
    else: # blob chain
        pos = 0
        buf = [] #infile = StringIO(data.data)
        w = buf.append
        while data is not None:
            l =  len(data.data)
            pos = pos + l
            if pos > start:
                # We are within the range
                lstart = l - (pos - start)

                if lstart < 0: lstart = 0
                
                # find the endpoint
                if end <= pos:
                    lend = l - (pos - end)
                    w(data[lstart:lend])
                    break

                w(data[lstart:])

            data = data.next

    return ''.join(buf)
    
