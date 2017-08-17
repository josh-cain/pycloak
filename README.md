# Pycloak
### A Simple Keycloak Admin API interface in Python

This Python package is for interacting with the Keycloak admin interface.

### Hacking

Required libraries:

 - PyJWT

Stand up a KC server locally:
```
docker run --rm -it -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=password -p 8080:8080 jboss/keycloak
```
