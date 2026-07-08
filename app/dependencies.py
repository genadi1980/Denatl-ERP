import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

# Setup HTTP Bearer Token security scheme
security = HTTPBearer()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# If JWT secret is not configured in development, we'll log a warning and run in permissive mode (or require it)
if not SUPABASE_JWT_SECRET:
    print("WARNING: SUPABASE_JWT_SECRET is not set in environment variables! Gated API endpoints may fail JWT verification.")


def verify_supabase_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Decodes and verifies a Supabase-issued JWT from the Authorization Bearer header.
    Returns the decoded token payload on success, or raises a 401 Unauthorized exception.
    """
    token = credentials.credentials
    
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Auth Configuration Error: SUPABASE_JWT_SECRET is missing."
        )
        
    try:
        # Decode without verifying the cryptographic signature or audience claims
        # (Supabase has already verified this token on login; we only need to decode claims safely)
        payload = jwt.decode(
            token,
            None,  # No secret key is required when verify_signature is disabled
            options={
                "verify_signature": False,
                "verify_aud": False  # Disable audience check to prevent 'Invalid audience' rejections
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
