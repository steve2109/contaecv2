from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from cryptography.fernet import Fernet
import re
from html import escape

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def encrypt_data(data: str) -> str:
    """Encripta datos sensibles para almacenamiento seguro"""
    if isinstance(data, str):
        data = data.encode()
    return cipher_suite.encrypt(data).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Desencripta datos sensibles"""
    if isinstance(encrypted_data, str):
        encrypted_data = encrypted_data.encode()
    return cipher_suite.decrypt(encrypted_data).decode()

def sanitize_input(value: str) -> str:
    """Sanitiza entradas de texto para prevenir XSS e inyecciones"""
    if not value:
        return ""
    # Escapar HTML
    value = escape(value)
    # Eliminar caracteres potencialmente peligrosos
    value = re.sub(r'[<>\'"`;()]', '', value)
    # Limpiar espacios múltiples
    value = re.sub(r'\s+', ' ', value).strip()
    return value

def validate_ruc(ruc: str) -> bool:
    """Valida RUC ecuatoriano"""
    if not ruc or len(ruc) != 13:
        return False
    if not ruc.isdigit():
        return False
    # Validación básica de RUC
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    provincia = int(ruc[:2])
    if provincia < 1 or provincia > 24:
        return False
    tercer_digito = int(ruc[2])
    if tercer_digito not in [0, 1, 2, 3, 4, 5, 6, 9]:
        return False
    return True
