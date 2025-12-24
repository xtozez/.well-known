from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_session
from .. import models
from ..schemas import lead as lead_schema

router = APIRouter()


@router.post("/", response_model=lead_schema.LeadRead)
def create_lead(data: lead_schema.LeadCreate, db: Session = Depends(get_session)):
    lead = models.Lead(**data.dict())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/", response_model=List[lead_schema.LeadRead])
def list_leads(db: Session = Depends(get_session)):
    return db.query(models.Lead).all()


@router.get("/{lead_id}", response_model=lead_schema.LeadRead)
def get_lead(lead_id: int, db: Session = Depends(get_session)):
    lead = db.query(models.Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
