
import json
from pycloak import merge

# TODO - could use some constant definitions for built-in protocols.
# However, don't enumerate since protocols are extensible in Keycloak

class Client:

    def __init__(self, auth_session, json_rep=None, dict_rep=None):
        if not json_rep and dict_rep:
            json_rep = json.loads(json.dumps(dict_rep))

        self.auth_session = auth_session
        self.id = json_rep.get('id')
        self.json = json_rep

    def merge(self, other, prefer_self=False):
        if prefer_self:
            return Client(self.auth_session, dict_rep=merge.merge(self.json, other.json))
        else:
            return Client(self.auth_session, dict_rep=merge.merge(other.json, self.json))
