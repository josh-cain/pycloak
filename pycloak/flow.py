
import requests
import json
from pycloak import execution

class Flow:

    def __init__(self, realm, json_rep=None, dict_rep=None):
        """
        Instantiates a representation of a Keycloak authentication flow.

        :param realm: pycloak realm object to which this flow belongs.
        :param json_rep: json representation of the authentication flow.  Given priority over dict_rep if both are provided.
        :param dict_rep: dictionary representation of the authentication flow.  Discarded if json_rep is provided.
        """
        if not json_rep and dict_rep:
            json_rep = json.loads(json.dumps(dict_rep))

        self.realm = realm
        self.id = json_rep.get('id')
        self.json = json_rep

    # TODO this just occurred to me... the '$host/auth' path can be changed.  should be parameterized!
    # Might be useful to make static url-maker methods in all the respective classes for this?
    def executions(self, provider=None):
        """
        Retrieves list of all executions for this authentication flow

        :return: json list of executions associated with this authentication flow
        """
        # TODO see if the ID can be used instead, no idea why KC console decided to use alias for REST path for executions
        # http://localhost:8080/auth/admin/realms/master/authentication/flows/Test Flow/executions
        executions_url = "{0}/auth/admin/realms/{1}/authentication/flows/{2}/executions".format(self.realm.auth_session.host, self.realm.id, self.json['alias'])
        response = requests.get(executions_url, headers=self.realm.auth_session.bearer_header)

        if response.status_code != 200:
            raise AuthFlowException("could not retrieve executions for auth flow")

        executions = json.loads(response.text)
        if provider is None:
            return executions
        else:
            return list(filter(lambda execution: execution.get('providerId') == provider, executions))

    def execution(self, id=None):
        """
        Retrieves a single execution by ID.

        :param id: GUID of the execution.  I.E. 2cd14612-4901-4d94-81ca-a86729d63fab
        :return: pycloak object of the matching execution.  None if not found or no id is provided.
        """
        executions = self.executions()
        if id is not None:
            execu = next(filter(lambda execu: execu['id'] == id, self.executions()), None)
            return execution.Execution(self, json_rep=execu)

        return None


    def create_execution(self, new_execution):
        """
        Creates an execution in this flow.  Note that the execution will be added according to default Keycloak behavior and
        further customization is likely to be necessary.

        :param execution: json object representing the execution to be added to the flow.  I.E. {'provider': 'auth-username-password-form'}
        :return: arbitrary execution that shares the same provider type.  Most commonly, there will only be one execution of each type,
        so this will be reliable.  However, since Keycloak does not return a Location header on 204, there is no deterministic
        way to validate the correct execution is retrieved.  If something crazy happens None might be returned.  Just warning you.

        Will PR for this soon.
        """
        # TODO validate required "provider" field present

        url = "{0}/auth/admin/realms/{1}/authentication/flows/{2}/executions/execution".format(self.realm.auth_session.host, self.realm.id, self.json['alias'])
        response = requests.post(url, json=new_execution, headers=self.realm.auth_session.bearer_header)

        # TODO keycloak PR for this, return at least a UID or something...
        if response.status_code != 204:
            raise AuthFlowException("Error attempting to create new execution: {0}/{1}".format(response.status_code, response.text))

        best_guess = next(iter(self.executions(provider=new_execution['provider'])), None)
        if best_guess is None:
            return None
        else:
            return execution.Execution(self, json_rep=best_guess)

    def update_execution(self, execution):
        """
        Performs an update operation for an execution, matched by ID

        :return: updated execution object, as retrieved from Keycloak
        """

        url = "{0}/auth/admin/realms/{1}/authentication/flows/{2}/executions".format(self.realm.auth_session.host, self.realm.id, self.json['alias'])
        response = requests.put(url, json=execution, headers=self.realm.auth_session.bearer_header)

        if response.status_code != 204:
            raise AuthFlowException("Error attempting to update execution: {0}/{1}".format(response.status_code, response.text))

        return self.execution(id=execution['id'])

    def delete_execution(self, id):
        """
        Deletes execution specified by ID.  If not found, no error is raised.
        """
        url = "{0}/auth/admin/realms/{1}/authentication/executions/{2}".format(self.realm.auth_session.host, self.realm.id, id)
        response = requests.delete(url, headers=self.realm.auth_session.bearer_header)

        if response.status_code not in [404, 204]:
            raise AuthFlowException("Error attempting to delete execution")

        #TODO feels wrong - return something else here
        return response

    def delete_all_executions(self):
        """
        Convenience method for remove all executions associated with this flow

        :return: fresh flow object with executions removed.
        """
        for execution in self.executions():
            self.delete_execution(execution['id'])

        return self.realm.auth_flow(id=self.id)


    def create_child_flow(self, child_flow):
        """
        Creates child flow, with the current flow as parent

        :param child_flow: json representation of the flow to create.  I.E. {'alias': 'test-sub-flow', 'type': 'basic-flow', 'description': 'Demonstrates how to configure a sub-flow', 'provider': 'registration-page-form'}
        """
        url = "{0}/auth/admin/realms/{1}/authentication/flows/{2}/executions/flow".format(self.realm.auth_session.host, self.realm.id, self.json['alias'])
        response = requests.post(url, json=child_flow, headers=self.realm.auth_session.bearer_header)

        if response.status_code != 204:
            raise AuthFlowException("Error attempting to create new execution")

        return next(iter(self.executions(provider=execution['provider'])))

    def update_child_flow(self, flow):
        """
        Just invokes update_execution.  Since both child flows and executions share the same structure, they use the same REST invocations
        """
        self.update_execution(flow)

class AuthFlowException(Exception):
    pass
