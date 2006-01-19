"""
insure that in a given deployment we don't deploy the same object twice
$Id$
"""

from core import Filter, OUTPUT_FILTERED

class UniqueGuard( Filter ):

    def __init__(self):
        self._oid_map = {}

    def process(self, pipe, content ):

        oid = content._p_oid
        if oid in self._oid_map:
            return OUTPUT_FILTERED
        self._oid_map[oid] = None
        return content
        
