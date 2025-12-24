# CRM Immobilier Neuf

Prototype monorepo pour CRM immobilier (VEFA) pour SPLM-SEMEXVAL.

## Backend
- FastAPI + SQLAlchemy
- Alembic migrations
- Dédoublonnage simple
- API Webhooks sécurisés par signature HMAC

## Frontend
- Next.js (App Router) avec base Tailwind

## Tests
- `pytest` pour le module de dédoublonnage
