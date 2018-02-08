import mwapi
import pytest

from jade.centralauth import CentralAuth
from jade import errors
from . import util

test_config = {
    'centralauth': {
        # Global info host can be arbitrary?
        'host': 'https://www.mediawiki.org',
    },
}

# TODO: Made this up cos I haven't found a missing user yet.
missing_gui_response = {
    'batchcomplete': '',
    'query': {
        'globaluserinfo': {
            'missing': '',
        }
    }
}

missing_lui_response = {
    "batchcomplete": "",
    "query": {
        "users": [{
            "name": "Example",
            "missing": ""
        }]
    }
}

enwiki_blocked_gui_response = {
    'batchcomplete': '',
    'query': {
        'globaluserinfo': {
            'home': 'enwiki',
            'id': 19729909,
            'registration': '2013-04-14T06:48:25Z',
            'name': 'FUCKYOU',
            'groups': [],
            'rights': [],
            'merged': [
                {
                    'wiki': 'enwiki',
                    'url': 'https://en.wikipedia.org',
                    'timestamp': '2013-04-14T06:48:25Z',
                    'method': 'primary',
                    'editcount': 0,
                    'registration': '2006-03-26T17:01:06Z',
                    'blocked': {
                        'expiry': 'infinity',
                        'reason': '{{username}}'
                    },
                },
            ]
        }
    }
}

locked_gui_response = {
    'batchcomplete': '',
    'query': {
        'globaluserinfo': {
            'home': 'metawiki',
            'id': 33085348,
            'registration': '2014-08-17T23:22:31Z',
            'name': 'Jalexander',
            'locked': '',
            'groups': [],
            'rights': [],
            'merged': [
                {
                    'wiki': 'commonswiki',
                    'url': 'https://commons.wikimedia.org',
                    'timestamp': '2017-12-12T19:44:56Z',
                    'method': 'login',
                    'editcount': 0,
                    'registration': '2017-12-12T19:44:56Z',
                },
                {
                    'wiki': 'loginwiki',
                    'url': 'https://login.wikimedia.org',
                    'timestamp': '2014-08-17T23:22:33Z',
                    'method': 'login',
                    'editcount': 0,
                    'registration': '2014-08-17T23:22:33Z',
                },
                {
                    'wiki': 'metawiki',
                    'url': 'https://meta.wikimedia.org',
                    'timestamp': '2014-08-17T23:22:31Z',
                    'method': 'new',
                    'editcount': 0,
                    'registration': '2014-08-17T23:22:31Z',
                },
                {
                    'wiki': 'nowikimedia',
                    'url': 'https://no.wikimedia.org',
                    'timestamp': '2017-12-13T09:53:07Z',
                    'method': 'login',
                    'editcount': 0,
                    'registration': '2017-12-13T09:53:07Z',
                }
            ]
        }
    }
}

autopatrolled_metawiki_gui_response = {
    "batchcomplete": "",
    "query": {
        "globaluserinfo": {
            "home": "enwiki",
            "id": 15622560,
            "registration": "2012-12-21T22:37:22Z",
            "name": "Awight (WMF)",
            "groups": [
                "oathauth-tester",
                "wmf-researcher"
            ],
            "merged": [
                {
                    "wiki": "metawiki",
                    "url": "https://meta.wikimedia.org",
                    "timestamp": "2012-12-21T23:59:21Z",
                    "method": "login",
                    "editcount": 222,
                    "registration": "2012-12-21T23:59:21Z",
                    "groups": [
                        "autopatrolled"
                    ]
                },
                {
                    "wiki": "ptwiki",
                    "url": "https://pt.wikipedia.org",
                    "timestamp": "2013-04-09T01:26:35Z",
                    "method": "login",
                    "editcount": 0,
                    "registration": "2013-04-09T01:26:35Z"
                },
            ],
            "unattached": []
        }
    }
}

autopatrolled_metawiki_lui_response = {
    'batchcomplete': '',
    'query': {
        'users': [{
            'userid': 2043420,
            'name': 'Awight (WMF)',
            'groups': ['autopatrolled', '*', 'user', 'autoconfirmed']
        }]
    }
}

no_autopatrolled_metawiki_lui_response = {
    'batchcomplete': '',
    'query': {
        'users': [{
            'userid': 2043420,
            'name': 'Awight (WMF)',
            'groups': ['*', 'user', 'autoconfirmed']
        }]
    }
}


def test_from_config():
    ca = CentralAuth.from_config(test_config)
    assert isinstance(ca, CentralAuth)


# TODO: We can't test this using the current mocking strategy, because the
# error comes from within .get
# def test_get_globaluser_info_invalid_user_id():
#    ca = CentralAuth.from_config(test_config)
#    with pytest.raises(mwapi.errors.APIError):
#        ca.get_globaluser_info(0)


def test_get_globaluser_info_missing_user():
    ca = CentralAuth.from_config(test_config)

    with util.mock_mwapi_get(missing_gui_response):
        with pytest.raises(errors.GlobalUserExistenceError) as exc_info:
            gui_doc = ca.get_globaluser_info(12345)

        assert exc_info.value.gu_id == 12345


def test_get_globaluser_info():
    ca = CentralAuth.from_config(test_config)

    with util.mock_mwapi_get(enwiki_blocked_gui_response):
        gui_doc = ca.get_globaluser_info(19729909)

    assert gui_doc['home'] == 'enwiki'
    assert gui_doc['name'] == 'FUCKYOU'


def test_check_user_rights_blocked_in_context():
    ca = CentralAuth.from_config(test_config)
    with util.mock_mwapi_get(enwiki_blocked_gui_response):
        with pytest.raises(errors.UserBlockedError) as exc_info:
            ca.check_user_rights(19729909, 'enwiki', ['autopatrolled'])

    assert exc_info.value.gu_id == 19729909
    assert exc_info.value.context == 'enwiki'
    assert exc_info.value.expiry == 'infinity'
    assert exc_info.value.reason == '{{username}}'


def test_check_user_rights_blocked_other_context():
    ca = CentralAuth.from_config(test_config)
    with util.mock_mwapi_get(enwiki_blocked_gui_response):
        ca.check_user_rights(19729909, 'frwiki', ['autopatrolled'])

    assert True


def test_check_user_rights_locked():
    ca = CentralAuth.from_config(test_config)
    #with mock.patch('mwapi.session.get') as mock_mwapi:
    #    mock_mwapi.side_effect = [
    #        enwiki_blocked_gui_response,
    #        enwiki_blocked_lui_response,
    #    ]
    with util.mock_mwapi_get(locked_gui_response):
        with pytest.raises(errors.UserLockedError) as exc_info:
            ca.check_user_rights(33085348, 'enwiki', ['autopatrolled'])

    assert exc_info.value.gu_id == 33085348


def test_check_user_rights_has_autopatrolled():
    ca = CentralAuth.from_config(test_config)
    with util.mock_mwapi_get([autopatrolled_metawiki_gui_response,
                              autopatrolled_metawiki_lui_response]):
        ca.check_user_rights(15622560, 'metawiki', ['autopatrolled'])

    assert True


def test_check_user_rights_lacks_autopatrolled():
    ca = CentralAuth.from_config(test_config)
    with util.mock_mwapi_get([autopatrolled_metawiki_gui_response,
                              no_autopatrolled_metawiki_lui_response]):
        with pytest.raises(errors.UserRightsError) as exc_info:
            ca.check_user_rights(15622560, 'metawiki', ['autopatrolled'])

        assert exc_info.value.gu_id == 15622560
        assert exc_info.value.context == 'metawiki'
        assert exc_info.value.required == ['autopatrolled']
        assert exc_info.value.user_groups == ['*', 'user', 'autoconfirmed']


def test_check_user_rights_local_missing():
    ca = CentralAuth.from_config(test_config)
    with util.mock_mwapi_get([autopatrolled_metawiki_gui_response,
                              missing_lui_response]):
        with pytest.raises(errors.LocalUserExistenceError) as exc_info:
            ca.check_user_rights(15622560, 'metawiki', ['autopatrolled'])

        assert exc_info.value.name == 'Awight (WMF)'
        assert exc_info.value.context == 'metawiki'
