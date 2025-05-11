# src/auth.py

import logging
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated


# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# In a real application, load these from environment variables or a secure config management
SECRET_KEY = os.environ.get("SECRET_KEY", "YOUR_DEFAULT_SUPER_SECRET_KEY") # CHANGE THIS!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Security Scheme ---
# This tells FastAPI to expect a Bearer token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") # Points to our login endpoint

# --- Token Operations ---
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates a JWT access token."""
    logger.debug(f"Creating access token for data: {data}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # Add expiration claim
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created for user: {data.get('sub')}")
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTPException if the token is invalid or expired.
    """
    logger.debug("get_current_user called.")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and verify the token signature and expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the user identifier and roles from the payload (claims)
        # 'sub' (subject) is a standard JWT claim for the principal (user identifier)
        username: str = payload.get("sub")
        user_roles: list[str] = payload.get("roles", [])

        if username is None:
            logger.warning("JWT token missing 'sub' claim.")
            raise credentials_exception

        # In a real application, you would fetch the user from your database here
        # using the username to ensure they still exist and are active.
        # For this example, we'll just return the payload data as the "user".
        user_data = {"username": username, "roles": user_roles}
        logger.info(f"Authenticated user: {username}")
        return user_data # Return user information
    except JWTError as e:
        logger.error(f"JWTError during authentication: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        # Catch other potential exceptions during user fetching if applicable
        raise credentials_exception


# --- User Verification (Example - Replace with Database Logic) ---
# This is a simplified example using a hardcoded user.
# In a real app, interact with your database to check username/password.

# Use passlib for secure password hashing
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a dummy hashed password for 'testuser'
# You would generate this when creating a user in a real system
# print(pwd_context.hash("securepassword123")) # Example of how to generate hash
FAKE_HASHED_PASSWORD = "$2b$12$EXAMPLEHASHEDPASSWORD..." # REPLACE with a real bcrypt hash!

fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": FAKE_HASHED_PASSWORD,
        "roles": ["user"], # Example roles
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hashed password."""
    logger.debug("Verifying password.")
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    """Retrieves user data from the dummy database (example)."""
    logger.debug(f"Fetching user from DB: {username}")
    return fake_users_db.get(username)

# --- Authorization Helper (Optional) ---
def require_role(role: str):
    """Dependency to check if the current user has a specific role."""
    def role_checker(current_user: dict = Depends(get_current_user)):
        logger.debug(f"Checking if user {current_user.get('username')} has role: {role}")
        if role not in current_user.get("roles", []):
            logger.warning(f"User {current_user.get('username')} lacks required role: {role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the '{role}' role"
            )
        return current_user
    return role_checker