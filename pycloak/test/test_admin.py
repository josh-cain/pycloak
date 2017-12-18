
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
