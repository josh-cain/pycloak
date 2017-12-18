
import json
import logging
import requests


class Realm:

    def __init__(self, auth_session, realm_json):
        self.auth_session = auth_session
        self.id = realm_json.get('id')
        self.realm = realm_json.get('realm')
        self.display_name = realm_json.get('displayName')

    # TODO add an optional filter criteria to clients
    def clients(self):
        clients_url = "{0}/auth/admin/realms/{1}/clients".format(
            self.auth_session.host, self.realm)
        clients_response = requests.get(
            clients_url, headers=self.auth_session.bearer_header, params={'viewableOnly': True})

        if (clients_response.status_code != 200):
            raise AdminException("Could not retrieve clients list.")

        return json.loads(clients_response.text)

    def client(self, client_id):
        # http://localhost:8080/auth/admin/realms/master/clients/1e6ff7ea-0812-4b95-b7d5-bfbe67c467f5
        client_url = "{0}/auth/admin/realms/{1}/clients/{2}".format(
            self.auth_session.host, self.realm, client_id)
        client_response = requests.get(
            client_url, headers=self.auth_session.bearer_header)

        if (clients_response.status_code != 200):
            raise AdminException("Could not retrieve clients list.")

        return json.loads(client_response.text)
