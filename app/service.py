'''
Contains the functionalities of the API routes
'''

from uuid import uuid4
from sqlalchemy.orm import Session, joinedload

from . import models, schemas

from .utils import Utility


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, register_info: schemas.UserCredentials, role: str = 'user'):
    hashed_password = Utility.get_hashed_password(register_info.password)
    db_user = models.User(email=register_info.email, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_with_info(db: Session, register_info: schemas.RegistrationWithInfoSchema, role: str = 'user') -> bool:
    try:
        hashed_password = Utility.get_hashed_password(register_info.password)
        db_user = models.User(email=register_info.email, hashed_password=hashed_password, role=role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        user_info = models.UserInfo(fullname=register_info.fullname, designation=register_info.designation, staff_id=register_info.staff_id, user_id=db_user.id)
        db.add(user_info)
        db.commit()
        db.refresh(user_info)
        
        return True
    except Exception as e:
        print(e)
        db.rollback()

        user = get_user_by_email(db, register_info.email)
        if user:
            db.delete(user)
            db.commit()
            
        return False


def create_user_info(db: Session, user_info_create: schemas.UserInfoCreate, user_id: int):
    user_info = models.UserInfo(**user_info_create.model_dump(), user_id=user_id)
    db.add(user_info)
    db.commit()
    db.refresh(user_info)
    return user_info


def edit_user_info(db: Session, user_info_create: schemas.UserInfoCreate, user_id: int):
    user_info = db.query(models.UserInfo).filter(models.UserInfo.user_id == user_id).first()
    
    user_info.fullname = user_info_create.fullname
    user_info.designation = user_info_create.designation
    user_info.staff_id = user_info_create.staff_id

    db.commit()
    db.refresh(user_info)
    return user_info


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_user_session(db: Session, user_id: int):
    db.query(models.UserSession).filter(models.UserSession.user_id == user_id).delete()
    db.commit()


def create_user_session(db: Session, user_id: int) -> models.UserSession:
    user_session = models.UserSession(session_id = uuid4(), user_id = user_id)
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    return user_session


def get_detailed_user_info(db: Session, user_id: int) -> schemas.UserInfo | None:
    user = get_user(db, user_id)
    if user:
        user_info: models.UserInfo = user.user_info
        if user_info:
            return schemas.UserInfo(user_id=user_id, email=user.email, fullname=user_info.fullname, designation=user_info.designation, staff_id=user_info.staff_id)
        else:
            return schemas.User(user_id=user_id, email=user.email)
    return None


def get_detailed_users(db: Session, skip: int = 0, limit: int = 100) -> list[schemas.UserInfo] | list:
    all_users_hybrid_detailed_info = db.query(models.User).options(joinedload(models.User.user_info)).all()     # Fetch all users with their respective user_info avoiding N + 1 queries
    all_users_detailed_info: list[schemas.UserInfo] = []
    for hybrid_user_info in all_users_hybrid_detailed_info:
        if hybrid_user_info.user_info:
            all_users_detailed_info.append(schemas.UserInfo(
                user_id=hybrid_user_info.id, 
                email=hybrid_user_info.email, 
                fullname=hybrid_user_info.user_info.fullname,
                designation=hybrid_user_info.user_info.designation,
                staff_id=hybrid_user_info.user_info.staff_id
                ))
        else:
            all_users_detailed_info.append(schemas.User(user_id=hybrid_user_info.id, email=hybrid_user_info.email))
    return all_users_detailed_info


def get_user_by_staff_id(db: Session, staff_id: int):
    user_info = db.query(models.UserInfo).filter(models.UserInfo.staff_id == staff_id).first()
    if user_info:
        return user_info.user
    
    return None
