# Serviço de autenticação JWT com usuários em memória
# Em produção, substituir por banco de dados real

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Configurações do JWT - em produção, usar variável de ambiente segura
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hashing de senhas com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Verifica se a senhaplain corresponde ao hash armazenado
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Aceita senhas em texto puro para usuário admin (desenvolvimento)
    if hashed_password.startswith("$2b$"):
        return pwd_context.verify(plain_password, hashed_password)
    return plain_password == hashed_password

# Gera hash de senha para armazenamento
def get_password_hash(password: str) -> str:
    # Retorna senha em texto para admin (modo desenvolvimento)
    if password == "admin123":
        return "admin123"
    return pwd_context.hash(password)

# Cria token JWT com dados do usuário e expiração
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decodifica e valida token JWT
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Banco de usuários em memória - em produção, usar banco de dados real
MOCK_USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@cloudcostiq.com",
        "full_name": "Admin User",
        "hashed_password": "admin123",
        "disabled": False
    }
}

# Busca usuário pelo nome de usuário
def get_user(username: str):
    if username in MOCK_USERS_DB:
        user_dict = MOCK_USERS_DB[username]
        return user_dict
    return None

# Autentica usuário com nome e senha
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user