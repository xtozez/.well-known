from typing import Optional
from sqlalchemy.orm import Session
from .. import models
import os
import re

try:
    import phonenumbers
except ImportError:  # pragma: no cover
    phonenumbers = None


# Simple Jaro-Winkler implementation
# Source adapted from public domain

def jaro_distance(s1: str, s2: str) -> float:
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    max_dist = int(max(len1, len2) / 2) - 1
    match = 0
    hash_s1 = [0] * len1
    hash_s2 = [0] * len2
    for i in range(len1):
        for j in range(max(0, i - max_dist), min(len2, i + max_dist + 1)):
            if s1[i] == s2[j] and hash_s2[j] == 0:
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break
    if match == 0:
        return 0.0
    t = 0
    point = 0
    for i in range(len1):
        if hash_s1[i]:
            while hash_s2[point] == 0:
                point += 1
            if s1[i] != s2[point]:
                t += 1
            point += 1
    t /= 2
    return (match / len1 + match / len2 + (match - t) / match) / 3.0


def jaro_winkler(s1: str, s2: str) -> float:
    jaro = jaro_distance(s1, s2)
    prefix = 0
    for c1, c2 in zip(s1, s2):
        if c1 == c2:
            prefix += 1
        else:
            break
        if prefix == 4:
            break
    return jaro + 0.1 * prefix * (1 - jaro)


def normalize_email(email: Optional[str]) -> Optional[str]:
    return email.strip().lower() if email else None


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if phonenumbers:
        try:
            parsed = phonenumbers.parse(digits, "FR")
            if not phonenumbers.is_valid_number(parsed):
                return digits
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            return digits
    return digits


def find_duplicate(db: Session, *, email: Optional[str], phone: Optional[str], first_name: str, last_name: str, city: Optional[str], zipcode: Optional[str], threshold: float) -> Optional[models.Lead]:
    email_norm = normalize_email(email)
    phone_norm = normalize_phone(phone)

    # strong match
    if email_norm:
        lead = db.query(models.Lead).filter(models.Lead.email == email_norm).first()
        if lead:
            return lead
    if phone_norm:
        lead = db.query(models.Lead).filter(models.Lead.phone_e164 == phone_norm).first()
        if lead:
            return lead

    # fuzzy match
    candidates = db.query(models.Lead).all()
    for cand in candidates:
        score_name = jaro_winkler((cand.first_name or "") + (cand.last_name or ""), (first_name or "") + (last_name or ""))
        score_city = jaro_winkler(cand.city or cand.zipcode or "", city or zipcode or "")
        score = (score_name + score_city) / 2
        if score >= threshold:
            return cand
    return None


def merge_leads(db: Session, existing: models.Lead, new: models.Lead) -> models.Lead:
    existing.consent = existing.consent or new.consent
    if new.source and new.source not in (existing.source or ""):
        existing.source = ",".join(filter(None, [existing.source, new.source]))
    existing.interactions.extend(new.interactions)
    db.delete(new)
    db.commit()
    db.refresh(existing)
    return existing
