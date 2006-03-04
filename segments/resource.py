from core import PipeSegment
from Products.CMFCore.FSObject import FSObject

class SiteResourceDeploy( PipeSegment ):
    """
    """

    def __init__(self, incremental=False):
        self.incremental = incremental

    def process( self, pipe, content ):
        resources = pipe.services["SiteResources"]
        resolver = pipe.services['ContentResolver']
        store = pipe.services["ContentStorage"]
        
        contents = list( resources.getContent() )

        
        if self.incremental and pipe.variables['LastDeployTime'] is not None:
            
            dtime = pipe.variables['LastDeployTime']
            dticks = dtime.timeTime()
            
            def time_filter( descriptor ):
                dvo = descriptor.getContent()
                if isinstance( dvo, FSObject):
                    #print "time", dticks, dvo._file_mod_time, dvo.bobobase_modification_time().timeTime(), dticks < dvo._file_mod_time, dtime < dvo.bobobase_modification_time()
                    return dticks < dvo._file_mod_time 
                else:
                    return dtime < dvo.bobobase_modification_time()

            original_count = len(contents)
            contents = filter( time_filter, contents )
            print "Time Filtered %s Directory View Objects"%(original_count-len(contents))

        for rd in contents:
            resolver.addResource( rd )

        for rd in contents:
            resources.cook( rd )
            resolver.resolve( rd )
            store.add( pipe, rd )

