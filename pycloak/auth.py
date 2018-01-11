
import json
import jwt
import logging
import requests
import time
import urllib.parse
import urllib.request

logger = logging.getLogger('pycloak.auth')


def direct_access_grant_token(username, password, host="http://localhost:8080", realm="master", client_id="admin-cli", include_offline=False):
    """
    Makes a request against the Keycloak openid-connect/token endpoint using a direct access grant to get a token.

    Returned JSON objects will look like this:
    {'access_token': 'ey...2w', 'expires_in': 60, 'refresh_expires_in': 1800, 'refresh_token': 'ey..Og', 'not-before-policy': 0, 'session_state': '5ca9ccf7-b425-4fe8-81a1-8bbd770ee312', 'token_type': 'bearer'}

    @param username: user for which the token is to be granted
    @param password: user's password
    @param host: full hostname with protocol of the keycloak auth server
    @param realm: realm against which the direct access grant will be made
    @param client_id: client argument for the direct access grant request
    @param include_offline: denotes whether or not to include the parameter for an offline token request.
    @return: json object representing token Response
    @raise: AuthException if a non-200 response is returned by the token endpoint
    """
    token_request_data = {'grant_type': 'password', 'client_id': client_id, 'username': username, 'password': password}
    if include_offline:
        token_request_data['scope'] = 'offline_access'
    token_request_url = "{0}/auth/realms/{1}/protocol/openid-connect/token".format(host, realm)
    token_response = requests.post(token_request_url, data=token_request_data)

    if token_response.status_code != 200:
        raise AuthException('Non-200 Response returned from direct access grant attempt: {}'.format(token_response.status_code))

    return json.loads(token_response.text)

def offline_token(offline_token , host="http://localhost:8080", realm="master", client_id="admin-cli", include_offline=False):
    token_request_data = {'grant_type': 'refresh_token', 'client_id': client_id, 'refresh_token': offline_token}

    if include_offline:
        token_request_data['scope'] = 'offline_access'
    token_request_url = "{0}/auth/realms/{1}/protocol/openid-connect/token".format(host, realm)
    token_response = requests.post(token_request_url, data=token_request_data)

    if token_response.status_code == 400:
        raise AuthException('400/Bad Request returned.  Validate that the client allows this kind of grant and the calling user has the offline_access role (and it is effective for the client)')
    if token_response.status_code != 200:
        raise AuthException('Non-200 Response returned from offline token refresh attempt: {}'.format(token_response.status_code))

    return json.loads(token_response.text)

def is_expired(token):
    """
    Takes a base-64 encoded representation of a JSON web token and determines if it is expired.  Note that this is the *only* check it performs.

    @param token: base-64 encoded representation of JWT
    @return: true if expired, false if non-expired
    """
    decoded_jwt = jwt.decode(token, verify=False)
    try:
        exp = int(decoded_jwt['exp'])
    except ValueError:
        logging.error('Could not determine token expiry using "exp" claim.  Pleave validate that valid tokens are being returned from the endpoint.')
        raise AuthException("Could not determine token expiry")

    return exp < int(time.time())

class AuthSession:

    __access_token = None

    def __init__(self, username=None, password=None, offline_token=None, host="http://localhost:8080", realm="master", client_id="admin-cli"):
        if offline_token is None and (username is None or password is None):
            raise AuthException("Unable to authenticate, no form of credentials provided.  Please supply either a username/password pair or offline token.")

        self.username = username
        self.password = password
        self.token = offline_token
        self.host = host
        self.realm = realm
        self.client_id = client_id

    #TODO should be using refresh tokens instead of direct access grants for re-auth every time
    def get_access_token(self):
        if self.__access_token is None or is_expired(self.__access_token):
            if self.token is not None:
                logging.debug('Using offline token grant to acquire access token.')
                token_response = offline_token(self.offline_token, self.host, self.realm, self.client_id)
            else:
                logging.debug('Using direct access grant to acquire access token.')
                token_response = direct_access_grant_token(self.username, self.password, self.host, self.realm, self.client_id)

            self.__access_token = token_response['access_token']

        return self.__access_token

    def bearer_header(self):
        return {'Authorization': "Bearer {}".format(self.get_access_token())}

    access_token = property(get_access_token)
    bearer_header = property(bearer_header)

class AuthException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
