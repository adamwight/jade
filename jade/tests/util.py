import contextlib
import copy
from unittest import mock


@contextlib.contextmanager
def mock_mwapi_get(response):
    """
    Helper to mock mwapi responses.

    TODO: Handle a series of responses.
    """
    # Our functions mutate their inputs, so make a copy in order to use
    # fixtures in multiple tests.
    response = copy.deepcopy(response)
    with mock.patch('mwapi.Session.get') as mock_get:
        if isinstance(response, dict):
            # Mocking a single API call.
            mock_get.return_value = response
        else:
            # Mocking a series of API calls, `response` is a list.
            mock_get.side_effect = response

        # Call the code under test.
        yield
