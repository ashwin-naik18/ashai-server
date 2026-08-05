import bcrypt
from datetime import timedelta, timezone, datetime
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from database import Base, engine, session_local
from model import User, APIKey, UsageLog
import secrets
from fastapi import Header
from model import APIKey
import time
import datetime


oAuth2_shceme = OAuth2PasswordBearer(tokenUrl="/login")


SECRET_KEY = "ASH IS THE BEST"
ALGORITHM = "HS256"
EXPIRE_TIME = 30

salt = bcrypt.gensalt()

def get_hased(password: str):
    password = password.encode("utf-8")
    return bcrypt.hashpw(password, salt).decode("utf-8")


def verify_password(hashed: str, plain: str):
    hashed = hashed.encode('utf-8')
    plain = plain.encode('utf-8')
    
    return bcrypt.checkpw(plain, hashed)


def get_jwt_token(data: dict):
    payload = data.copy()
    
    current_time = datetime.datetime.now(timezone.utc)
    
    exp_time = current_time + timedelta(minutes=30)
    
    payload["exp"] = exp_time

    key = jwt.encode(
        payload, 
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return key


def current_user(
    token: str = Depends(oAuth2_shceme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        user_id = payload.get("sub")
        
        db = session_local()
        
        response = db.query(User).filter(User.id == user_id).first()
        
        if not response:
            raise HTTPException(
                status_code=401,
                detail="User Doesn't exists"
            )
            
        if not response.is_active:
            raise HTTPException(
                status_code=403,
                detail="Account is Disabled.."
            )
        
        return response
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
        
    except HTTPException:
        raise
    
    except Exception as e:
        print(e)
        return{
            "error" : f"{str(e)}"
        }
        
    finally:
        db.close()
        
        

def create_api_key():
    api = secrets.token_hex(20)
    api = "ash-ai_" + api
    
    return api
    
    
def api_user(
    api_key : str = Header(..., alias='x-api-key')
):
    try:
        db = session_local()
        
        res = db.query(APIKey).filter(APIKey.api_key == api_key).first()
        
        
        if not res or not res.is_active:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
            
        user = db.query(User).filter(User.id == res.user_id).first()
        
        return [user, res.id]
        
    except HTTPException:
        raise
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    
    finally:
        db.close()
        

def get_usage(api_key_id):
    try:
        db = session_local()
        
        res = db.query(UsageLog).filter(UsageLog.api_key_id == api_key_id).all()
        
        if not res:
            raise HTTPException(
                status_code=404,
                detail="NO api key found"
            )
        
        l = []
        
        for use in res:
            l.append({
                "api_key_id" : api_key_id,
                "request" : use.request,
                "response" : use.response
            })
            
        return l
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
        
    finally:
        db.close()
        
        
LIMIT = 100

def check_rate_limit(api_key_id):
    start_of_today = datetime.datetime.now().date()
    try:
        db = session_local()
        
        total_rows = db.query(UsageLog).filter(
            UsageLog.api_key_id == api_key_id,
            UsageLog.created_at >= start_of_today
        ).count()
        
        if total_rows > LIMIT:
            raise HTTPException(
                status_code=429,
                detail="API request Exhausted"
            )
            
        return True

        
    except HTTPException:
        raise
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
        
    finally:
        db.close()