
from pycloak import auth, admin
import pytest
import json


def test_get_fed_providers(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    fed_providers = admin.Admin(session).realm('master').federation_providers()
    assert len(fed_providers) == 0


def test_add_fed_provider(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    provider_to_add = {'name': 'Test Kerb Provider', 'providerId': 'kerberos',
                       'providerType': 'org.keycloak.storage.UserStorageProvider', 'parentId': 'master'}
    provider_to_add['config'] = {'priority': [0], 'kerberosRealm': ['TESTKERB.COM'],
                                 'serverPrincipal': ['HTTP/test@TESTKERB.COM'], 'keytab': ['/etc/krb5.keytab'], 'debug': ['false'], 'allowPasswordAuthentication': ['false']}
    provider_json = json.loads(json.dumps(provider_to_add))
    new_provider = admin.Admin(session).realm('master').add_federation_provider(provider_json)
    assert new_provider is not None

    fed_providers = admin.Admin(session).realm('master').federation_providers()
    assert len(fed_providers) == 1


def test_get_fed_provider_by_id(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)

    fed_providers = admin.Admin(session).realm('master').federation_providers()
    assert len(fed_providers) == 1, "Unanticipated number of federation providers.  Brittle test is unusable."

    fed_provider_by_id = admin.Admin(session).realm('master').federation_provider(id=fed_providers[0]['id'])
    assert fed_provider_by_id is not None


def test_get_fed_provider_by_name(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    fed_provider_by_name = admin.Admin(session).realm('master').federation_provider(name='Test Kerb Provider')
    assert fed_provider_by_name is not None


def test_update_fed_provider(keycloak_server, admin_username, admin_password):
    session = auth.AuthSession(admin_username, admin_password)
    kerb_provider = admin.Admin(session).realm('master').federation_provider(name='Test Kerb Provider')
    kerb_provider['config']['debug'] = ['true']

    updated_kerb_provider = admin.Admin(session).realm('master').update_federation_provider(kerb_provider)
    assert updated_kerb_provider['config']['debug'] == ['true']
