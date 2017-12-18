
import pytest

@pytest.fixture(scope='session')
def admin_username():
    return 'admin'

@pytest.fixture(scope='session')
def admin_password():
    return 'password'

@pytest.fixture(scope='session')
def keycloak_server(request, admin_username, admin_password):
    print('Starting docker container for Keycloak server...')
    import docker
    import requests
    import time

    docker_instance_name = 'pycloak-test-server'
    client = docker.from_env()
    client.containers.run('jboss/keycloak:3.4.1.Final', environment={'KEYCLOAK_USER': admin_username, 'KEYCLOAK_PASSWORD': admin_password}, ports={'8080/tcp': '8080'}, name=docker_instance_name, remove=True, detach=True)

    booted = False;
    while not booted:
        print('Waiting for container to boot...')
        time.sleep(1)

        try:
            booted = requests.get('http://127.0.0.1:8080/auth/admin/master/console/').status_code == 200
            print('Keycloak console is up, fixture is ready.')
        except requests.exceptions.ConnectionError:
            print('Keycloak admin console not available')

    def fin():
        print('Stopping docker container for Keycloak server....')
        # spin down docker container
        pycloak_test_severs = client.containers.list(filters={'name': docker_instance_name})
        if pycloak_test_severs:
            pycloak_test_severs[0].stop()
            print('Keycloak server shutdown complete')
        else:
            print('Test server has already been shut down')

    request.addfinalizer(fin)
