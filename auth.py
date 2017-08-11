
import json
import requests
import urllib.parse
import urllib.request

def direct_access_grant_token(username, password, host="http://localhost:8080", realm="master", client_id="admin-cli"):
    token_request_data = {'grant_type' : 'password', 'client_id' : client_id, 'username' : username, 'password' : password}
    token_request_url = "{0}/auth/realms/{1}/protocol/openid-connect/token".format(host, realm)
    token_response = requests.post(token_request_url, data=token_request_data)
    print(token_response.status_code)
    print(token_response.text)
