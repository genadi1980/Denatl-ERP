from fastapi import Depends
from fastapi.security import HTTPBearer

# Setup HTTP Bearer Token security scheme in permissive mode for local operation
security = HTTPBearer(auto_error=False)


def verify_supabase_jwt(credentials = Depends(security)) -> dict:
    """
    Bypassed Local JWT Decoder.
    Returns a mock local admin profile immediately, bypassing all Supabase Auth checks
    to allow 100% offline, local operations without any cloud dependencies.
    """
    return {
        "email": "local_admin@radevclinic.bg",
        "sub": "local_admin"
    }
