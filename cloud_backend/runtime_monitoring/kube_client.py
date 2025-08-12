from kubernetes import client

from kubernetes import client

def get_core_client(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client.CoreV1Api()

def get_apps_client(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client.AppsV1Api()

def get_batch_client(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client.BatchV1Api()

def get_autoscaling_client(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client.AutoscalingV1Api()

def get_networking_client(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client.NetworkingV1Api()

def get_rbac_client(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client.RbacAuthorizationV1Api()

def get_extensions_client(api_server, port, token):
    configuration = client.Configuration()
    configuration.host = f"https://{api_server}:{port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client.ApiextensionsV1Api()
