import hashlib
import hmac
import secrets

from ..errors import ApiError


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_DIGEST = "sha256"
PBKDF2_ITERATIONS = 100_000
SALT_BYTES = 16


def hash_password(plain_text: str) -> str:
    if not plain_text:
        raise ApiError("password is required", "BAD_REQUEST", 400)

    salt = secrets.token_hex(SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        PBKDF2_DIGEST,
        plain_text.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    digest = derived_key.hex()
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(plain_text: str, stored_hash: str) -> bool:
    if not plain_text or not stored_hash:
        return False

    try:
        algorithm, iterations, salt, digest = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != PBKDF2_ALGORITHM:
        return False

    candidate = hashlib.pbkdf2_hmac(
        PBKDF2_DIGEST,
        plain_text.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(candidate, digest)
