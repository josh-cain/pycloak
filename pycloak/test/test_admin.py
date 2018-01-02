
from pycloak import auth, admin
import pytest

def test_list_realms(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    realms = kc_admin.realms
    assert len(realms) != 0, "No realms returned by /realms endpoint"

def test_get_realm(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    master = kc_admin.realm('master')
    assert master.realm == 'master', 'master realm not found'

def test_add_realm(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    new_realm = kc_admin.add_realm('add-realm-test')
    assert new_realm.realm == 'add-realm-test', 'could not successfully add new realm'

def test_update_realm(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    new_realm = kc_admin.add_realm('update-realm-test')
    assert new_realm.realm == 'update-realm-test', 'could not successfully add new realm for update test'
    assert new_realm.json['sslRequired'] != 'none', 'sslRequired flag already set to "none", cannot perform update test'
    new_realm.json['sslRequired'] = 'none'
    updated_realm = kc_admin.update_realm(new_realm)
    assert updated_realm.json['sslRequired'] == 'none'
