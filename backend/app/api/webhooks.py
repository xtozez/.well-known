import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_session
from .. import models
from ..schemas.lead import LeadCreate
from ..services import dedup
import os

router = APIRouter()


def verify_signature(provider: str, body: bytes, signature: str) -> bool:
    secret = os.getenv(f"{provider.upper()}_WEBHOOK_SECRET", "")
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)


@router.post("/webhooks/{provider}")
async def ingest_webhook(provider: str, request: Request, db: Session = Depends(get_session)):
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if not verify_signature(provider, body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    payload = await request.json()
    data = LeadCreate(
        source=provider,
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        email=payload.get("email"),
        phone_e164=payload.get("phone"),
        budget_min=payload.get("budget_min"),
        budget_max=payload.get("budget_max"),
        typology=payload.get("typology"),
        city=payload.get("city"),
        zipcode=payload.get("zipcode"),
    )
    threshold = float(os.getenv("DEDUP_THRESHOLD", "0.85"))
    existing = dedup.find_duplicate(
        db,
        email=data.email,
        phone=data.phone_e164,
        first_name=data.first_name or "",
        last_name=data.last_name or "",
        city=data.city,
        zipcode=data.zipcode,
        threshold=threshold,
    )
    if existing:
        return {"status": "duplicate", "lead_id": existing.id}
    lead = models.Lead(**data.dict())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    interaction = models.Interaction(lead_id=lead.id, type="import", content=f"Lead importé via {provider}")
    db.add(interaction)
    db.commit()
    return {"status": "ok", "lead_id": lead.id}
