from kubernetes import client
from django.conf import settings


def _configure(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    tls = getattr(settings, 'K8S_TLS', {}) or {}
    verify = tls.get('VERIFY_SSL', False)
    configuration.verify_ssl = verify
    ca = tls.get('CA_CERT')
    if verify and ca:
        configuration.ssl_ca_cert = ca
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return configuration


def get_core_client(api_server, port, token):
    _configure(api_server, port, token)
    return client.CoreV1Api()


def get_apps_client(api_server, port, token):
    _configure(api_server, port, token)
    return client.AppsV1Api()


def get_batch_client(api_server, port, token):
    _configure(api_server, port, token)
    return client.BatchV1Api()


def get_autoscaling_client(api_server, port, token):
    _configure(api_server, port, token)
    return client.AutoscalingV1Api()


def get_networking_client(api_server, port, token):
    _configure(api_server, port, token)
    return client.NetworkingV1Api()


def get_rbac_client(api_server, port, token):
    _configure(api_server, port, token)
    return client.RbacAuthorizationV1Api()


def get_extensions_client(api_server, port, token):
    _configure(api_server, port, token)
    return client.ApiextensionsV1Api()
