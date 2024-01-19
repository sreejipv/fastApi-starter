from fastapi import Depends, FastAPI, HTTPException
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from email.mime.text import MIMEText
import smtplib

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')    
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')     
EMAIL_APP_PASSWORD = os.environ.get('EMAIL_APP_PASSWORD')    
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')    


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587  # Use 465 for SSL

def send_password_recovery_email(email_to: str, reset_token: str):
    subject = "Password Recovery"
    body = f"Use this link to reset your password: http://your-app/reset-password?token={reset_token}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USERNAME
    msg["To"] = email_to

    with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_USERNAME, [email_to], msg.as_string())