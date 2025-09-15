"""
FastAPI Authentication API for Chatbot
Clean authentication system with customer_id, email, and password
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn
from datetime import datetime, timedelta
import jwt
import secrets
import hashlib
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

load_dotenv()

def send_password_reset_email(email: str, token: str):
    """Sends a password reset email to the user."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_host, smtp_port, smtp_user, smtp_password]):
        print("SMTP settings not configured. Cannot send email.")
        return

    reset_link = f"http://localhost:8000/auth/reset-password?token={token}"  # Replace with your frontend URL

    msg = EmailMessage()
    msg.set_content(f"Please use the following link to reset your password: {reset_link}")
    msg["Subject"] = "Password Reset Request"
    msg["From"] = smtp_user
    msg["To"] = email

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot Authentication API",
    description="A clean authentication system for chatbots with customer_id, email, and password",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chatbot_auth")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]

# Pydantic models
class UserSignup(BaseModel):
    customer_id: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    customer_id: str
    password: str

class PasswordReset(BaseModel):
    customer_id: str

class NewPassword(BaseModel):
    token: str
    new_password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    customer_id: str
    email: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = users_collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True

def validate_customer_id(customer_id: str) -> bool:
    """Validate customer ID format"""
    if len(customer_id) < 6 or len(customer_id) > 20:
        return False
    if not customer_id.isalnum():
        return False
    return True

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chatbot Authentication API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    """User registration endpoint"""
    try:
        # Validate customer_id format
        if not validate_customer_id(user_data.customer_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID must be 6-20 alphanumeric characters"
            )
        
        # Validate password strength
        if not validate_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, and number"
            )
        
        # Check if customer_id already exists
        existing_user = users_collection.find_one({"customer_id": user_data.customer_id})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID already exists"
            )
        
        # Check if email already exists
        existing_email = users_collection.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create user document
        user_doc = {
            "customer_id": user_data.customer_id,
            "email": user_data.email,
            "password": hash_password(user_data.password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "email_verified": False,
            "reset_tokens": []
        }
        
        # Insert user
        result = users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            # Create access token
            access_token = create_access_token(data={"sub": str(result.inserted_id)})
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=str(result.inserted_id),
                    customer_id=user_data.customer_id,
                    email=user_data.email,
                    created_at=user_doc["created_at"]
                )
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """User login endpoint"""
    try:
        # Find user by customer_id
        user = users_collection.find_one({"customer_id": user_data.customer_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid customer ID or password"
            )
        
        if not user.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Verify password
        if not verify_password(user_data.password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid customer ID or password"
            )
        
        # Update last login
        users_collection.update_one(
            {"_id": user['_id']},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user['_id'])})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(user['_id']),
                customer_id=user['customer_id'],
                email=user['email'],
                created_at=user['created_at']
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/auth/forgot-password")
async def forgot_password(reset_data: PasswordReset):
    """Generate password reset token"""
    try:
        user = users_collection.find_one({"customer_id": reset_data.customer_id})
        if not user:
            # Don't reveal if user exists or not
            return {"message": "If the customer ID exists, reset instructions have been sent"}
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Store token in user document
        users_collection.update_one(
            {"_id": user['_id']},
            {
                "$push": {
                    "reset_tokens": {
                        "token": token,
                        "expires_at": expires_at,
                        "used": False
                    }
                }
            }
        )
        
        # Send email with reset link
        send_password_reset_email(user["email"], token)
        
        return {"message": "If the customer ID exists, reset instructions have been sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/auth/reset-password")
async def reset_password(password_data: NewPassword):
    """Reset password using token"""
    try:
        # Validate new password
        if not validate_password(password_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, and number"
            )
        
        # Find user with valid token
        user = users_collection.find_one({
            "reset_tokens": {
                "$elemMatch": {
                    "token": password_data.token,
                    "expires_at": {"$gt": datetime.utcnow()},
                    "used": False
                }
            }
        })
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        # Hash new password
        hashed_password = hash_password(password_data.new_password)
        
        # Update password and mark token as used
        users_collection.update_one(
            {
                "_id": user['_id'],
                "reset_tokens.token": password_data.token
            },
            {
                "$set": {
                    "password": hashed_password,
                    "updated_at": datetime.utcnow(),
                    "reset_tokens.$.used": True
                }
            }
        )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user['_id']),
        customer_id=current_user['customer_id'],
        email=current_user['email'],
        created_at=current_user['created_at']
    )

@app.post("/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user['password']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if not validate_password(password_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, and number"
            )
        
        # Hash new password
        hashed_password = hash_password(password_data.new_password)
        
        # Update password
        users_collection.update_one(
            {"_id": current_user['_id']},
            {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout endpoint"""
    # In a stateless JWT system, logout is handled client-side
    # You could implement token blacklisting here if needed
    return {"message": "Logged out successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
