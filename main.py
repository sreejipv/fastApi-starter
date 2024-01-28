import email
from fastapi import Depends, FastAPI, HTTPException, Form, UploadFile, File
from database import db  # Import the MongoDB connection
from models import Item, PasswordRecoveryRequest, PasswordRecoveryResponse, User, UserInDB  
from fastapi import HTTPException
from bson import ObjectId  # Import ObjectId from the bson module
from passlib.context import CryptContext
import logging
from utils import create_jwt_token, get_current_user, get_hashed_password, send_password_recovery_email
from uuid import uuid4
import bcrypt



logging.basicConfig(level=logging.INFO)


app = FastAPI()

users_collection = db.get_collection("users")

# async def get_user(db, username):
#    if username in db:
#         return True


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




@app.post("/items/")
async def create_item(item: Item):
    collection = db.get_collection("items")


    # Get the name from the item before inserting it
    item_data = item.dict()
    item_name = item_data.get("name")
    result = collection.insert_one(item.dict())
    
    if result.acknowledged:
        inserted_id = str(result.inserted_id)

        return {"status": f"Item '{item_name}' '{inserted_id}' created successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create item")

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    try:
        item_object_id = ObjectId(item_id)  # Convert the item_id to ObjectId
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid item_id")

    collection = db.get_collection("items")
    item = collection.find_one({"_id": item_object_id})

    if item:
        # Convert the ObjectId to a string for JSON serialization
        item["_id"] = str(item["_id"])
        return item
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.post("/signup")
async def create_user(data: User):
    # querying database to check if user already exist
    user = users_collection.find_one({"email": data.email})
    if user is not None:
        raise HTTPException(status_code=404, detail="User already exists")
    token_data = {"sub": data.email}
    token = create_jwt_token(token_data)
    user_document = {
        'name': data.name,
        'email': data.email,
        'password': get_hashed_password(data.password),
    }

    result = users_collection.insert_one(user_document)
    return {"access_token": token, "token_type": "bearer", "inserted_id": str(result.inserted_id)}




@app.post("/login")
async def login_user(email: str= Form(...), password: str= Form(...)):
    user = users_collection.find_one({"email": email, "password": bcrypt.hash(password) })
    if not user:
        raise HTTPException(status_code=404, detail="User not exists")
    return {"Login successfull"}

@app.post("/password-recovery", response_model=PasswordRecoveryResponse)
async def recover_password(request: PasswordRecoveryRequest):
    user = users_collection.find_one({"email": request.email})
    if user:    
        token_data = {"sub": request.email}
        reset_token = create_jwt_token(token_data)        
        send_password_recovery_email(request.email, reset_token)
        return {"message": "Password recovery email sent"}
    else:
        raise HTTPException(status_code=404, detail="User not exists")



@app.get("/protected")
async def get_protected_data(current_user: str = Depends(get_current_user)):
    return {"message": "You are authenticated", "username": current_user}
