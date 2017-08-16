
import json
import logging
import requests
import urllib.parse
import urllib.request

logger = logging.getLogger('pycloak.auth')


def direct_access_grant_token(username, password, host="http://localhost:8080", realm="master", client_id="admin-cli"):
    """
    Makes a request against the Keycloak openid-connect/token endpoint using a direct access grant to get a token.

    Returned JSON objects will look like this:
    {'access_token': 'ey...2w', 'expires_in': 60, 'refresh_expires_in': 1800,
    'refresh_token': 'ey..Og', 'not-before-policy': 0, 'session_state': '5ca9ccf7-b425-4fe8-81a1-8bbd770ee312'}

    @param username: user for which the token is to be granted
    @param password: user's password
    @param host: full hostname with protocol of the keycloak auth server
    @param realm: realm against which the direct access grant will be made
    @param client_id: client argument for the direct access grant request
    @return: json object representing token Response
    @raise: AuthException if a non-200 response is returned by the token endpoint
    """
    token_request_data = {'grant_type': 'password',
                          'client_id': client_id, 'username': username, 'password': password}
    token_request_url = "{0}/auth/realms/{1}/protocol/openid-connect/token".format(
        host, realm)
    token_response = requests.post(token_request_url, data=token_request_data)

    if token_response.status_code != 200:
        raise AuthException(
            'Non-200 Response returned from direct access grant attempt: {}'.format(token_response.status_code))

    return json.loads(token_response.text)


class AuthException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
