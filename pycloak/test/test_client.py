

from pycloak import auth, admin, realm, client
import pytest


def test_list_clients(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    clients = kc_admin.realm('master').clients()
    assert len(clients) != 0, "No clients returned by /clients endpoint"


def test_get_nonexistent_client(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    with pytest.raises(realm.RealmException, message="Invalid client did not raise RealmException"):
        kc_admin.realm('master').client('admin-cli')


def test_get_client(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    clients = kc_admin.realm('master').clients()
    kc_admin.realm('master').client(clients[0]['id'])


def test_get_client_by_id(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    admin_cli = kc_admin.realm('master').client_id('admin-cli')
    assert admin_cli is not None, 'Could not retrieve admin-cli by clientId'


def test_get_nonexistent_client_by_id(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    none_client = kc_admin.realm('master').client_id('XXXXXX')
    assert none_client is None, 'Returned client object for non-existent clientId'


def test_create_client(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    created_client = kc_admin.realm('master').create_client('test-create-client', "openid-connect")
    assert created_client is not None


def test_update_client(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    created_client = kc_admin.realm('master').create_client('test-update-client', "openid-connect")
    created_client.json['name'] = 'Test Update Client'
    updated_client = kc_admin.realm('master').update_client(created_client.json)
    assert updated_client.json['name'] == 'Test Update Client', 'Failed to properly update client'

def test_delete_client(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    created_client = kc_admin.realm('master').create_client('test-delete-client', "openid-connect")
    kc_admin.realm('master').delete_client(created_client.json['id'])
    assert kc_admin.realm('master').client_id('test-delete-client') is None

def test_merge_client(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    created_client = kc_admin.realm('master').create_client('test-merge-client', "openid-connect")
    merging_client = client.Client(session, dict_rep={'clientId': 'test-merge-client', 'enabled': True, 'protocol': 'openid-connect', 'directAccessGrantsEnabled': False })
    merged_client = created_client.merge(merging_client)
    assert merged_client.json['directAccessGrantsEnabled'] == False

def test_merge_client_preferred(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    created_client = kc_admin.realm('master').create_client('test-merge-prefer-client', "openid-connect")
    merging_client = client.Client(session, dict_rep={'clientId': 'test-merge-prefer-client', 'enabled': True, 'protocol': 'openid-connect', 'directAccessGrantsEnabled': False })
    merged_client = created_client.merge(merging_client, prefer_self=True)
    assert merged_client.json['directAccessGrantsEnabled'] == True
