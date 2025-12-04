"""Authentication module for Chart Preparation Agent."""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chart-agent-super-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()

# Available data sources
AVAILABLE_DATA_SOURCES = ["healthlake", "epic", "athena"]


# Models
class User(BaseModel):
    """User model."""
    username: str  # Email address (defaults to email)
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    disabled: bool = False
    role: str = "user"  # "admin" or "user"
    allowed_data_sources: List[str] = ["healthlake"]  # Data sources user can access
    practitioner_id: Optional[str] = None  # Link to practitioner for auto-filtering
    practitioner_name: Optional[str] = None  # Display name of linked practitioner


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


class UserCreate(BaseModel):
    """Model for creating a new user."""
    email: str  # Username defaults to email
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "user"
    allowed_data_sources: List[str] = ["healthlake"]
    practitioner_id: Optional[str] = None
    practitioner_name: Optional[str] = None


class UserUpdate(BaseModel):
    """Model for updating a user."""
    email: Optional[str] = None  # Changing email also changes username
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    role: Optional[str] = None
    allowed_data_sources: Optional[List[str]] = None
    practitioner_id: Optional[str] = None
    practitioner_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model (without password)."""
    username: str  # Email address (displayed as username)
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    disabled: bool = False
    role: str = "user"
    allowed_data_sources: List[str] = []
    practitioner_id: Optional[str] = None
    practitioner_name: Optional[str] = None


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


# In-memory user database (for demo - use real DB in production)
# Password for admin is: ChartAgent2024!
USERS_DB = {
    "admin@chartagent.local": {
        "username": "admin@chartagent.local",
        "email": "admin@chartagent.local",
        "first_name": "System",
        "last_name": "Administrator",
        "disabled": False,
        "role": "admin",
        "allowed_data_sources": ["healthlake", "epic", "athena"],
        "practitioner_id": None,
        "practitioner_name": None,
        "hashed_password": pwd_context.hash("ChartAgent2024!")
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database."""
    if username in USERS_DB:
        user_dict = USERS_DB[username]
        return UserInDB(**user_dict)
    return None


def get_all_users() -> List[UserResponse]:
    """Get all users (without passwords)."""
    users = []
    for username, user_data in USERS_DB.items():
        users.append(UserResponse(
            username=user_data.get("username", username),
            email=user_data.get("email", username),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            disabled=user_data.get("disabled", False),
            role=user_data.get("role", "user"),
            allowed_data_sources=user_data.get("allowed_data_sources", ["healthlake"]),
            practitioner_id=user_data.get("practitioner_id"),
            practitioner_name=user_data.get("practitioner_name")
        ))
    return users


def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user."""
    # Normalize email: trim whitespace and lowercase (emails are case-insensitive)
    normalized_email = user_data.email.strip().lower() if user_data.email else ""
    if not normalized_email:
        raise ValueError("Email is required and cannot be empty")
    
    # Username defaults to normalized email
    username = normalized_email
    
    if username in USERS_DB:
        raise ValueError(f"User with email '{username}' already exists")
    
    # Validate data sources
    for source in user_data.allowed_data_sources:
        if source not in AVAILABLE_DATA_SOURCES:
            raise ValueError(f"Invalid data source: {source}")
    
    # Normalize name fields (trim whitespace)
    first_name = user_data.first_name.strip() if user_data.first_name else None
    last_name = user_data.last_name.strip() if user_data.last_name else None
    
    USERS_DB[username] = {
        "username": username,
        "email": normalized_email,
        "first_name": first_name if first_name else None,
        "last_name": last_name if last_name else None,
        "disabled": False,
        "role": user_data.role,
        "allowed_data_sources": user_data.allowed_data_sources,
        "practitioner_id": user_data.practitioner_id,
        "practitioner_name": user_data.practitioner_name,
        "hashed_password": get_password_hash(user_data.password)
    }
    
    return UserResponse(
        username=username,
        email=normalized_email,
        first_name=first_name,
        last_name=last_name,
        disabled=False,
        role=user_data.role,
        allowed_data_sources=user_data.allowed_data_sources,
        practitioner_id=user_data.practitioner_id,
        practitioner_name=user_data.practitioner_name
    )


def update_user(username: str, user_data: UserUpdate) -> UserResponse:
    """Update an existing user."""
    if username not in USERS_DB:
        raise ValueError(f"User '{username}' not found")
    
    user = USERS_DB[username]
    final_username = username
    
    # Handle email/username change
    if user_data.email is not None:
        # Normalize email: trim whitespace and lowercase
        normalized_email = user_data.email.strip().lower()
        if not normalized_email:
            raise ValueError("Email cannot be empty")
        
        if normalized_email != username:
            # Email is changing - check if new email already exists
            if normalized_email in USERS_DB:
                raise ValueError(f"User with email '{normalized_email}' already exists")
            if username == "admin@chartagent.local":
                raise ValueError("Cannot change admin email")
            # Move user to new email (username)
            USERS_DB[normalized_email] = user
            del USERS_DB[username]
            user = USERS_DB[normalized_email]
            user["username"] = normalized_email
            user["email"] = normalized_email
            final_username = normalized_email
        else:
            # Email is same but may need normalization (update stored value)
            user["email"] = normalized_email
    
    # Normalize name fields (trim whitespace)
    if user_data.first_name is not None:
        trimmed_first = (user_data.first_name or "").strip()
        user["first_name"] = trimmed_first if trimmed_first else None
    if user_data.last_name is not None:
        trimmed_last = (user_data.last_name or "").strip()
        user["last_name"] = trimmed_last if trimmed_last else None
    if user_data.password is not None:
        user["hashed_password"] = get_password_hash(user_data.password)
    if user_data.disabled is not None:
        user["disabled"] = user_data.disabled
    if user_data.role is not None:
        user["role"] = user_data.role
    if user_data.allowed_data_sources is not None:
        # Validate data sources
        for source in user_data.allowed_data_sources:
            if source not in AVAILABLE_DATA_SOURCES:
                raise ValueError(f"Invalid data source: {source}")
        user["allowed_data_sources"] = user_data.allowed_data_sources
    if user_data.practitioner_id is not None:
        user["practitioner_id"] = user_data.practitioner_id if user_data.practitioner_id != "" else None
    if user_data.practitioner_name is not None:
        user["practitioner_name"] = user_data.practitioner_name if user_data.practitioner_name != "" else None
    
    return UserResponse(
        username=final_username,
        email=user.get("email", final_username),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        disabled=user.get("disabled", False),
        role=user.get("role", "user"),
        allowed_data_sources=user.get("allowed_data_sources", ["healthlake"]),
        practitioner_id=user.get("practitioner_id"),
        practitioner_name=user.get("practitioner_name")
    )


def delete_user(username: str) -> bool:
    """Delete a user."""
    if username not in USERS_DB:
        raise ValueError(f"User '{username}' not found")
    if username == "admin@chartagent.local":
        raise ValueError("Cannot delete the admin user")
    
    del USERS_DB[username]
    return True


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user. Username can be email or actual username."""
    # Normalize input: trim whitespace and lowercase (emails are case-insensitive)
    normalized_username = username.strip().lower() if username else ""
    
    # Try normalized username first
    user = get_user(normalized_username)
    
    # Backward compatibility: "admin" -> "admin@chartagent.local"
    if not user and normalized_username == "admin":
        user = get_user("admin@chartagent.local")
    
    # Try finding by email if still not found (also normalized)
    if not user:
        for key, user_data in USERS_DB.items():
            stored_email = user_data.get("email", "").strip().lower() if user_data.get("email") else ""
            if stored_email == normalized_username:
                user = get_user(key)
                break
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
