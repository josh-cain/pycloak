
from pycloak import auth, admin, realm
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
    assert master.id == 'master', 'master realm not found'

def test_get_realm_not_found(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    nonexistent_realm = kc_admin.realm('none')
    assert nonexistent_realm is None

def test_add_realm(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    new_realm = kc_admin.add_realm('add-realm-test')
    assert new_realm.id == 'add-realm-test', 'could not successfully add new realm'

def test_update_realm(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    new_realm = kc_admin.add_realm('update-realm-test')
    assert new_realm.id == 'update-realm-test', 'could not successfully add new realm for update test'
    assert new_realm.json['sslRequired'] != 'none', 'sslRequired flag already set to "none", cannot perform update test'
    new_realm.json['sslRequired'] = 'none'
    updated_realm = kc_admin.update_realm(new_realm)
    assert updated_realm.json['sslRequired'] == 'none'

def test_merge_realm(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    new_realm = kc_admin.add_realm('merge-realm-test')
    assert new_realm.id == 'merge-realm-test', 'could not successfully add new realm for update test'
    merge_realm = realm.Realm(session, dict_rep={'id': 'merge-realm-test', 'accessCodeLifespan': 33})
    merge_result = new_realm.merge(merge_realm)
    assert merge_result.json['accessCodeLifespan'] == 33
    assert merge_result.json['enabled'] == True

def test_merge_realm_preferring_self(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kc_admin = admin.Admin(session)
    new_realm = kc_admin.add_realm('merge-realm-test2')
    assert new_realm.id == 'merge-realm-test2', 'could not successfully add new realm for update test'
    merge_realm = realm.Realm(session, dict_rep={'id': 'merge-realm-test2', 'accessCodeLifespan': 33})
    merge_result = new_realm.merge(merge_realm, prefer_self=True)
    assert merge_result.json['accessCodeLifespan'] != 33
