from core import PipeSegment
from Products.CMFCore.FSObject import FSObject

class RegistryDeploy( PipeSegment ):
    """
    """

    def __init__(self, incremental=False):
        self.incremental = incremental

    def process( self, pipe, content ):
        registries = pipe.services["ContentRegistries"]
        resolver = pipe.services['ContentResolver']
        store = pipe.services["ContentStorage"]
        
        contents = registries.getContent()

        if self.incremental and pipe.variables['LastDeployTime'] is not None:
            dtime = pipe.variables['LastDeployTime']
            dticks = dtime.timeTime()
            
            def time_filter( descriptor ):
                dvo = descriptor.getContent()
                if isinstance( dvo, FSObject):
                    #print "time", dticks, dvo._file_mod_time, dvo.bobobase_modification_time().timeTime(), dticks < dvo._file_mod_time, dtime < dvo.bobobase_modification_time()
                    return dticks < dvo._file_mod_time or \
                           dtime  < dvo.bobobase_modification_time()
                else:
                    return dtime < dvo.bobobase_modification_time()

            original_count = len(contents)
            contents = filter( time_filter, contents )
            #print "Time Filtered %s Directory View Objects"%(original_count-len(contents))

        for dr in contents:
            resolver.addResource( dr )

        for dr in contents:
            f = open("/tmp/debug.log", "a")
            f.write("RegistryDeploy => %r\n" % dr)
            f.close()
            registries.cookRegistryObject( dr )
            resolver.resolve( dr )
            store.add( pipe, dr )

