"""
an example content filter. content filters are executed over matched
content immediately before storage.
CVS: $Id: example.py,v 1.1 2003/02/28 05:04:19 k_vertigo Exp $
"""

from registry import registerFilter

def example_filter(descriptor, rendered_content, file_path):
    """
    descriptor is a content descriptor object, it offers
    access to the context, the deployed content object, and
    various deployment metadata about the object.

    rendered content is a string of the content object in
    rendered form.

    file path, represents the filesystem path that the rendered
    content will be stored at on the *zope server*, not the
    deployment server.

    currently only modifications to the rendered content are
    tracked. changing this is trivial
    """

    # lets change all 'the's to 'The'
    return rendered_content.replace('the', 'The')

# register the filter so we can use it
registerFilter('THE_example', example_filter)
