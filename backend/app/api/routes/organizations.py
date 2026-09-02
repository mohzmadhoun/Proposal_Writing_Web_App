from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationRead])
def list_organizations(db: Session = Depends(get_db)) -> list[Organization]:
    return list(db.scalars(select(Organization).order_by(Organization.created_at.desc())))


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)) -> Organization:
    organization = Organization(name=payload.name, slug=payload.slug)
    db.add(organization)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists",
        ) from exc
    db.refresh(organization)
    return organization
