

# TODO - could use some constant definitions for built-in protocols.
# However, don't enumerate since protocols are extensible in Keycloak

class Client:

    def __init__(self, auth_session, client_json):
        self.auth_session = auth_session
        self.id = client_json.get('id')
        self.client_id = client_json.get('clientId')
        self.json = client_json
