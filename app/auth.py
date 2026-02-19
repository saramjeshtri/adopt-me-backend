import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

async def verify_admin(x_api_key: str = Header(...)):
    """
    Dependency that protects admin routes.
    The client must send the header: X-API-Key: your_secret_key
    """
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Akses i paautorizuar",
        )