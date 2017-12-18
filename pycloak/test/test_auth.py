
from pycloak import auth
import pytest

def test_auth_success(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    access_token = session.get_access_token()
    assert access_token != None

def test_auth_failure(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, 'NOT' + admin_password)
    with pytest.raises(auth.AuthException, message='Invalid credentials did not cause exception'):
        access_token = session.get_access_token()
