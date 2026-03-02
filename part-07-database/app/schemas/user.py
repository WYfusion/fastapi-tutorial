from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    first_name: Optional[str]
    surname: Optional[str]
    email: Optional[EmailStr] = None
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr


# Properties to receive via API on update
class UserUpdate(UserBase):
    ...


class UserInDBBase(UserBase):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# Additional properties to return via API
class User(UserInDBBase):
    pass
