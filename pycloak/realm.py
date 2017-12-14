
class Realm:

    def __init__(self, auth_session, realm_json):
        self.auth_session = auth_session
        self.id = realm_json['id']
        self.realm = realm_json['realm']
