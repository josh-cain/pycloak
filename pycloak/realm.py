
import json
import logging
import requests
from pycloak import client


class Realm:

    def __init__(self, auth_session, realm_json):
        self.auth_session = auth_session
        self.id = realm_json.get('id')
        self.realm = realm_json.get('realm')
        self.json = realm_json

    # TODO add an optional filter criteria to clients
    def clients(self):
        clients_url = "{0}/auth/admin/realms/{1}/clients".format(
            self.auth_session.host, self.realm)
        clients_response = requests.get(
            clients_url, headers=self.auth_session.bearer_header, params={'viewableOnly': True})

        if (clients_response.status_code != 200):
            raise RealmException("Could not retrieve clients list.")

        return json.loads(clients_response.text)

    def client(self, id):
        client_url = "{0}/auth/admin/realms/{1}/clients/{2}".format(
            self.auth_session.host, self.realm, id)
        client_response = requests.get(
            client_url, headers=self.auth_session.bearer_header)

        if (client_response.status_code != 200):
            raise RealmException(
                "Could not retrieve clients for id: {}.  Did you specify using the clientId field instead of GUID?".format(id))

        return client.Client(self.auth_session, json.loads(client_response.text))

    def client_id(self, client_id):
        return next(filter(lambda client: client.get('clientId') == client_id, self.clients()), None)

    def create_client(self, client_id, protocol, rootUrl=None):
        create_client_url = "{0}/auth/admin/realms/{1}/clients".format(
            self.auth_session.host, self.realm)
        create_client_response = requests.post(create_client_url, json={'enabled': True, 'attributes': {
        }, 'redirectUris': [], 'clientId': client_id, 'protocol': protocol, 'rootUrl': rootUrl}, headers=self.auth_session.bearer_header)

        # TODO fix inconsistent errors... most things just throw an exception
        # instead of providing useful feedback
        if create_client_response.status_code != 201:
            logging.error("Failed to create client: [{}]{}".format(
                create_client_response.status_code, create_client_response.text))
            raise RealmException(
                "Could not create client with clientId: {}".format(client_id))

        new_client = requests.get(create_client_response.headers[
                                  'Location'], headers=self.auth_session.bearer_header)
        if new_client.status_code != 200:
            raise RealmException("Error attempting to retrieve newly created client: {}".format(client_id))

        return client.Client(self.auth_session, json.loads(new_client.text))

    def update_client(self, updated_client):
        client_url = "{0}/auth/admin/realms/{1}/clients/{2}".format(self.auth_session.host, self.realm, updated_client.get('id'))
        update_client_response = requests.put(client_url, json=updated_client, headers=self.auth_session.bearer_header)

        if update_client_response.status_code != 204:
            raise RealmException("Error attempting to update client: {}".format(updated_client['id']))

        updated_client = requests.get(client_url, headers=self.auth_session.bearer_header)
        if updated_client.status_code != 200:
            raise RealmException("Error attempting to retrieve newly created client: {}".format(client_id))

        return client.Client(self.auth_session, json.loads(updated_client.text))

    def delete_client(self, id):
        client_url = "{0}/auth/admin/realms/{1}/clients/{2}".format(self.auth_session.host, self.realm, id)
        delete_client_response = requests.delete(client_url, headers=self.auth_session.bearer_header)

        if delete_client_response.status_code != 204:
            raise RealmException("Error attempting to delete client: {}".format(id))

class RealmException(Exception):
    pass
