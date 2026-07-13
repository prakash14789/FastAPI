# ============================================================
# 3_model_validator.py  -  Cross-field validation rules
# ============================================================
# @field_validator (file 2) validates ONE field at a time.
# @model_validator validates the ENTIRE model — all fields together.
#
# Use model_validator when:
#   - A rule involves 2+ fields simultaneously
#   - Conditional requirement: "if field A has X, then field B must exist"
#   - The rule makes no sense on a single field alone
#
# mode='after'  (most common):
#   Runs AFTER all individual fields are validated and set.
#   Use 'self' to access any field on the model directly.
#   Return 'self' to accept, raise ValueError to reject.
#
# mode='before' (rare):
#   Receives the raw input dict before any field validation.
#   Use when you need to pre-process or reshape raw data.
# ============================================================

from pydantic import BaseModel, ValidationError, model_validator
from typing import Dict


class Patient(BaseModel):
    name: str
    age: int
    contact_details: Dict[str, str]

    # mode='after' -> instance method, use 'self' (no @classmethod needed)
    # All fields are already validated when this runs.
    @model_validator(mode='after')
    def validate_emergency_contact(self):
        # Rule: if patient is older than 60,
        # contact_details MUST contain an 'emergency' key.
        # This rule touches BOTH 'age' AND 'contact_details'
        # -> impossible to write with @field_validator alone.
        if self.age > 60 and 'emergency' not in self.contact_details:
            raise ValueError('Patients older than 60 must have an emergency contact')
        return self     # always return self when valid


print("=== model_validator: cross-field rule ===")

# Valid: age=35, no emergency contact required
try:
    p = Patient(name='Nitish', age=35, contact_details={'phone': '9999'})
    print("age=35, no emergency ->  OK:", p.name, p.age)
except ValidationError as e:
    print(e)

# Valid: age=65 WITH emergency contact — passes the rule
try:
    p = Patient(name='Nitish', age=65,
                contact_details={'phone': '9999', 'emergency': '8888'})
    print("age=65, with emergency-> OK:", p.name, p.age)
except ValidationError as e:
    print(e)

# Invalid: age=65 but NO emergency contact — fails the cross-field rule
try:
    p = Patient(name='Nitish', age=65, contact_details={'phone': '9999'})
except ValidationError as e:
    print("age=65, no emergency  -> ERROR:", e.errors()[0]['msg'])
