import base64
import hashlib

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash(plain: str) -> str:
    digest = hashlib.sha256(plain.encode()).digest()
    return base64.b64encode(digest).decode()


def hash_password(plain: str) -> str:
    return _pwd_context.hash(_prehash(plain))


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(_prehash(plain), hashed)