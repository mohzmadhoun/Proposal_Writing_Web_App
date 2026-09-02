from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    organization_name: str | None = None
    organization_slug: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthUserMembership(BaseModel):
    organization_id: str
    organization_name: str
    organization_slug: str
    role: str


class AuthUser(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    memberships: list[AuthUserMembership]


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser
