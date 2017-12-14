
from pycloak import admin, auth

def test_test():
    session = auth.AuthSession('admin', 'password')
    assert session != None
    adminn = admin.Admin(session)
    print(adminn.get_realms())
