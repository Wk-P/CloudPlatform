import datetime
import json
import hmac
import hashlib
import base64
from functools import wraps
from django.http import JsonResponse
from django.conf import settings


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def _b64url_decode(data_str: str) -> bytes:
    padding = '=' * (-len(data_str) % 4)
    return base64.urlsafe_b64decode(data_str + padding)


def jwt_encode(payload: dict) -> str:
    # header
    header = {"alg": "HS256", "typ": "JWT"}
    # exp (unix ts)
    exp_dt = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_SETTINGS.get('EXP_MINUTES', 60))
    body = {**payload, 'exp': int(exp_dt.timestamp())}

    secret = (settings.JWT_SETTINGS.get('SECRET') or settings.SECRET_KEY).encode('utf-8')
    signing_input = f"{_b64url(json.dumps(header, separators=(',', ':')).encode())}.{_b64url(json.dumps(body, separators=(',', ':')).encode())}"
    sig = hmac.new(secret, signing_input.encode('ascii'), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url(sig)}"


def jwt_decode(token: str) -> dict:
    try:
        header_b64, payload_b64, sig_b64 = token.split('.')
    except ValueError:
        raise ValueError('Malformed token')

    secret = (settings.JWT_SETTINGS.get('SECRET') or settings.SECRET_KEY).encode('utf-8')
    signing_input = f"{header_b64}.{payload_b64}".encode('ascii')
    expected_sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
        raise ValueError('Invalid signature')

    payload = json.loads(_b64url_decode(payload_b64))
    exp = payload.get('exp')
    if exp is not None and int(exp) < int(datetime.datetime.utcnow().timestamp()):
        raise ValueError('Token expired')
    return payload


def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not settings.JWT_SETTINGS.get('ENFORCE', False):
            return view_func(request, *args, **kwargs)

        auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth or not auth.startswith('Bearer '):
            return JsonResponse({'detail': 'Unauthorized'}, status=401)
        token = auth.split(' ', 1)[1]
        try:
            request.jwt_payload = jwt_decode(token)
        except Exception as e:
            return JsonResponse({'detail': f'Invalid token: {e}'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped
