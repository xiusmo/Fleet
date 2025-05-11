from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import uuid

from jose import JWTError, jwt
import bcrypt

from app.utils.load_keys import load_private_key, load_public_key
from shared.core.config import settings

ALGORITHM = "RS256"

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """创建JWT令牌"""
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    pwd_bytes = plain_password.encode('utf-8')
    
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode('utf-8')
    else:
        hashed_bytes = hashed_password
        
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')


def create_fleet_jwt(audience: str, issuer: str = "fleet") -> str:
    # 动态加载私钥，确保 setup_node_keys 执行后可以读取
    try:
        private_key = load_private_key(f"config/{settings.CURRENT_NODE}/private.pem")
    except FileNotFoundError:
        raise RuntimeError("Private key not configured on this node")
    now = datetime.utcnow()
    payload = {
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": str(uuid.uuid4())
    }
    return jwt.encode(payload, private_key, algorithm=ALGORITHM)


def verify_fleet_jwt(token: str, expected_audience: str) -> dict:
    try:
        unverified = jwt.get_unverified_claims(token)
        issuer = unverified.get("iss")
        if not issuer:
            raise ValueError("Token missing issuer claim")
        
        # 动态加载公钥，不使用缓存的TRUSTED_KEYS
        try:
            public_key = load_public_key(issuer)
            return jwt.decode(token, public_key, algorithms=[ALGORITHM], audience=expected_audience)
        except FileNotFoundError:
            raise ValueError(f"Issuer {issuer} not in trusted list")
    except JWTError as e:
        raise ValueError(f"Token validation failed: {str(e)}")