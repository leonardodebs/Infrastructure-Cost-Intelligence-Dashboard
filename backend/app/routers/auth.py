# Router de autenticação - endpoints de login e gestão de usuários

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from app.models.schemas import Token, User, LoginRequest
from app.services import auth

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Esquema OAuth2 para extrair token do header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency que extrai e valida o usuário atual pelo token JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth.decode_token(token)
    if payload is None:
        raise credentials_exception
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = auth.get_user(str(username))
    if user is None:
        raise credentials_exception
    return user

# Endpoint de login - recebe username/password e retorna token JWT
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = auth.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para obter dados do usuário logado
@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return User(
        username=current_user["username"],
        email=current_user.get("email"),
        full_name=current_user.get("full_name"),
        disabled=current_user.get("disabled")
    )