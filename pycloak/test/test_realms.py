
from pycloak import admin, auth

def test_test():
    session = auth.AuthSession('admin', 'password')
    #admin = admin.Admin(session)
    assert session != None
