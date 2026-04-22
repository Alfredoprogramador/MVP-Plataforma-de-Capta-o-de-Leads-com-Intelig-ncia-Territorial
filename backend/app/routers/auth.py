from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import LoginRequest, TokenOut, UserOut, UserCreate, ChangePasswordRequest
from ..services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    token = authorization.split(" ", 1)[1]
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    user = auth_service.get_user_by_username(db, payload.get("sub", ""))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")
    return user


def get_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    token = auth_service.create_access_token({"sub": user.username})
    return TokenOut(
        access_token=token,
        username=user.username,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not auth_service.verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    current_user.hashed_password = auth_service.hash_password(payload.new_password)
    db.commit()
    return {"detail": "Senha alterada com sucesso"}


@router.get("/users", response_model=list[UserOut])
def list_users(current_user=Depends(get_admin_user), db: Session = Depends(get_db)):
    from ..models import User
    return db.query(User).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, current_user=Depends(get_admin_user), db: Session = Depends(get_db)):
    existing = auth_service.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=409, detail="Usuário já existe")
    return auth_service.create_user(
        db,
        username=payload.username,
        password=payload.password,
        full_name=payload.full_name or "",
        email=payload.email or "",
        is_admin=payload.is_admin,
    )
