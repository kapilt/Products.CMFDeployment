from core import PipeSegment

class DirectoryViewDeploy( PipeSegment ):
    """
    """

    def process( self, pipe, content ):

        views = pipe.services["ContentDirectoryViews"]
        resolver = pipe.services['URIResolver']
        store = pipe.services["ContentStorage"]
        
        contents = views.getContent()

        for dvc in contents:
            resolver.addResource( dvc )

        for dvc in contents:
            views.cookViewObject( dvc )
            resolver.resolve( dvc )
            store( dvc )

