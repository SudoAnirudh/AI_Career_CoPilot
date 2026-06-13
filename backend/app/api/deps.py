from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.config import settings

def get_current_user(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)) -> User:
    """
    Get the authenticated user. If DEV_AUTH_BYPASS is active, 
    bypasses Clerk validation and returns the default developer user.
    """
    if settings.DEV_AUTH_BYPASS:
        # Retrieve or create default dev user based on PRD details
        user = db.query(User).filter(User.clerk_id == "dev_user_clerk").first()
        if not user:
            user = User(
                clerk_id="dev_user_clerk",
                name="Anirudh Sudheer",
                email="anirudhsudheer@gmail.com"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
        
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
        
    # Standard Clerk authorization validation
    token = authorization.replace("Bearer ", "")
    # Normally, we would verify the Clerk JWT signature here.
    # For this implementation, we will query or create the user from the Clerk ID context
    # passed in headers or custom claims (mocked here if invalid signature checking)
    clerk_id = "dev_user_clerk" # Placeholder
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user
