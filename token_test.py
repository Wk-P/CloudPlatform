import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IlZfRzRrQUpOaU5iTHM1N1ZPQnk2ODlMYm8xbkZzOXRPRjlxMXRGZ2pvX1EifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzgyNDY2OTgxLCJpYXQiOjE3NTA5MzA5ODEsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiZjFmOTAyNzgtNTgxZS00ZTIwLThlNTktMjczODk2MmFjNTYwIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZWZhdWx0Iiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRqYW5nby1hZ2VudCIsInVpZCI6ImQ0N2ViNjRjLWI1ZmItNGI0Ny1iZjdiLWQwNzkyNjY2ZmQ0MiJ9fSwibmJmIjoxNzUwOTMwOTgxLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpkamFuZ28tYWdlbnQifQ.x-JIm17kazqAP6A8dW9KV8or2M-w487UuabiqKRgDG4z_C0EFKflJ9REiuIvPu7qUMAn9aK6ntkA7wvE2kIKvA0liZZiMX5O_65oAdUncfzQrsCfKUWHDzkvks4_Amk7E-4RVmOOKii3bdVzAVC03IJw-VExL7Qdv5w17ZXMYRgfneC3XJxAxrKrBhTxxD3kACxb66Iqg1vGUKNSf8pLMi0EV6cG7he5P4qIkKb3WMGCZnFzibPmyrWbtY282wZgoq2gSjXmVvRvBPxxRM8d7BAI3vd7aABi9UuO2A4vok4E2MPmpQKOzsw_BZOAgNfADzy4jmAfOjWbFLfThJCLdQ"
url = "https://192.168.0.247:8443"
separator = '-'*10

def test_api_server():
    resp = requests.get(f"{url}/api", headers={"Authorization": f"Bearer {token}"}, verify=False)
    print('Test API Server connection')
    print("Status:", resp.status_code)
    print(json.dumps(resp.json(), indent=4)) 
    print(separator)

def test_cluster():
    resp = requests.get(f"{url}/version", headers={"Authorization": f"Bearer {token}"}, verify=False)
    print('Test cluster info GET')
    print("Status:", resp.status_code)
    print(json.dumps(resp.json(), indent=4)) 
    print(separator)


def test_pods():
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


def test_nodes():
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
    test_api_server()
    test_cluster()
    test_pods()
    test_nodes()