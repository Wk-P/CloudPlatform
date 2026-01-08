import requests
import json
from pathlib import Path
import base64
from datetime import datetime, timedelta, timezone

# DEPRECATED: Do not use global K8S_API_SERVER
# Each cluster has its own api_server, retrieve from KubeCluster model
# K8S_API_SERVER = 'https://192.168.0.247:8443/'  # OLD: hardcoded, no longer used


def load_test_token():
    test_token_file_path = Path(__file__).parent / 'k8s_test_auth_token' / 'token.json'
    
    if not test_token_file_path.exists():
        raise RuntimeError('token.json does not exist.')

    with open(test_token_file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise RuntimeError("token.json can not parse to JSON.")
    
    if not isinstance(data, list):
        raise RuntimeError("token.json format error, it should be a list.")
    
    valid_tokens = []
    for item in data:
        if not isinstance(item, dict):
            continue
        token = item.get("token")
        if not token:
            continue
        exp_time = decode_token(token).get('exp')
        if exp_time:
            valid_tokens.append((token, exp_time))

    if not valid_tokens:
        raise RuntimeError("token.json does not include valid token ")

    best_token, best_exp = max(valid_tokens, key=lambda t: t[1])
    return best_token, best_exp

def test_refresh_token():
    # DEPRECATED: Should retrieve API server from KubeCluster model instead
    # K8S_API = K8S_API_SERVER  # OLD: hardcoded global
    # K8S_API = account.k8s_api_server_url  # OLD: duplicated in K8sAccount
    from runtime_monitoring.models import KubeCluster
    cluster = KubeCluster.objects.first()
    if not cluster:
        raise RuntimeError('No cluster configured')
    K8S_API = f'https://{cluster.api_server}:{cluster.port}'
    
    PLATFORM_BEAR_TOKEN, _ = load_test_token()
    TOKEN_FILE_PATH = Path(__file__).parent / 'k8s_test_auth_token' / 'token.json'
    SERVICEACCOUNT_NAME  = 'platform-admin'
    NAMESPACE = 'my-platform'

    url = f"{K8S_API}/api/v1/namespaces/{NAMESPACE}/serviceaccounts/{SERVICEACCOUNT_NAME}/token"
    headers = {
        **token_header(PLATFORM_BEAR_TOKEN),
        'Content-Type': 'application/json'
    }
    payload = {
        'apiVersion': 'authentication.k8s.io/v1',
        'kind': 'TokenRequest',
        'spec': {
            'expirationSeconds': 3600
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, verify=False)
        resp.raise_for_status()
        data = resp.json()

        token = data["status"]["token"]
        expiration = data["status"]["expirationTimestamp"]  # ISO time string

        print("Get new token success")

        # parsing
        new_entry = {
            "token": token,
            "datetime": datetime.now().strftime("%Y-%m-%d"),
            "expiration": expiration
        }

        if TOKEN_FILE_PATH.exists():
            with open(TOKEN_FILE_PATH, 'r', encoding='utf-8') as f:
                token_list = json.load(f)
        else:
            token_list = []

        # add and save
        token_list.append(new_entry)

        with open(TOKEN_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(token_list, f, indent=4)

        print("Saved into token.json")

    except Exception as e:
        print(f"[ERROR] Refresh token failed for {SERVICEACCOUNT_NAME}: {e}")
        raise


def decode_token(token: str):
    payload = token.split('.')[1]

    payload += '=' * (-len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload)
    payload_data: dict = json.loads(decoded)

    return payload_data


def is_token_expiring_soon(token: str, buffer_minutes=5):
    expire_timestamp = decode_token(token).get('exp', datetime.now())

    expire_time  = datetime.fromtimestamp(expire_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)

    return expire_time < (now + timedelta(minutes=buffer_minutes))

# def get_valid_token(account: K8sAccount):
#     if not account.token or not account.token_expire_time:
#         return

def token_header(token: str):
    return {
        'Authorization': f'Bearer {token}'
    }

def test_https_width_token():
    try:
        token, _ = load_test_token()
        from runtime_monitoring.models import KubeCluster
        cluster = KubeCluster.objects.first()
        if not cluster:
            print('No cluster configured')
            return
        api_url = f'https://{cluster.api_server}:{cluster.port}/api'
        headers = {**token_header(token)}
        resp = requests.get(api_url, headers=headers, verify=False)
        print(resp.text)

    except RuntimeError as e:
        print(e)
        exit(1)

if __name__ == "__main__":
    while True:
        print('1. Check token expiring.')
        print('2. Test token validation.')
        print('3. Refresh token (Test).')
        print('4. Exit')
        print('=============')
        input_str= input('Input the number of function: ')
        if input_str == '1':
            token, _ = load_test_token()
            print('Token expiration:', is_token_expiring_soon(token))
            print('\n', end='')
        elif input_str == '2':
            test_https_width_token()
        elif input_str == '3':
            sure_str = input("Make sure refresh(create) new token? [yes/no](default is N): ")
            if sure_str in ('y', 'Y', 'yes', 'Yes', 'YEs', 'YES') :
                test_refresh_token()
            else:
                print('Refresh cancelled.\n')
        elif input_str == '4':
            print('=> BYE\n')
            break
        else:
            print("Not valid number. Input again please\n")
