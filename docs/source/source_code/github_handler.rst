GitHub : :mod:`github_handler`
##############################

The :mod:`github_handler` module handles all communications
with the NeXus GitHub repository.  


If the user has provided
GitHub credentials (username and password) in a 
`__github_creds__.txt` file in the source code directory, 
then the access will be through 
the Github Basic Authentication interface.  This is helpful since
the GitHub API Rate Limit allows for only a few downloads
through the API per hour if using unauthenticated access.

source code documentation
*************************

..  automodule:: punx.github_handler
    :members: 
    :synopsis: manages the communications with GitHub
