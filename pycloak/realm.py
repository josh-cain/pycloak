
import json
import logging
import requests

class Realm:

    def __init__(self, auth_session, realm_json):
        self.auth_session = auth_session
        self.id = realm_json['id']
        self.realm = realm_json['realm']
        self.display_name = realm_json['displayName']

    # TODO add an optional filter criteria to clients
    def clients(self):
        clients_url = "{0}/auth/admin/realms/{1}/clients".format(
            self.auth_session.host, self.realm)
        clients_response = requests.get(
            clients_url, headers=self.auth_session.bearer_header, params={'viewableOnly': True})

        if (clients_response.status_code != 200):
            raise AdminException("Could not retrieve clients list.")

        return json.loads(clients_response.text)
