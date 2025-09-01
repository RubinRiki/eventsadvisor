from pydantic import BaseModel, EmailStr, field_validator

class User(BaseModel):
    """Represents a full internal user object including sensitive fields."""
    id: str
    email: EmailStr
    username: str
    hashed_password: str
    role: str = "user"
    is_active: bool = True

class UserPublic(BaseModel):
    """Represents the user object exposed to the client (no password)."""
    id: str
    email: EmailStr
    username: str
    role: str
    is_active: bool

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Ensure username is not empty and strip extra whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("username is required")
        return v
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
