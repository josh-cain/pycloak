
import pytest

@pytest.fixture(scope='session')
def keycloak_server(request):
    print('Starting docker container for Keycloak server...')
    import docker
    import requests
    import time

    # TODO error handling here for if a docker client is not detected
    # start up docker container
    client = docker.from_env()
    client.containers.run('jboss/keycloak:3.4.1.Final', environment={'KEYCLOAK_USER': 'admin', 'KEYCLOAK_PASSWORD': 'password'}, ports={'8080/tcp': '8080'}, name='pycloak-test-server', remove=True, detach=True)

    booted = False;
    while not booted:
        print('Waiting for container to boot...')
        time.sleep(1)

        try:
            booted = requests.get('http://127.0.0.1:8080/auth/admin/master/console/').status_code == 200
        except requests.exceptions.ConnectionError:
            print('Keycloak admin console not available')

    def fin():
        print('Stopping docker container for Keycloak server....')
        # spin down docker container
        pycloak_test_severs = client.containers.list(filters={'name': 'pycloak-test-server'})
        if pycloak_test_severs:
            pycloak_test_severs[0].stop()
            print('Keycloak server shutdown complete')
        else:
            print('Test server has already been shut down')

    request.addfinalizer(fin)
