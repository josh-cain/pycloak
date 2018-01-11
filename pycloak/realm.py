
import json
import logging
import requests
from pycloak import client, merge


class Realm:

    def __init__(self, auth_session, json_rep=None, dict_rep=None):
        if not json_rep and dict_rep:
            json_rep = json.loads(json.dumps(dict_rep))

        self.auth_session = auth_session
        self.id = json_rep.get('id')
        self.json = json_rep

    # TODO add an optional filter criteria to clients
    def clients(self):
        clients_url = "{0}/auth/admin/realms/{1}/clients".format(self.auth_session.host, self.id)
        clients_response = requests.get(clients_url, headers=self.auth_session.bearer_header, params={'viewableOnly': True})

        # TODO only return none on not found, all other erros should exception
        if (clients_response.status_code != 200):
            return None

        return json.loads(clients_response.text)

    def client(self, id):
        client_url = "{0}/auth/admin/realms/{1}/clients/{2}".format(self.auth_session.host, self.id, id)
        client_response = requests.get(client_url, headers=self.auth_session.bearer_header)

        if (client_response.status_code != 200):
            raise RealmException(
                "Could not retrieve clients for id: {}.  Did you specify using the clientId field instead of GUID?".format(id))

        return client.Client(self.auth_session, json_rep=json.loads(client_response.text))

    def client_id(self, client_id):
        client_json = next(filter(lambda client: client.get('clientId') == client_id, self.clients()), None)
        if client_json:
            return client.Client(self.auth_session, json_rep=client_json)
        else:
            return None

    def create_client(self, client_id, protocol, rootUrl=None):
        create_client_url = "{0}/auth/admin/realms/{1}/clients".format(
            self.auth_session.host, self.id)
        create_client_response = requests.post(create_client_url, json={'enabled': True, 'attributes': {
        }, 'redirectUris': [], 'clientId': client_id, 'protocol': protocol, 'rootUrl': rootUrl}, headers=self.auth_session.bearer_header)

        # TODO fix inconsistent errors... most things just throw an exception
        # instead of providing useful feedback
        if create_client_response.status_code != 201:
            logging.error("Failed to create client: [{}]{}".format(
                create_client_response.status_code, create_client_response.text))
            raise RealmException("Could not create client with clientId: {}".format(client_id))

        new_client = requests.get(create_client_response.headers['Location'], headers=self.auth_session.bearer_header)
        if new_client.status_code != 200:
            raise RealmException("Error attempting to retrieve newly created client: {}".format(client_id))

        return client.Client(self.auth_session, json_rep=json.loads(new_client.text))

    def update_client(self, updated_client):
        client_url = "{0}/auth/admin/realms/{1}/clients/{2}".format(self.auth_session.host, self.id, updated_client.get('id'))
        update_client_response = requests.put(client_url, json=updated_client, headers=self.auth_session.bearer_header)

        if update_client_response.status_code != 204:
            raise RealmException("Error attempting to update client: {}".format(updated_client['id']))

        updated_client = requests.get(client_url, headers=self.auth_session.bearer_header)
        if updated_client.status_code != 200:
            raise RealmException("Error attempting to retrieve newly created client: {}".format(client_id))

        return client.Client(self.auth_session, json_rep=json.loads(updated_client.text))

    def delete_client(self, id):
        client_url = "{0}/auth/admin/realms/{1}/clients/{2}".format(self.auth_session.host, self.id, id)
        delete_client_response = requests.delete(client_url, headers=self.auth_session.bearer_header)

        if delete_client_response.status_code != 204:
            raise RealmException("Error attempting to delete client: {}".format(id))

    def merge(self, other, prefer_self=False):
        if prefer_self:
            return Realm(self.auth_session, dict_rep=merge.merge(self.json, other.json))
        else:
            return Realm(self.auth_session, dict_rep=merge.merge(other.json, self.json))

    def federation_providers(self):
        fed_provider_url = "{0}/auth/admin/realms/{1}/components?parent={1}&type=org.keycloak.storage.UserStorageProvider".format(
            self.auth_session.host, self.id)
        get_fed_providers_response = requests.get(fed_provider_url, headers=self.auth_session.bearer_header)

        if get_fed_providers_response.status_code != 200:
            raise RealmException("Error attempting to retrieve federation providers for realm: {}".format(self.id))

        return json.loads(get_fed_providers_response.text)

    def add_federation_provider(self, federation_provider):
        fed_provider_url = "{0}/auth/admin/realms/{1}/components".format(self.auth_session.host, self.id)
        add_fed_provider_response = requests.post(fed_provider_url, json=federation_provider,
                                                  headers=self.auth_session.bearer_header)

        if add_fed_provider_response.status_code != 201:
            raise RealmException("Error attempting to create federation provider: {0}.  Recieved HTTP code: {1}, with message: {2}".format(
                federation_provider['name'], add_fed_provider_response.status_code, add_fed_provider_response.text))

        retrieve_new_fed_provider_response = requests.get(add_fed_provider_response.headers[
                                                          'Location'], headers=self.auth_session.bearer_header)
        if retrieve_new_fed_provider_response.status_code != 200:
            raise RealmException("Error attempting to retrieve newly created federation provider: {}".format(
                federation_provider['name']))

        return json.loads(retrieve_new_fed_provider_response.text)

    def federation_provider(self, id=None, name=None):
        if id is not None:
            fed_provider_url = "{0}/auth/admin/realms/{1}/components/{2}".format(self.auth_session.host, self.id, id)
            get_fed_provider_response = requests.get(fed_provider_url, headers=self.auth_session.bearer_header)

            # TODO only return none on 404/Not Found
            if get_fed_provider_response.status_code != 200:
                return None

            return json.loads(get_fed_provider_response.text)

        elif name is not None:
            return next(filter(lambda provider: provider.get('name') == name, self.federation_providers()), None)

        else:
            raise RealmException(
                "Cannot lookup federation provider for realm {} without an ID or name.  Please specify one.".format(self.id))

    def update_federation_provider(self, updated_provider):
        fed_provider_url = "{0}/auth/admin/realms/{1}/components/{2}".format(
            self.auth_session.host, self.id, updated_provider['id'])
        update_fed_provider_response = requests.put(
            fed_provider_url, json=updated_provider, headers=self.auth_session.bearer_header)

        if update_fed_provider_response.status_code != 204:
            raise RealmException("Unable to update federation provider with id: {0}.  Returned HTTP {1}, with message: {2}".format(
                updated_provider['id'], update_fed_provider_response.status_code, update_fed_provider_response.text))

        return self.federation_provider(id=updated_provider['id'])

    # TODO fed provider delete


class RealmException(Exception):
    pass
