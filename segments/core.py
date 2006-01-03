"""
$Id$
"""

from interfaces import *

#################################

OUTPUT_FILTERED = object()

# internal marker value to pipe execution
_OUTPUT_FINISHED = object()

#################################

class Pipeline( object ):

    __implements__ = IPipeline 
    
    def __init__(self, **kw):
        self.steps = []
        self.vars = kw
        self.services = {}
        
    def __iter__(self):
        for s in self.steps:
            yield s

    def process( self, context ):
        for s in self:
            context = s.process( self, context )

class PolicyPipeline( Pipeline ): pass


class PipeExecutor( object ):
    """
    support for pipes include producer/filters/conditional branches segments
    """

    def __init__(self, steps ):
        self.steps = steps
        self.context_iterator = None
        self.producer_idx = 0
        
    def process( self, pipeline, context ):
        idx = 0
        while context is not _OUTPUT_FINISHED:

            step = self.steps[idx]

            if isinstance( step, Producer ):
                if self.context_iterator is not None:
                    raise RuntimeError("only one producer per pipeline atm")
                self.context_iterator = step.process( self, pipeline, context )
                context = self.getNextContextObject()

            elif isinstance( step, Consumer ):
                step.process( self, pipeline, context )
                context = self.getNextContentObject()
                idx = self.producer_idx
                
            elif isinstance( step, Filter ):
                value = step.process( self, pipeline, context )
                if value is OUTPUT_FILTERED:
                    context = self.getNextContentObject()
                    idx = self.producer_idx
                else:
                    context = value
                    
            elif isinstance( step, PipeSegment ):
                context = step.process( self, pipeline, context )
                
            idx += 1

    def getNextContextObject( self ):
        if self.context_iterator is None:
            return _OUTPUT_FINISHED
        try:
            return self.context_iterator.next()
        except StopIteration:
            return _OUTPUT_FINISHED
            
                
class BaseSegment( object ):
    
    def process( self, pipeline, ctxobj ):
        raise NotImplemented

class PipeSegment( BaseSegment ):

    __implements__ =  IPipeSegment 

class Producer( PipeSegment ):

    __implements__ = IProducer 

class Consumer( PipeSegment ):

    __implements__ = IConsumer

class Filter( PipeSegment ):
    
    __implements__ = IFilter


class VariableAggregator( PipeSegment ):

    def __init__(self, variable_name=""):
        self.values = []
        self.variable_name = variable_name

    def process(self, pipeline, ctxobj ):
        pipeline.vars[ self.variable_name ]=self.values
        self.values.append( ctxobj )
        return ctxobj


## class VariableIterator( Producer ):

##     def __init__(self, variable_name, steps ):
##         self.variable_name = variable_name
##         self.steps = steps

##     def process( self, pipeline, ctxobj ):
##         for value in pipeline.vars.get( self.variable_name, () ):
##             for s in self.steps:
##                 s.process( pipeline, value )


## class ConditionalBranch( PipeSegment ):

##     def __init__(self, branches ):
##         assert isinstance( branches, list)
##         self.branches = branches

##     def addBranch( self, condition, step ):
##         self.branches.append( ( condition, step ) )

##     def process( self, pipeline, ctxobj ):
##         for condition, step in self.branches:
##             if condition( ctxobj ):
##                 return step( pipeline, ctxobj )

