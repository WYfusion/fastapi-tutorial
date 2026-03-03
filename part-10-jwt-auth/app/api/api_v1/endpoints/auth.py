from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from app import crud
from app import schemas
from app.api import deps
from app.core.auth import (
    authenticate,
    create_access_token,
)
from app.models.user import User

router = APIRouter()


@router.post("/login")
def login(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Get the JWT for a user with data from OAuth2 request form body.
    """

    # 这里是接受来自于前端的登录请求，包含用户名和密码。我们使用 authenticate 函数来验证用户的凭据。
    # 前端的请求中的用户名后端这里当作了email来处理，所以 authenticate 函数会在数据库中查找对应的用户记录，并验证密码是否正确。
    # part-10-jwt-auth/app/core/auth.py的26-31行 db.query(User).filter(User.email == email).first() 作用是找到User.email字段和前端传过来的用户名相匹配的第一个用户记录。
    # 也就是说，前端传过来的用户名应该是用户的email地址。
    # 
    user = authenticate(email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {
        "access_token": create_access_token(sub=user.id),
        "token_type": "bearer",
    }


@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: User = Depends(deps.get_current_user)):
    """
    Fetch the current logged in user.
    """

    user = current_user
    return user


@router.post("/signup", response_model=schemas.User, status_code=201)
def create_user_signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """

    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user = crud.user.create(db=db, obj_in=user_in)

    return user
