"""Private S3-compatible storage for HER POV purchases.
Supports Cloudflare R2 and other S3 services. No customer-facing object URLs.
Never write eBooks into a public directory or code repository.
"""
import io
import os
import hashlib
from urllib.parse import urlparse

KINDS = {"ebook": "ebook.pdf", "bonus": "bonus.pdf"}
# SHA256 fingerprints of the original verified 56-page ebook and 1-page bonus.
EXPECTED_SHA256 = {
    "ebook": "ed41a473601fc4878093365b42f6960f974c9fa6fb41e30f4dd1e0c84be31693",
    "bonus": "353cbbdf6109f65d46a3fd88502ec12b16b06e09f19f581c85f4b60fd61decd2",
}
KEY_PREFIX = "her-pov/volume-01/"

def _env(key):
    return os.environ.get(key, "").strip()

def configured():
    required = ("S3_ENDPOINT_URL", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY", "S3_BUCKET")
    endpoint = _env("S3_ENDPOINT_URL")
    parsed = urlparse(endpoint)
    return (all(_env(k) for k in required) and parsed.scheme == "https"
            and bool(parsed.hostname) and not parsed.username and not parsed.password)

def _client():
    if not configured():
        raise RuntimeError("Private object storage not configured")
    import boto3
    return boto3.client("s3", endpoint_url=_env("S3_ENDPOINT_URL"),
                        aws_access_key_id=_env("S3_ACCESS_KEY_ID"),
                        aws_secret_access_key=_env("S3_SECRET_ACCESS_KEY"),
                        region_name=_env("S3_REGION") or "auto",
                        config=__import__("botocore.config", fromlist=["Config"]).Config(
                            signature_version="s3v4", retries={"max_attempts": 3, "mode": "standard"}))

def _key(kind):
    if kind not in KINDS:
        raise ValueError("Invalid private asset kind")
    return KEY_PREFIX + KINDS[kind]

def exists(kind):
    if not configured():
        return False
    try:
        result = _client().head_object(Bucket=_env("S3_BUCKET"), Key=_key(kind))
        return (50 <= int(result.get("ContentLength", 0)) <= 15 * 1024 * 1024
                and result.get("Metadata", {}).get("sha256") == EXPECTED_SHA256[kind])
    except Exception:
        return False

def upload(kind, data):
    if len(data) < 50 or len(data) > 15 * 1024 * 1024 or not data.startswith(b"%PDF-") or b"%%EOF" not in data[-2048:]:
        raise ValueError("Invalid PDF")
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256[kind]:
        raise ValueError("File does not match the official HER POV release PDF")
    _client().put_object(Bucket=_env("S3_BUCKET"), Key=_key(kind), Body=data,
                         ContentType="application/pdf", CacheControl="private, no-store",
                         Metadata={"product": "the-first-message-formula", "kind": kind,
                                   "sha256": digest})
    return True

def read(kind):
    response = _client().get_object(Bucket=_env("S3_BUCKET"), Key=_key(kind))
    data = response["Body"].read(15 * 1024 * 1024 + 1)
    if len(data) > 15 * 1024 * 1024 or not data.startswith(b"%PDF-") or hashlib.sha256(data).hexdigest() != EXPECTED_SHA256[kind]:
        raise RuntimeError("Stored document failed integrity check")
    return io.BytesIO(data)
