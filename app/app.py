import time
from fastapi import APIRouter, Cookie, Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session

from . import service, models, schemas
from .database import SessionLocal, engine

from .utils import Utility
from .authenticator import Authenticator, AuthenticationMiddleware

from .config import *

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time * 1000} ms"
    return response

### Add base route
router = APIRouter(prefix=BASE_PATH)

# =============Initialize App Utilities=============
Utility.initialize()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return "Welcome to Auth Service with FastAPI. Go to /docs to see all API routes"


# Add the authentication middleware to the app
app.add_middleware(AuthenticationMiddleware)


@router.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie(
        key="my_cookie",
        value="cookie_value",
        httponly=True,
        max_age=3600,  # cookie valid for 1 hour
        expires=3600,  # expires in 1 hour
        samesite="lax"  # can be 'strict', 'lax', or 'none'
    )
    return {"message": "Cookie has been set"}


@router.get("/get-cookie")
def get_cookie(my_cookie: str = Cookie(None)):
    if my_cookie:
        return {"this_cookie": my_cookie}
    else:
        return {"message": "No cookie found"}


@router.post("/register")
def register(register_info: schemas.UserCredentials, db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, email=register_info.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_user = service.create_user(db=db, register_info=register_info)

    if created_user:
        return {"message":"User registered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Something went wrong")
    

@router.post("/register-full")
def register_with_info(register_info: schemas.RegistrationWithInfoSchema, db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, email=register_info.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    staff_info = service.get_user_by_staff_id(db=db, staff_id=register_info.staff_id)
    if staff_info:
        raise HTTPException(status_code=400, detail="Staff id already exists")
    
    user_creation_successful = service.create_user_with_info(db=db, register_info=register_info)

    if user_creation_successful:
        return {"message":"User registered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/login")
def login(login_info: schemas.UserCredentials, response: Response, db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, email=login_info.email)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email")

    if not Utility.verify_password(login_info.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )
    
    service.delete_user_session(db=db, user_id=user.id)
    new_user_session = service.create_user_session(db=db, user_id=user.id)
    
    access_token = Utility.create_access_token(data=schemas.AccessTokenInputData(sub=user.id, role=user.role, session_id=str(new_user_session.session_id)))

    # Set the access token cookie
    Utility.set_access_token_cookie(response, access_token)

    return {"message":"Logged in successfully"}


@router.get("/logout")
def logout(response: Response, db: Session = Depends(get_db), jwt_payload: schemas.AccessTokenPayload = Depends(Authenticator())):
    service.delete_user_session(db, user_id=jwt_payload.sub)

    response.delete_cookie("access_token")

    return {"message": "Logged out successfully"}


@router.post('/change-password')
def change_password(request: schemas.UserPasswordChangeSchema, db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, request.email)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not Utility.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    new_hashed_password = Utility.get_hashed_password(request.new_password)
    user.hashed_password = new_hashed_password
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/users", response_model=list[schemas.UserInfo])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), auth_payload: schemas.AccessTokenPayload = Depends(Authenticator())):
    if auth_payload.role != 'admin':
        raise HTTPException(status_code=403, detail="Unauthorized")
    users = service.get_detailed_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.UserInfo)
def read_user(user_id: int, db: Session = Depends(get_db), auth_payload: schemas.AccessTokenPayload = Depends(Authenticator())):
    db_user = service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id == auth_payload.sub or auth_payload.role == 'admin':
        user_info = service.get_detailed_user_info(db=db, user_id=user_id)
        if user_info:
            return user_info
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve user info")
    else:
        raise HTTPException(status_code=403, detail="Cannot access other's info")
    

@router.get("/user-info", response_model=schemas.UserInfo)
def read_user_info(db: Session = Depends(get_db), auth_payload: schemas.AccessTokenPayload = Depends(Authenticator())):    
    user_info = service.get_detailed_user_info(db=db, user_id=auth_payload.sub)
    if user_info:
        return user_info
    else:
        raise HTTPException(status_code=500, detail="Failed to retrieve user info")


@router.post("/user-info", response_model=schemas.UserInfo)
def create_user_info(info: schemas.UserInfoCreate, db: Session = Depends(get_db), auth_payload: schemas.AccessTokenPayload = Depends(Authenticator())):
    user_id = auth_payload.sub
    user = service.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.user_info:
        raise HTTPException(status_code=400, detail="User info already exists")
    
    staff_info = service.get_user_by_staff_id(db=db, staff_id=info.staff_id)
    if staff_info:
        raise HTTPException(status_code=400, detail="Staff id already exists")

    user_info = service.create_user_info(db=db, user_info_create=info, user_id=user_id)
    if user_info:
        detailed_user_info = service.get_detailed_user_info(db=db, user_id=user_id)
        return detailed_user_info
    else:
        raise HTTPException(status_code=500, detail="Something went wrong")
    

@router.put("/user-info", response_model = schemas.UserInfo)
def edit_user_info(info: schemas.UserInfoCreate, db: Session = Depends(get_db), auth_payload: schemas.AccessTokenPayload = Depends(Authenticator())):
    user_id = auth_payload.sub
    user = service.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.user_info:
        raise HTTPException(status_code=404, detail="User info not found")
    
    if user.user_info.staff_id != info.staff_id:
        staff_info = service.get_user_by_staff_id(db=db, staff_id=info.staff_id)
        if staff_info:
            raise HTTPException(status_code=400, detail="Staff id belongs to someone else")

    user_info = service.edit_user_info(db=db, user_info_create=info, user_id=user_id)
    if user_info:
        detailed_user_info = service.get_detailed_user_info(db=db, user_id=user_id)
        return detailed_user_info
    else:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/superuser")
def create_super_user(superuser_credentials: schemas.SuperUserCredentials, db: Session = Depends(get_db)):
    superuser = service.get_user_by_email(db, email=superuser_credentials.email)
    if superuser:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if not Utility.verify_plain_password(superuser_credentials.superuser_password, Utility.SUPERUSER_PASSWORD):
        raise HTTPException(status_code=403, detail="Incorrect admin password")
    
    created_user = service.create_user(db=db, register_info=schemas.UserCredentials(email=superuser_credentials.email, password=superuser_credentials.password), role='admin')

    if created_user:
        return {"message":"Admin registered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Something went wrong")
    

@router.get("/authenticate", response_model=schemas.UserInfo)
def authenticate(db: Session = Depends(get_db), auth_payload: schemas.AccessTokenPayload = Depends(Authenticator())):    
    user_info = service.get_detailed_user_info(db=db, user_id=auth_payload.sub)
    if user_info:
        return user_info
    else:
        raise HTTPException(status_code=500, detail="Failed to retrieve user info")


app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)