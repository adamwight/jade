'''
Example of a locally blocked user: https://www.mediawiki.org/w/api.php?action=query&meta=globaluserinfo&guiuser=FUCKYOU&guiprop=groups%7Cmerged%7Cunattached
Example of a locked account:
https://www.mediawiki.org/w/api.php?action=query&meta=globaluserinfo&guiuser=Jalexander&guiprop=groups%7Cmerged%7Cunattached
User in good standing: https://www.mediawiki.org/w/api.php?action=query&meta=globaluserinfo&guiuser=EpochFail&guiprop=groups%7Cmerged%7Cunattached|rights|editcount

TODO: Make a request to check on rights for every action
TODO: Make a request to local wiki (in context) for local user rights
'''  # noqa: E501
import mwapi

from . import errors


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
        session = mwapi.Session(
            context_doc['url'], self.ca_session.user_agent)
        doc = session.get(
            action='query', list='users', ususers={name}, usprop={'groups'})
        lui_doc = doc['query']['users'][0]
        if 'missing' in lui_doc:
            raise errors.LocalUserExistenceError(name, context_doc['wiki'])

        return lui_doc

    def check_user_rights(self, gu_id, context, requirements):
        gui_doc = self.get_globaluser_info(gu_id)

        if 'locked' in gui_doc:
            raise errors.UserLockedError(
                "The user account with gu_id={0} is locked".format(gu_id))

        # Check for local context
        if context in gui_doc['merged']:
            context_doc = gui_doc['merged'][context]

            if 'blocked' in context_doc:
                raise errors.UserBlockedError(
                    "the user account with gu_id={0} is blocked on {1}: {2}"
                    .format(gu_id, context, context_doc['blocked']))

            lui_doc = self.get_localuser_info(gui_doc['name'], context_doc)
            local_groups = lui_doc.get('groups', []) or []

            if not set(local_groups) & set(requirements):
                raise errors.UserRightsError(
                    gu_id, context, requirements, local_groups)

    @classmethod
    def from_config(cls, config):
        return cls(config['centralauth'])
