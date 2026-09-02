from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    AuthUser,
    AuthUserMembership,
    LoginRequest,
    RegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_auth_user(db: Session, user: User) -> AuthUser:
    memberships = list(
        db.execute(
            select(Membership, Organization)
            .join(Organization, Organization.id == Membership.organization_id)
            .where(Membership.user_id == user.id)
        )
    )
    return AuthUser(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        memberships=[
            AuthUserMembership(
                organization_id=str(membership.organization_id),
                organization_name=organization.name,
                organization_slug=organization.slug,
                role=membership.role,
            )
            for membership, organization in memberships
        ],
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.flush()

    if payload.organization_name and payload.organization_slug:
        organization = Organization(
            name=payload.organization_name,
            slug=payload.organization_slug,
            created_by=user.id,
        )
        db.add(organization)
        db.flush()
        db.add(
            Membership(
                organization_id=organization.id,
                user_id=user.id,
                role="owner",
                created_by=user.id,
            )
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration conflict: verify organization slug uniqueness",
        ) from exc

    db.refresh(user)
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_build_auth_user(db, user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_build_auth_user(db, user))


@router.get("/me", response_model=AuthUser)
def me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AuthUser:
    return _build_auth_user(db, current_user)
