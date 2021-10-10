"""
unit tests of punx.github_handler
"""

# from .. import github_handler
from punx import github_handler  # FIXME: developer only


def test_connect_repo():
    grr = github_handler.GitHub_Repository_Reference()
    assert isinstance(grr.connect_repo(), bool)


def test_get_GitHub_credentials():
    token = github_handler.get_GitHub_credentials()
    assert isinstance(token, (type(None), str))


test_connect_repo()
