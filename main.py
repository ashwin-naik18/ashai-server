from fastapi import FastAPI, HTTPException, Depends, Header
from model import User, APIKey, ChatRequest, UsageLog
from database import Base, engine, session_local
from scheme import userCreate, userLogin
from security import *
from rate_limiter import check_rate_limit as redis_check_rate_limit
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from langchain_ollama import ChatOllama


Base.metadata.create_all(bind=engine)

app = FastAPI()


ALLOWED_MODELS = [
    "llama3.1:latest",
    "qwen2.5-coder:14b"
]


@app.get("/")
def home():
    return{
        "message" : "Welcome To AI API Platform"
    }
    

@app.post("/register")
def register(user : userCreate):
    db = session_local()
    
    try:
        response = db.query(User).filter(User.email == user.email).first()
        
        if response:
            raise HTTPException(
                status_code=409,
                detail=f"User with email {user.email} already exists"
            )
            
        new_user = User(
            username = user.username,
            email = user.email,
            password = get_hased(user.password),
            phone_no = user.phone_no
        )
        
        db.add(new_user)
        
        db.commit()
        
        db.refresh(new_user)
        
        print(new_user.id)
        print(new_user.is_active)
        print(new_user.username)
        
        return {
            "message" : "User Registered Successfully",
            "id" : new_user.id,
            "username" : new_user.username
        }
    
    except HTTPException :
        raise
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
        
    finally:
        db.close()
        
        
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends() 
):
    db = session_local()
    
    try:
        response = db.query(User).filter(User.email == form_data.username).first()
        
        if response:
            if verify_password(response.password, form_data.password):
                key = get_jwt_token({'sub' : str(response.id)})
                return{
                    "access_token" : key,
                    "token_type" : "bearer"
                }
                
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid password"
                )
                
        else:
            raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
            )
            
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
        
        
@app.get("/me")
def me(
    user = Depends(current_user)
):
    return user


@app.post("/generate_key")
def generate_api_key(
    current_user = Depends(current_user)
):  
    try:
        db = session_local()
        
        api_key = create_api_key()
        
        key = APIKey(
            api_key = api_key,
            user_id = current_user.id
        )
        
        db.add(key)
        db.commit()
        db.refresh(key)
        
        return{
            "message" : "API key generated successfully",
            "api_key" : str(api_key)
        }
        
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
        
    finally:
        db.close()
        
        
@app.get("/api_keys")
def all_api_key(
    current_user = Depends(current_user)
):
    try:
        db = session_local()
        
        response = db.query(APIKey).filter(current_user.id == APIKey.user_id).all()
        
        a = []
        
        for user in response:
            a.append({
                "id" : user.id,
                "api_key" : user.api_key,
                "is_active" : user.is_active,
                "time_stamp" : user.created_at
            })
        
        return {
            "All API Key" : a
        }
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
        
    finally :
        db.close()
        
        
@app.put("/disable_user")
def disable_user(
    current_user = Depends(current_user)
):
    try:
    
        db = session_local()
        
        user = db.query(User).filter(User.id == current_user.id).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="User is already disabled"
            )
        
        user.is_active = False
        
        db.query(APIKey).filter(APIKey.user_id == current_user.id).update(
            {"is_active" : False}
        )  
        
        db.commit()  
    
        return{
            "message" : "User Disabled successfully.."
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
        
    finally:
        db.close()
        
        
@app.get("/test")
def test(
    api_key : str = Header(..., alias='x-api-key')
):
    return {
        "api key" : api_key
    }
    
    
@app.post("/chat")
def chat(
    request : ChatRequest,
    response = Depends(api_user)
):
    db = None
    try:
        if request.model not in ALLOWED_MODELS:
            raise HTTPException(
                status_code=400,
                detail="Bad Request"
            )
            
        user = response[0]
        api_key_id = response[1]
        
        db = session_local()
        
        result = redis_check_rate_limit(api_key_id)
        
        if not result["allowed"]:
            raise HTTPException(
                status_code=429,
                detail="Too mant request. Daily API request limit exceeded."
            )
        
        if result['allowed']:
            
            llm = ChatOllama(model=request.model)
            
            content = request.message
            
            res = llm.invoke(content)
            
            
            new_row = UsageLog(
                user_id = user.id,
                api_key_id = api_key_id,
                request = request.message,
                response = res.content
            )
            
            db.add(new_row)
            
            db.commit()
            
            db.refresh(new_row)
            
            return{
                "request" : str(request.message),
                "response" : str(res),
                "user_id" : user.id,
                "status_code" : 200
            }
            
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
        
    
    finally : 
        if db is not None:
            db.close()
        
        
@app.get("/usage")
def usage(
    user = Depends(api_user)
):
    api_id = user[1]
    
    usage = get_usage(api_id)
    
    return{
        "api_id" : api_id,
        "usage" : usage
    }
    
