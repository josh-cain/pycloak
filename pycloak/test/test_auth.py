
from pycloak import admin, auth
import pytest

def test_auth_success(keycloak_server):
    session = auth.AuthSession('admin', 'password')
    access_token = session.get_access_token()
    assert access_token != None

def test_auth_failure(keycloak_server):
    session = auth.AuthSession('admin', 'NOTpassword')
    with pytest.raises(auth.AuthException, message='Invalid credentials did not cause exception'):
        access_token = session.get_access_token()
