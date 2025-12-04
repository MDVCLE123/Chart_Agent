"""Cognito Authentication module for Chart Preparation Agent."""
import os
import boto3
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
import requests

# Cognito configuration
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET", "")

# Bearer token security
security = HTTPBearer()

# Cognito client
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

# Cache for JWKS
_jwks_cache = None
_jwks_url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"


# Models
class User(BaseModel):
    """User model."""
    username: str  # Cognito sub (unique ID) - but display email
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    disabled: bool = False
    role: str = "user"
    allowed_data_sources: List[str] = ["healthlake"]
    practitioner_id: Optional[str] = None
    practitioner_name: Optional[str] = None


class Token(BaseModel):
    """Token response model."""
    access_token: str
    id_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict


class LoginRequest(BaseModel):
    """Login request model."""
    username: str  # email
    password: str


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
    email: Optional[str] = None
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
    username: str  # Cognito sub (but we'll display email)
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    disabled: bool = False
    role: str = "user"
    allowed_data_sources: List[str] = []
    practitioner_id: Optional[str] = None
    practitioner_name: Optional[str] = None


def _get_secret_hash(username: str) -> str:
    """Calculate Cognito secret hash."""
    message = username + COGNITO_CLIENT_ID
    dig = hmac.new(
        COGNITO_CLIENT_SECRET.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()


def _get_jwks():
    """Get JSON Web Key Set from Cognito."""
    global _jwks_cache
    if _jwks_cache is None:
        response = requests.get(_jwks_url)
        _jwks_cache = response.json()
    return _jwks_cache


def _parse_user_attributes(attributes: list) -> dict:
    """Parse Cognito user attributes into a dictionary."""
    attr_dict = {}
    for attr in attributes:
        name = attr['Name']
        value = attr['Value']
        if name == 'sub':
            attr_dict['username'] = value
        elif name == 'email':
            attr_dict['email'] = value
        elif name == 'given_name':
            attr_dict['first_name'] = value
        elif name == 'family_name':
            attr_dict['last_name'] = value
        elif name == 'name':  # Fallback for full name
            # Try to split if it's a full name
            parts = value.split(' ', 1) if value else []
            if len(parts) == 2:
                attr_dict['first_name'] = parts[0]
                attr_dict['last_name'] = parts[1]
            elif len(parts) == 1:
                attr_dict['first_name'] = parts[0]
        elif name == 'custom:role':
            attr_dict['role'] = value
        elif name == 'custom:sources':
            attr_dict['allowed_data_sources'] = value.split('|') if value else ['healthlake']
        elif name == 'custom:pract_id':
            attr_dict['practitioner_id'] = value if value else None
        elif name == 'custom:pract_name':
            attr_dict['practitioner_name'] = value if value else None
    return attr_dict


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user with Cognito."""
    try:
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
                'SECRET_HASH': _get_secret_hash(email)
            }
        )
        
        auth_result = response.get('AuthenticationResult', {})
        
        # Get user info from ID token
        id_token = auth_result.get('IdToken', '')
        # Decode without verification just to get claims (we trust Cognito)
        claims = jwt.get_unverified_claims(id_token)
        
        return {
            'access_token': auth_result.get('AccessToken', ''),
            'id_token': id_token,
            'refresh_token': auth_result.get('RefreshToken', ''),
            'expires_in': auth_result.get('ExpiresIn', 3600),
            'user': {
                'username': claims.get('email', ''),  # Display email as username
                'email': claims.get('email', ''),
                'first_name': claims.get('given_name', ''),
                'last_name': claims.get('family_name', ''),
                'role': claims.get('custom:role', 'user'),
                'allowed_data_sources': claims.get('custom:sources', 'healthlake').split('|'),
                'practitioner_id': claims.get('custom:pract_id'),
                'practitioner_name': claims.get('custom:pract_name'),
            }
        }
    except cognito_client.exceptions.NotAuthorizedException:
        return None
    except cognito_client.exceptions.UserNotFoundException:
        return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from Cognito access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Get user info from Cognito using access token
        response = cognito_client.get_user(AccessToken=token)
        
        attr_dict = _parse_user_attributes(response.get('UserAttributes', []))
        
        email = attr_dict.get('email', response.get('Username', ''))
        return User(
            username=email,  # Display email as username
            email=email,
            first_name=attr_dict.get('first_name'),
            last_name=attr_dict.get('last_name'),
            disabled=False,
            role=attr_dict.get('role', 'user'),
            allowed_data_sources=attr_dict.get('allowed_data_sources', ['healthlake']),
            practitioner_id=attr_dict.get('practitioner_id'),
            practitioner_name=attr_dict.get('practitioner_name'),
        )
    except cognito_client.exceptions.NotAuthorizedException:
        raise credentials_exception
    except Exception as e:
        print(f"Token validation error: {e}")
        raise credentials_exception


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============== User Management Functions ==============

def get_all_users() -> List[UserResponse]:
    """Get all users from Cognito."""
    users = []
    try:
        paginator = cognito_client.get_paginator('list_users')
        for page in paginator.paginate(UserPoolId=COGNITO_USER_POOL_ID):
            for user in page['Users']:
                attr_dict = _parse_user_attributes(user.get('Attributes', []))
                email = attr_dict.get('email', user.get('Username', ''))
                users.append(UserResponse(
                    username=email,  # Display email as username
                    email=email,
                    first_name=attr_dict.get('first_name'),
                    last_name=attr_dict.get('last_name'),
                    disabled=not user.get('Enabled', True),
                    role=attr_dict.get('role', 'user'),
                    allowed_data_sources=attr_dict.get('allowed_data_sources', ['healthlake']),
                    practitioner_id=attr_dict.get('practitioner_id'),
                    practitioner_name=attr_dict.get('practitioner_name'),
                ))
    except Exception as e:
        print(f"Error listing users: {e}")
    return users


def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user in Cognito."""
    try:
        # Build user attributes
        user_attributes = [
            {'Name': 'email', 'Value': user_data.email},
            {'Name': 'email_verified', 'Value': 'true'},
            {'Name': 'custom:role', 'Value': user_data.role},
            {'Name': 'custom:sources', 'Value': '|'.join(user_data.allowed_data_sources)},
        ]
        
        if user_data.first_name:
            user_attributes.append({'Name': 'given_name', 'Value': user_data.first_name})
        if user_data.last_name:
            user_attributes.append({'Name': 'family_name', 'Value': user_data.last_name})
        if user_data.practitioner_id:
            user_attributes.append({'Name': 'custom:pract_id', 'Value': user_data.practitioner_id})
        if user_data.practitioner_name:
            user_attributes.append({'Name': 'custom:pract_name', 'Value': user_data.practitioner_name})
        
        # Create user
        response = cognito_client.admin_create_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=user_data.email,
            TemporaryPassword=user_data.password,
            UserAttributes=user_attributes,
            MessageAction='SUPPRESS'  # Don't send welcome email
        )
        
        # Set permanent password
        cognito_client.admin_set_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=user_data.email,
            Password=user_data.password,
            Permanent=True
        )
        
        # Add to group based on role
        group_name = 'admins' if user_data.role == 'admin' else 'users'
        try:
            cognito_client.admin_add_user_to_group(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=user_data.email,
                GroupName=group_name
            )
        except:
            pass  # Group might not exist
        
        # Get the created user's sub
        user_info = response.get('User', {})
        attr_dict = _parse_user_attributes(user_info.get('Attributes', []))
        
        return UserResponse(
            username=user_data.email,  # Display email as username
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            disabled=False,
            role=user_data.role,
            allowed_data_sources=user_data.allowed_data_sources,
            practitioner_id=user_data.practitioner_id,
            practitioner_name=user_data.practitioner_name,
        )
    except cognito_client.exceptions.UsernameExistsException:
        raise ValueError(f"User with email '{user_data.email}' already exists")
    except Exception as e:
        raise ValueError(f"Failed to create user: {str(e)}")


def update_user(username: str, user_data: UserUpdate) -> UserResponse:
    """Update a user in Cognito."""
    try:
        # First, get the user to find their email (username in Cognito)
        users = get_all_users()
        target_user = None
        cognito_username = None
        
        for user in users:
            if user.username == username:
                target_user = user
                cognito_username = user.email  # In Cognito, email is the username
                break
        
        if not target_user:
            raise ValueError(f"User not found")
        
        # Build attributes to update
        user_attributes = []
        
        if user_data.first_name is not None:
            user_attributes.append({'Name': 'given_name', 'Value': user_data.first_name})
        if user_data.last_name is not None:
            user_attributes.append({'Name': 'family_name', 'Value': user_data.last_name})
        if user_data.role is not None:
            user_attributes.append({'Name': 'custom:role', 'Value': user_data.role})
        if user_data.allowed_data_sources is not None:
            user_attributes.append({'Name': 'custom:sources', 'Value': '|'.join(user_data.allowed_data_sources)})
        if user_data.practitioner_id is not None:
            user_attributes.append({'Name': 'custom:pract_id', 'Value': user_data.practitioner_id or ''})
        if user_data.practitioner_name is not None:
            user_attributes.append({'Name': 'custom:pract_name', 'Value': user_data.practitioner_name or ''})
        
        if user_attributes:
            cognito_client.admin_update_user_attributes(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=cognito_username,
                UserAttributes=user_attributes
            )
        
        # Update password if provided
        if user_data.password:
            cognito_client.admin_set_user_password(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=cognito_username,
                Password=user_data.password,
                Permanent=True
            )
        
        # Enable/disable user
        if user_data.disabled is not None:
            if user_data.disabled:
                cognito_client.admin_disable_user(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Username=cognito_username
                )
            else:
                cognito_client.admin_enable_user(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Username=cognito_username
                )
        
        # Return updated user info
        return UserResponse(
            username=target_user.email,  # Display email as username
            email=target_user.email,
            first_name=user_data.first_name if user_data.first_name is not None else target_user.first_name,
            last_name=user_data.last_name if user_data.last_name is not None else target_user.last_name,
            disabled=user_data.disabled if user_data.disabled is not None else target_user.disabled,
            role=user_data.role if user_data.role is not None else target_user.role,
            allowed_data_sources=user_data.allowed_data_sources if user_data.allowed_data_sources is not None else target_user.allowed_data_sources,
            practitioner_id=user_data.practitioner_id if user_data.practitioner_id is not None else target_user.practitioner_id,
            practitioner_name=user_data.practitioner_name if user_data.practitioner_name is not None else target_user.practitioner_name,
        )
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to update user: {str(e)}")


def delete_user(username: str) -> bool:
    """Delete a user from Cognito."""
    try:
        # Find the user's email (Cognito username)
        users = get_all_users()
        cognito_username = None
        
        for user in users:
            if user.username == username:
                cognito_username = user.email
                # Prevent deleting the admin
                if user.role == 'admin' and user.email == 'admin@chartagent.local':
                    raise ValueError("Cannot delete the primary admin user")
                break
        
        if not cognito_username:
            raise ValueError(f"User not found")
        
        cognito_client.admin_delete_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=cognito_username
        )
        return True
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to delete user: {str(e)}")

