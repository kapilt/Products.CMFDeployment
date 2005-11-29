"""
$Id$
"""

def implements( iface ): pass

class IPipeline( object ):
    services = " "
    vars = " "
    steps = " "

    def process( context ): pass

class IPipeSegment( object ):
    def process( pipeline, ctxobj ): pass

class IProducer( IPipeSegment ): pass
class IConsumer( IPipeSegment ): pass
class IProducerConsumer( IPipeSegment ): pass
class IFilter( IProducerConsumer ): pass
class ITee( IPipeSegment ): pass
class IWatcher( IPipeSegment ): pass
class IConditionalBranch( IPipeSegment ): pass


#################################

class Pipeline( object ):

    def __init__(self, **kw):
        self.steps = []
        self.vars = kw
        self.services = {}
        
    def __iter__(self):
        for s in self.steps:
            yield s

    def process( self, context ): #calls process on each step
        for s in self:
            #print "Pipeline process of", s
            context = s.process( self, context )
  
class PipeSegment( object ):
    def process( self, pipeline, ctxobj ):
        raise NotImplemented

class Producer( PipeSegment ):

    def process( self, pipeline, ctxobj ):
        for res in self.generate():
            yield res

class Iterator( PipeSegment ):

    def __init__(self, steps ):
        self.steps = steps
        
    def process( self, pipeline, ctxobj ):
        for obj in ctxobj:
            for s in self.steps:
                s.process( pipeline, obj )
        return ctxobj

class VariableAggregator( PipeSegment ):

    def __init__(self, variable_name=""):
        self.values = []
        self.variable_name = variable_name

    def process(self, pipeline, ctxobj ):
        pipeline.vars[ self.variable_name ]=self.values
        self.values.append( ctxobj )
        return ctxobj

class VariableIterator( PipeSegment ):

    def __init__(self, variable_name, steps ):
        self.variable_name = variable_name
        self.steps = steps

    def process( self, pipeline, ctxobj ):
        for value in pipeline.vars.get( self.variable_name, () ):
            for s in self.steps:
                s.process( pipeline, value )


class ConditionalBranch( PipeSegment ):

    def __init__(self, branches ):
        assert isinstance( branches, list)
        self.branches = branches

    def addBranch( self, condition, step ):
        self.branches.append( ( condition, step ) )

    def process( self, pipeline, ctxobj ):
        for condition, step in self.branches:
            if condition( ctxobj ):
                return step( pipeline, ctxobj )

