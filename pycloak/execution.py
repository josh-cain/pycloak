
import json
import requests
from pycloak import auth, admin, flow

class Execution:

    def __init__(self, flow, json_rep=None, dict_rep=None):
        # TODO pretty sure I don't have to do this.  Explore what python typing automagically does for me.
        if not json_rep and dict_rep:
            json_rep = json.loads(json.dumps(dict_rep))

        self.flow = flow
        self.id = json_rep.get('id')
        self.json = json_rep

    def create_config(self, config):
        url = "{0}/auth/admin/realms/{1}/authentication/executions/{2}/config".format(self.flow.realm.auth_session.host, self.flow.realm.id, self.id)
        response = requests.post(url, json=config, headers=self.flow.realm.auth_session.bearer_header)

        if response.status_code != 201:
            raise KeycloakExecutionException("Error attempting to create new execution: {0}/{1}".format(response.status_code, response.text))

        return requests.get(response.headers['Location']).text

# TODO too many exceptions, clean up handling
class KeycloakExecutionException(Exception):
    pass
