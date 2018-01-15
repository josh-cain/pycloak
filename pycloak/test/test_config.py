
from pycloak import auth, admin

def test_get_valid_config(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    executions = master_realm.auth_flow(alias='first broker login').executions()
    auth_config = next(filter(lambda execution: execution.get('authenticationConfig') is not None, executions), None)
    assert auth_config is not None, "couldn't find a configurable execution"
    print(auth_config['authenticationConfig'])
    assert master_realm.auth_config(auth_config['authenticationConfig']) is not None

def test_create_config(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    master_realm = admin.Admin(session).realm('master')
    auth_flow = {'alias': 'test create config flow', 'providerId': 'basic-flow', 'description': 'This flow is used for testing config creation', 'topLevel': 'true', 'builtIn': 'false'}
    created_auth_flow = master_realm.create_auth_flow(auth_flow)
    idp_redirector = {'provider': 'identity-provider-redirector'}
    created_execution = created_auth_flow.create_execution(idp_redirector)
    new_config = created_execution.create_config({'alias': 'test create config', 'config': {'defaultProvider': 'https://www.github.com'}})
    assert new_config is not None
