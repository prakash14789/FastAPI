# ============================================================
# 4_field_constraints.py  -  Field() constraints + Annotated metadata
# ============================================================
# Instead of writing @field_validator for simple rules,
# use Field() directly on the field declaration — much less code.
#
# PART A: Field() constraints
#   max_length=N  -> string/list can have at most N characters/items
#   min_length=N  -> string/list must have at least N characters/items
#   gt=N          -> number must be > N  (strictly greater than)
#   lt=N          -> number must be < N  (strictly less than)
#   ge=N          -> number must be >= N (greater than or equal)
#   le=N          -> number must be <= N (less than or equal)
#   default=...   -> default value if field is not provided
#
# PART B: Field() metadata  (via Annotated)
#   title='...'       -> human-friendly label shown in Swagger UI
#   description='...' -> explains the field to API consumers
#   examples=[...]    -> sample values shown in Swagger UI
#
# Annotated[TYPE, Field(...)] — the modern Pydantic v2 way:
#   Keeps type AND all rules in one place.
#   Preferred when Field() has many arguments.
#
# WHERE TO USE Field() vs @field_validator?
#   Field()          -> simple numeric/string limits (gt, lt, max_length)
#   @field_validator -> complex logic, regex, calling external services, etc.
# ============================================================

from pydantic import BaseModel, ValidationError, Field, EmailStr
from typing import List, Dict, Optional, Annotated


# --------------------------------------------------------
# Part A: Field() constraints
# --------------------------------------------------------
class Patient(BaseModel):
    name: str               = Field(max_length=50)              # name <= 50 chars
    email: EmailStr
    age: int                = Field(gt=0, lt=120)               # 0 < age < 120
    weight: float           = Field(gt=0)                       # weight > 0
    married: bool           = False                             # simple default
    allergies: Optional[List[str]] = Field(default=None, max_length=5)  # list max 5 items
    contact_details: Dict[str, str]


print("=== Part A: Field() Constraints ===")
try:
    p = Patient(name='Nitish', email='n@example.com', age=35,
                weight=72.5, contact_details={'phone': '9999'})
    print("Valid  ->", p.name, p.age, p.allergies)
except ValidationError as e:
    print(e)

try:
    Patient(name='A' * 51, email='n@example.com', age=35,   # name too long
            weight=72.5, contact_details={'phone': '9999'})
except ValidationError as e:
    print("Name > 50   ->", e.errors()[0]['msg'])

try:
    Patient(name='Nitish', email='n@example.com', age=0,    # age not > 0
            weight=72.5, contact_details={'phone': '9999'})
except ValidationError as e:
    print("age=0 (gt=0) ->", e.errors()[0]['msg'])
print()


# --------------------------------------------------------
# Part B: Annotated + Field metadata
# --------------------------------------------------------
# Constraints + metadata in ONE Field() call.
# FastAPI reads this schema to build Swagger UI automatically.
class PatientWithMeta(BaseModel):
    name: Annotated[
        str,
        Field(
            max_length=50,
            title='Name of the patient',            # shown as label in Swagger
            description='Full name, max 50 chars',  # shown as hint in Swagger
            examples=['Nitish', 'Amit']             # shown as example in Swagger
        )
    ]
    email: Annotated[
        EmailStr,
        Field(title='Email', description='Valid email address',
              examples=['patient@hospital.com'])
    ]
    age: Annotated[
        int,
        Field(gt=0, lt=120,
              title='Age', description='Patient age 1-119',
              examples=[25, 35, 60])
    ]


print("=== Part B: Annotated + Metadata ===")
try:
    p = PatientWithMeta(name='Nitish', email='n@example.com', age=35)
    print("Valid ->", p)
except ValidationError as e:
    print(e)

# model_json_schema() shows what FastAPI sends to Swagger UI
schema = PatientWithMeta.model_json_schema()
name_field = schema['properties']['name']
print("Schema 'name' field:")
print("  title      :", name_field.get('title'))
print("  description:", name_field.get('description'))
print("  examples   :", name_field.get('examples'))
print("  maxLength  :", name_field.get('maxLength'))
# All four appear — constraints AND metadata live together in one Field()
