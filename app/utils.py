import os
from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import Response
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
import app.schemas as schemas
from .config import *

def ensure_initialized(method):
    def wrapper(cls, *args, **kwargs):
        if not cls.initialized:
            raise Exception("Utils not initialized")
        return method(cls, *args, **kwargs)
    return wrapper

class Utility:
    ALGORITHM = "HS256"
    JWT_SECRET_KEY = None
    password_context = None

    SUPERUSER_PASSWORD = None

    initialized = False

    @classmethod
    def initialize(cls):
        try:
            load_dotenv()
            cls.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

            if cls.JWT_SECRET_KEY is None:
                raise Exception("JWT signing Keys not set")

            cls.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

            cls.SUPERUSER_PASSWORD = os.getenv('SUPERUSER_PASSWORD')

            cls.initialized = True
            
            print("***** APP INITIALIZED *****")
        except Exception as e:
            raise Exception("Failed to initialize utils")
        
    @classmethod
    @ensure_initialized
    def app_init_test(cls):
        print("App already initialized")

    @classmethod
    @ensure_initialized
    def get_hashed_password(cls, password: str) -> str:
        return cls.password_context.hash(password)

    @classmethod
    @ensure_initialized
    def verify_password(cls, password: str, hashed_pass: str) -> bool:
        return cls.password_context.verify(password, hashed_pass)
    
    @classmethod
    @ensure_initialized
    def verify_plain_password(cls, password: str, plain_password: str) -> bool:
        return password == plain_password

    @classmethod
    @ensure_initialized
    def create_access_token(cls, data: schemas.AccessTokenInputData, expires_delta: int = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        encoded_jwt = schemas.AccessTokenPayload(**data.model_dump(), exp=expire).model_dump()
        encoded_jwt = jwt.encode(encoded_jwt, cls.JWT_SECRET_KEY, cls.ALGORITHM)

        return encoded_jwt
    
    @classmethod
    @ensure_initialized
    def set_access_token_cookie(cls, response: Response, access_token: str):
        response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",  # can be 'strict', 'lax', or 'none'
        max_age=SESSION_EXPIRE_MINUTES * 60
    )


    @classmethod
    @ensure_initialized
    def decodeJWT(cls, jwtoken: str, options: dict[str, Any] = None) -> dict:
        try:
            # Decode and verify the token
            payload = jwt.decode(jwtoken, cls.JWT_SECRET_KEY, cls.ALGORITHM, options)
            return payload
        except jwt.ExpiredSignatureError as e:
            print(f"{jwtoken} | Token expired")
            raise e
        except jwt.InvalidTokenError as e:
            print(f"{jwtoken} | Invalid token")
            raise e
        except Exception as e:
            print(f"{jwtoken} | Token validation error")
            raise e