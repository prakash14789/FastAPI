# ============================================================
# 1_pydantic_why.py  -  Why Pydantic? What problem does it solve?
# ============================================================
# WITHOUT Pydantic:
#   You get raw data (dict, JSON, form input).
#   You have to manually check types, validate, convert.
#   Easy to miss edge cases -> bugs in production.
#
# WITH Pydantic:
#   You define a model (class with type hints).
#   Pydantic automatically validates + converts all data.
#   If data is wrong -> ValidationError with a clear message.
#   No manual if/else checks needed.
# ============================================================

from pydantic import BaseModel, ValidationError
from typing import List, Dict, Optional


# --- Basic model: just declare fields with types ---
# Pydantic reads these type hints and validates every value automatically.
class Patient(BaseModel):
    name: str
    age: int
    weight: float                           # decimal number
    married: bool                           # True / False
    allergies: List[str]                    # list — every item must be a string
    contact_details: Dict[str, str]         # dict — both key and value are strings


# Valid data — everything matches the declared types
p1 = Patient(
    name='Nitish', age=35, weight=75.2, married=True,
    allergies=['pollen', 'dust'],
    contact_details={'email': 'n@example.com', 'phone': '9999999999'}
)
print("=== Valid Patient ===")
print(p1)
print()


# --- Optional fields & defaults ---
# Optional[str] = None  -> can be str OR None, field is not required
# List[str] = []        -> not required, defaults to empty list
# bool = False          -> not required, defaults to False
# Fields WITHOUT a default are REQUIRED — omitting them raises ValidationError.
class PatientV2(BaseModel):
    name: str                       # REQUIRED
    age: int                        # REQUIRED
    weight: float                   # REQUIRED
    married: bool = False           # optional, default False
    allergies: List[str] = []       # optional, default empty list
    email: Optional[str] = None     # optional, default None

# Only pass required fields — Pydantic fills in the rest with defaults
p2 = PatientV2(name='Ankit', age=28, weight=68.0)
print("=== Optional & Defaults ===")
print(p2)   # married=False, allergies=[], email=None are auto-filled
print()


# --- What happens when data is WRONG? ---
print("=== ValidationError demo ===")
try:
    bad = Patient(
        name='Nitish',
        age='not_a_number',         # age must be int, this is a string
        weight=75.2, married=True,
        allergies=['pollen'],
        contact_details={'phone': '9999'}
    )
except ValidationError as e:
    print("Caught ValidationError:")
    for err in e.errors():
        print(f"  field: {err['loc'][0]}  ->  {err['msg']}")
