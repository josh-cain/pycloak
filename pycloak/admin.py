
import json
import logging
import requests
from pycloak import realm

class Admin:

    def __init__(self, auth_session):
        self.auth_session = auth_session

    def get_realms(self):
        realms_url = "{0}/auth/admin/realms".format(self.auth_session.host)
        realms_response = requests.get(
            realms_url, headers=self.auth_session.bearer_header)

        if (realms_response.status_code != 200):
            raise AdminException('Could not retrieve realms')

        return json.loads(realms_response.text)

    realms = property(get_realms)

    def realm(self, realm_name):
        realms_url = "{0}/auth/admin/realms/{1}".format(self.auth_session.host, realm_name)
        realm_response = requests.get(realms_url, headers=self.auth_session.bearer_header)

        if (realm_response.status_code != 200):
            raise AdminException(
                "Could not retrieve realm {}".format(realm_name))

        return realm.Realm(self.auth_session, json.loads(realm_response.text));

    def add_realm(self, realm_id, enabled=True):
        realms_url = "{0}/auth/admin/realms".format(self.auth_session.host)
        add_realm_data = {'id': realm_id, 'realm': realm_id, 'enabled': enabled}
        realm_response = requests.post(
            realms_url, json=add_realm_data, headers=self.auth_session.bearer_header)

        if (realm_response.status_code != 201):
            raise AdminException(
                "Could not add realm {}".format(realm_id))

        return realm_response.headers['Location']

class AdminException:

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
