"""
routers/certificates.py
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.certificate import CertificateCreate, CertificateRead
from app.services.student_data_service import add_certificate, delete_certificate, list_certificates

router = APIRouter()


@router.get("", response_model=list[CertificateRead])
def get_certificates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_certificates(db, current_user.id)


@router.post("", response_model=CertificateRead, status_code=status.HTTP_201_CREATED)
def create_certificate(
    payload: CertificateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return add_certificate(db, current_user.id, payload)


@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_certificate(
    certificate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_certificate(db, current_user.id, certificate_id)
