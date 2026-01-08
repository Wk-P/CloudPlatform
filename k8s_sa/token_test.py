from math import exp
import requests
import json
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# read token and url from config.json
def load_config():
    with open(Path(__file__).parent / 'config.json', 'r') as f:
        config = json.load(f)
    token = config['token']
    url = config['endpoint']
    separator = '-'*10
    return token, url, separator

def test_api_server(url, token, separator):
    resp = requests.get(f"{url}/api", headers={"Authorization": f"Bearer {token}"}, verify=False)
    print('Test API Server connection')
    print("Status:", resp.status_code)
    print(json.dumps(resp.json(), indent=4)) 
    print(separator)

def test_cluster(url, token, separator):
    resp = requests.get(f"{url}/version", headers={"Authorization": f"Bearer {token}"}, verify=False)
    print('Test cluster info GET')
    print("Status:", resp.status_code)
    print(json.dumps(resp.json(), indent=4)) 
    print(separator)


def test_pods(url, token, separator):
    resp = requests.get(f"{url}/api/v1/pods", headers={"Authorization": f"Bearer {token}"}, verify=False)
    print('Test cluster pods info GET')
    print("Status:", resp.status_code)
    data = resp.json()
    for item in data.get("items", []):
        name = item["metadata"]["name"]
        namespace = item["metadata"]["namespace"]
        status = item["status"]["phase"]
        print(f"[{namespace}] {name}: {status}")
    print(separator)


def test_nodes(url, token, separator):
    resp = requests.get(f"{url}/api/v1/nodes", headers={"Authorization": f"Bearer {token}"}, verify=False)
    print('Test cluster nodes info GET')
    print("Status:", resp.status_code)
    data = resp.json()
    for node in data.get("items", []):
        name = node["metadata"]["name"]
        status_list = node["status"]["conditions"]
        ready_condition = next((c for c in status_list if c["type"] == "Ready"), {})
        ready_status = ready_condition.get("status", "Unknown")
        print(f"{name}: Ready={ready_status}")
    print(separator)

if __name__ == "__main__":
    token, url, separator = load_config()
    try:
        test_api_server(url=url, token=token, separator=separator)
    except Exception as e:
        print("Failed to connect to API server:", e)
        exit(1)
    try:
        test_cluster(url=url, token=token, separator=separator)
    except Exception as e:
        print("Failed to get cluster info:", e)
        exit(1)
    try:
        test_pods(url=url, token=token, separator=separator)
    except Exception as e:
        print("Failed to get pods info:", e)
        exit(1)
    try:
        test_nodes(url=url, token=token, separator=separator)
    except Exception as e:
        print("Failed to get nodes info:", e)
        exit(1)