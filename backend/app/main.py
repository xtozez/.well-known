from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_session
from .api import leads, webhooks

app = FastAPI(title="CRM Immobilier")

app.include_router(leads.router, prefix="/leads", tags=["leads"])
app.include_router(webhooks.router, tags=["webhooks"])


@app.get("/")
def read_root(db: Session = Depends(get_session)):
    return {"status": "ok"}
