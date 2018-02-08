'''
Example of a locally blocked user: https://www.mediawiki.org/w/api.php?action=query&meta=globaluserinfo&guiuser=FUCKYOU&guiprop=groups%7Cmerged%7Cunattached
Example of a locked account:
https://www.mediawiki.org/w/api.php?action=query&meta=globaluserinfo&guiuser=Jalexander&guiprop=groups%7Cmerged%7Cunattached
User in good standing: https://www.mediawiki.org/w/api.php?action=query&meta=globaluserinfo&guiuser=EpochFail&guiprop=groups%7Cmerged%7Cunattached|rights|editcount

TODO: Make a request to check on rights for every action
TODO: Make a request to local wiki (in context) for local user rights
'''  # noqa: E501
import mwapi

from . import about
from . import errors

USER_AGENT = "{} -- {}".format(about.__name__, about.__author_email__)


class CentralAuth:

    def __init__(self, ca_session):
        self.ca_session = ca_session

    def get_globaluser_info(self, gu_id):
        doc = self.ca_session.get(
            action="query", meta="globaluserinfo", guiid=gu_id,
            guiprop={'groups', 'merged', 'rights'})
        gui_doc = doc['query']['globaluserinfo']
        if 'missing' in gui_doc:
            raise errors.GlobalUserExistenceError(gu_id)

        # Convert the 'merged' field from a list to a mapping
        gui_doc['merged'] = {d['wiki']: d for d in gui_doc['merged']}

        return gui_doc

    def get_localuser_info(self, name, context_doc):
        session = mwapi.Session(context_doc['url'], user_agent = USER_AGENT)
        doc = session.get(
            action='query', list='users', ususers={name}, usprop={'groups'})
        lui_doc = doc['query']['users'][0]
        if 'missing' in lui_doc:
            raise errors.LocalUserExistenceError(name, context_doc['wiki'])

        return lui_doc

    def check_user_rights(self, gu_id, context, requirements):
        gui_doc = self.get_globaluser_info(gu_id)

        if 'locked' in gui_doc:
            raise errors.UserLockedError(gu_id)

        # Check for local context
        if context in gui_doc['merged']:
            context_doc = gui_doc['merged'][context]

            if 'blocked' in context_doc:
                raise errors.UserBlockedError(
                    gu_id,
                    context,
                    context_doc['blocked']['expiry'],
                    context_doc['blocked']['reason'])

            lui_doc = self.get_localuser_info(gui_doc['name'], context_doc)
            local_groups = lui_doc.get('groups', []) or []

            if not set(local_groups) & set(requirements):
                raise errors.UserRightsError(
                    gu_id, context, requirements, local_groups)

    @classmethod
    def from_config(cls, config):
        # Extract config.
        session_config = config['centralauth'].copy()
        if 'user_agent' not in session_config:
            session_config['user_agent'] = USER_AGENT
        # Pull host out as it's not a keyword arg.
        host = session_config['host']
        del(session_config['host'])

        # Create session based on config.
        ca_session = mwapi.Session(host, **session_config)

        return cls(ca_session)
