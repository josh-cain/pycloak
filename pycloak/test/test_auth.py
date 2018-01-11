
from pycloak import auth, admin, realm, client
import pytest

def test_auth_success(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    access_token = session.get_access_token()
    assert access_token != None

def test_auth_failure(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, 'NOT' + admin_password)
    with pytest.raises(auth.AuthException, message='Invalid credentials did not cause exception'):
        access_token = session.get_access_token()

def test_get_offline_token(keycloak_server, admin_username, admin_password):
    # First, have to make sure that admin-cli has access to all roles, otherwise offline_token requests will fail
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    admin_cli = kc_admin.realm('master').client_id('admin-cli')
    admin_cli.json['fullScopeAllowed'] = 'true'
    kc_admin.realm('master').update_client(admin_cli.json)

    token_response = auth.direct_access_grant_token(admin_username, admin_password, include_offline=True)
    assert token_response.get('refresh_token') != None

def test_use_offline_token(keycloak_server, admin_username, admin_password):
    direct_access_token_response = auth.direct_access_grant_token(admin_username, admin_password, include_offline=True)
    offline_token_response = auth.offline_token(direct_access_token_response['refresh_token'])
    assert offline_token_response.get('access_token') != None

def test_create_session_offline_token(keycloak_server, admin_username, admin_password):
    direct_access_token_response = auth.direct_access_grant_token(admin_username, admin_password, include_offline=True)
    session = auth.AuthSession(offline_token=direct_access_token_response['refresh_token'])
    assert session.get_access_token() is not None
