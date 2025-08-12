import json, requests
from auth import load_test_token, K8S_API_SERVER

def get_cluster_info(api_server: str):
    token, _ = load_test_token()

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    endpoints = [
        '/version',
        '/api',
        '/apis',
        '/api/v1/nodes',
        '/api/v1/namespaces'
    ]

    for endpoint in endpoints:
        print(f"\n==== {endpoint} ====")
        try:
            resp = requests.get(f"{api_server.rstrip('/')}{endpoint}", headers=headers, verify=False)
            print(f"[{resp.status_code}] {resp.url}")
            print(resp.json())
        except Exception as e:
            print(f"❌ Failed to access {endpoint}: {e}")
    


if __name__ == "__main__":
    get_cluster_info(K8S_API_SERVER)