from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

from app.models import UserSession
from .utils import Utility
import app.schemas as schemas
from .database import SessionLocal
from sqlalchemy.orm import Session

from .config import *

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Authenticator(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(Authenticator, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        request.scope['auth_required'] = True

        # First, try to get the token from the cookies
        token = request.cookies.get("access_token")

        # If no token is found in cookies, check the Authorization header
        # if not token:
        #     credentials: HTTPAuthorizationCredentials = await super(Authenticator, self).__call__(request)
        #     if credentials:
        #         if not credentials.scheme == "Bearer":
        #             raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        #         token = credentials.credentials

        # If no token is found in cookies or Authorization header, raise an error
        if not token:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

        # Verify the token
        try:
            jwt_payload = self.verify_jwt(token)
        except jwt.ExpiredSignatureError as e:      # Only refresh the token if the error is due to access token expiry
            try:
                jwt_payload = self.refresh_access_token_and_get_payload(request, token, db)
            except Exception as e:      # For any error encountered while refreshing token including session expiry, 
                # ***might not reach here since access_token cookie max_age is set to SESSION_EXPIRE_MINUTES and refresh_token function 
                # also checks expiry based on the same value, so cookie may be gone after session expiry before even coming here
                # but if in case its not gone automatically, this bit of code will handle it through the AuthenticationMiddleware
                request.state.delete_access_token = True
                raise HTTPException(status_code=403, detail="Invalid token or session.")
        except Exception as e:      # For any other error when verifying access token jwt
            request.state.delete_access_token = True
            raise HTTPException(status_code=403, detail="Invalid token or session.")
            
        return jwt_payload

    def verify_jwt(self, jwtoken: str) -> schemas.AccessTokenPayload:
        payload = Utility.decodeJWT(jwtoken)

        if payload['token_type'] == 'access':
            payload = schemas.AccessTokenPayload(**payload)
        else:   # ***Resource accessible with access token only
            # payload = Schemas.RefreshTokenPayload(**payload)
            raise jwt.InvalidTokenError

        return payload
    
    def refresh_access_token_and_get_payload(self, request: Request, access_token: str, db: Session) -> schemas.AccessTokenPayload:
        payload = Utility.decodeJWT(jwtoken=access_token, options={ "verify_exp": False })
        payload = schemas.AccessTokenPayload(**payload)

        
        def get_valid_user_session(payload: schemas.AccessTokenPayload, auto_update = False) -> UserSession | None:
            user_session = db.query(UserSession).filter(UserSession.session_id == UUID(payload.session_id)).first()

            if user_session:
                if user_session.user_id == payload.sub:
                    if user_session.created_at >= (datetime.now() - timedelta(minutes=SESSION_EXPIRE_MINUTES)):
                        if auto_update:
                            user_session.session_id = uuid4()
                            db.commit()
                            db.refresh(user_session)
                        return user_session
                    
            return None

        valid_user_session = get_valid_user_session(payload=payload)

        if not valid_user_session:
            raise jwt.InvalidTokenError
        
        # Update the session
        valid_user_session.session_id = uuid4()
        db.commit()
        db.refresh(valid_user_session)
        
        new_access_token = Utility.create_access_token(data=schemas.AccessTokenInputData(sub=payload.sub, role=payload.role, session_id=str(valid_user_session.session_id)))
        
        request.state.new_access_token = new_access_token

        return payload
    


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if the path is one that should be skipped
        if request.url.path in [f"{BASE_PATH}/logout"]:
            # Skip the middleware logic
            return await call_next(request)
        
        # Call the next middleware or endpoint handler
        response = await call_next(request)

        # Check if the request has authentication requirement
        if request.scope.get("auth_required", False):
            # Check if there's a token deletion request from authenticator dependency
            delete_access_token = getattr(request.state, 'delete_access_token', False)
            if delete_access_token:
                response.delete_cookie("access_token")
            else:   # If there's no request for deletion, there might be a request for addition
                # Check if there's a new access token in the state
                new_access_token = getattr(request.state, 'new_access_token', None)
                if new_access_token:
                    # Set the access token cookie
                    Utility.set_access_token_cookie(response, new_access_token)

        return response