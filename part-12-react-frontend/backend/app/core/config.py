import pathlib

from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union


# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    JWT_SECRET: str = "TEST_SECRET_DO_NOT_USE_IN_PROD"
    ALGORITHM: str = "HS256"

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8001",  # type: ignore
        "http://127.0.0.1:8001",  # type: ignore
    ]

    # Origins that match this regex OR are in the above list are allowed
    BACKEND_CORS_ORIGIN_REGEX: Optional[
        str
    ] = (
        r"https.*\.(netlify.app|herokuapp.com)"
        r"|http://(localhost|127\.0\.0\.1)(:\d+)?"
        r"|http://172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}(:\d+)?"
        r"|http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?"
        r"|http://10\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?"
    )  # noqa: W605

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example_part_12.db"
    FIRST_SUPERUSER: EmailStr = "admin@recipeapi.com"
    FIRST_SUPERUSER_PW: str = "CHANGEME"

    class Config:
        case_sensitive = True


settings = Settings()
