
from pycloak import auth, admin, merge
import pytest
import json


def test_get_auth_flows(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    auth_flows = admin.Admin(session).realm('master').auth_flows()
    assert auth_flows is not None

def test_create_auth_flow(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    auth_flow = {'alias': 'test flow', 'providerId': 'basic-flow', 'description': 'This flow is used for test purposes', 'topLevel': 'true', 'builtIn': 'false'}
    created_auth_flow = admin.Admin(session).realm('master').create_auth_flow(json.loads(json.dumps(auth_flow)))
    assert created_auth_flow is not None

def test_get_auth_flow(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    auth_flow = master_realm.auth_flow(alias='test flow')
    assert auth_flow is not None

def test_get_auth_flow_by_id(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    auth_flow = master_realm.auth_flow(alias='test flow')
    auth_flow_by_id = master_realm.auth_flow(id=auth_flow.id)
    assert auth_flow_by_id is not None

def test_get_none_auth_flow(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    auth_flow = master_realm.auth_flow(alias='not there')
    assert auth_flow is None

def test_get_none_auth_flow_by_id(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    auth_flow = master_realm.auth_flow(id='cdf3b8b6-5cdc-439d-b54a-5d375788af85')
    assert auth_flow is None

def test_get_executions(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    executions = master_realm.auth_flow(alias='browser').executions()
    assert len(executions) > 0

def test_get_empty_executions(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    executions = master_realm.auth_flow(alias='test flow').executions()
    assert len(executions) == 0

def test_get_filtered_executions(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    executions = master_realm.auth_flow(alias='browser').executions(provider='auth-cookie')
    assert len(executions) == 1
    assert executions[0]['displayName'] == 'Cookie'

def test_get_execution(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    executions = master_realm.auth_flow(alias='browser').executions()
    execution = master_realm.auth_flow(alias='browser').execution(id=executions[0]['id'])
    assert execution is not None


def test_create_execution(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    form_execution = json.loads(json.dumps({'provider': 'auth-username-password-form'}))
    created_execution = master_realm.auth_flow(alias='test flow').create_execution(form_execution)
    assert created_execution is not None


def test_update_execution(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    form_execution = json.loads(json.dumps({'provider': 'auth-username-password-form'}))
    created_execution = master_realm.auth_flow(alias='test flow').create_execution(form_execution)
    assert created_execution.json['requirement'] != 'REQUIRED', "test is brittle, assumes pre-conditions, and fails"
    created_execution.json['requirement'] = 'REQUIRED'
    assert master_realm.auth_flow(alias='test flow').update_execution(created_execution.json).json['requirement'] == 'REQUIRED'

def test_delete_execution(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    executions = master_realm.auth_flow(alias='test flow').executions()
    executions_before_delete = len(executions)
    response = master_realm.auth_flow(alias='test flow').delete_execution(executions[0]['id'])
    assert response.status_code == 204
    assert len(master_realm.auth_flow(alias='test flow').executions()) < executions_before_delete

def test_delete_all_executions(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    auth_flow = {'alias': 'test flow2', 'providerId': 'basic-flow', 'description': 'This flow is used for test purposes', 'topLevel': 'true', 'builtIn': 'false'}
    test_flow2 = admin.Admin(session).realm('master').create_auth_flow(json.loads(json.dumps(auth_flow)))
    test_flow2.create_execution({'provider': 'auth-username-password-form'})
    test_flow2.create_execution({'provider': 'identity-provider-redirector'})
    test_flow2.create_execution({'provider': 'auth-spnego'})
    assert len(master_realm.auth_flow(alias='test flow2').executions()) == 3
    test_flow2.delete_all_executions()
    assert len(master_realm.auth_flow(alias='test flow2').executions()) == 0
