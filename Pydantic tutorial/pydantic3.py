# ============================================================
# pydantic3.py  -  Pydantic In Depth  (clean learning file)
# ============================================================
# Building on pydantic2.py, we now go deeper step by step:
#   1. Richer field types   - float, bool, List[str], Dict[str,str]
#   2. Optional + defaults  - fields that aren't always required
#   3. field_validator      - custom rules (mode='after' default)
#   4. field_validator      - mode='before' (run before type conversion)
#   5. Model methods        - model_dump, model_dump_json, model_copy
#   6. Nested models        - a model inside a model
#   7. Special types        - EmailStr, AnyUrl
#   8. Field() constraints  - max_length, gt, lt inline
#   9. Annotated + metadata - title, description, examples for API docs
# ============================================================

from pydantic import BaseModel, ValidationError, field_validator, EmailStr, AnyUrl, Field
from typing import List, Dict, Optional, Annotated


# ============================================================
# STEP 1: Richer Field Types
# ============================================================
# Beyond str and int, Pydantic handles:
#   float  -> decimal numbers
#   bool   -> True / False
#   List[str]       -> list where every item must be a string
#                      (List alone won't tell Pydantic what's inside)
#   Dict[str, str]  -> key-value pairs, both key and value are strings

class Patient(BaseModel):
    name: str
    age: int
    weight: float
    married: bool
    allergies: List[str]            # List[str] not just List — Pydantic needs to know the item type
    contact_details: Dict[str, str]

p1 = Patient(
    name='Nitish', age=35, weight=75.2, married=True,
    allergies=['pollen', 'dust'],
    contact_details={'email': 'n@example.com', 'phone': '9999999999'}
)
print("=== STEP 1: Richer Types ===")
print(p1)
print()


# ============================================================
# STEP 2: Optional Fields & Defaults
# ============================================================
# Optional[str] = None  -> field can be str OR None, not required
# List[str] = []        -> defaults to empty list if not provided
# bool = False          -> defaults to False if not provided
# Fields WITHOUT a default are REQUIRED — missing them raises ValidationError.

class PatientV2(BaseModel):
    name: str                       # REQUIRED
    age: int                        # REQUIRED
    weight: float                   # REQUIRED
    married: bool = False           # optional, default False
    allergies: List[str] = []       # optional, default empty list
    email: Optional[str] = None     # optional, default None

# Only pass required fields — Pydantic fills in defaults for the rest
p2 = PatientV2(name='Ankit', age=28, weight=68.0)
print("=== STEP 2: Optional & Defaults ===")
print(p2)  # married=False, allergies=[], email=None are auto-filled
print()


# ============================================================
# STEP 3: field_validator  (mode='after' — the DEFAULT)
# ============================================================
# When you need rules beyond just "is it the right type?",
# use @field_validator.
#
# mode='after' (default):
#   Pydantic converts the type FIRST, then your function runs.
#   So 'value' inside your function is already the correct type (int, str…).
#
# Return the value to accept it, raise ValueError to reject it.

class PatientV3(BaseModel):
    name: str
    age: int

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty.')
        return v.strip().title()    # clean + capitalise: 'nitish' -> 'Nitish'

    @field_validator('age')        # no mode= means mode='after' (default)
    @classmethod
    def age_valid(cls, v):
        # v is already an int here because Pydantic converted it first
        if v <= 0 or v >= 120:
            raise ValueError('Age must be between 1 and 119.')
        return v

print("=== STEP 3: field_validator (mode='after', default) ===")
try:
    p3 = PatientV3(name='  nitish  ', age=35)
    print("Valid ->", p3)           # name auto-cleaned to 'Nitish'
except ValidationError as e:
    print(e)

try:
    PatientV3(name='', age=35)     # empty name -> ValidationError
except ValidationError as e:
    print("Empty name ->", e.errors()[0]['msg'])

try:
    PatientV3(name='Nitish', age=-5)
except ValidationError as e:
    print("age=-5  ->", e.errors()[0]['msg'])
print()


# ============================================================
# STEP 4: field_validator  mode='before'
# ============================================================
# mode='before':
#   Your function runs FIRST on the RAW input, BEFORE Pydantic
#   converts the type.  'value' could be str, float, int — anything.
#   Use this to clean / transform messy input before validation.
#
# mode='after' (commented for comparison):
#   @field_validator('age')          <- default, no mode needed
#   def validate_age(cls, v):
#       # v is already int here
#       if 0 < v < 100: return v
#       raise ValueError('...')

class PatientV4(BaseModel):
    name: str
    age: int

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, value):
        # value is RAW here — could be '35' (string) passed by mistake
        if 0 < value < 100:
            return value            # return raw value, Pydantic will cast to int
        else:
            raise ValueError('Age should be in between 0 and 100')

print("=== STEP 4: field_validator mode='before' ===")
try:
    p4 = PatientV4(name='Nitish', age=35)
    print("Valid  ->", p4)
except ValidationError as e:
    print(e)

try:
    PatientV4(name='Nitish', age=150)
except ValidationError as e:
    print("age=150 ->", e.errors()[0]['msg'])
print()


# ============================================================
# STEP 5: Model Methods
# ============================================================
# Once you have a validated Pydantic object, useful built-ins:
#   .model_dump()         -> Python dict
#   .model_dump_json()    -> JSON string
#   .model_json_schema()  -> JSON schema (FastAPI uses this for Swagger docs)
#   .model_copy(update={})-> copy with some fields overridden

p5 = PatientV2(name='Priya', age=25, weight=55.5, married=True,
               allergies=['nuts'], email='priya@example.com')

print("=== STEP 5: Model Methods ===")
print("model_dump()      ->", p5.model_dump())
print("model_dump_json() ->", p5.model_dump_json())
print("model_copy(age=26)->", p5.model_copy(update={'age': 26}))
print()


# ============================================================
# STEP 6: Nested Models
# ============================================================
# A Pydantic model can have another model as a field.
# Pydantic validates BOTH levels — outer and inner.
# Useful for structured data like Address, ContactInfo, etc.

class Address(BaseModel):
    city: str
    state: str
    pin_code: str       # str, not int — pins can have leading zeros

class PatientV5(BaseModel):
    name: str
    age: int
    address: Address    # nested model

p6 = PatientV5(
    name='Rahul', age=40,
    address={'city': 'Mumbai', 'state': 'Maharashtra', 'pin_code': '400001'}
    # Pydantic auto-converts the dict into an Address object
)
print("=== STEP 6: Nested Models ===")
print(p6)
print("City:", p6.address.city)
print("model_dump() ->", p6.model_dump())   # address dict nested inside
print()


# ============================================================
# STEP 7: Special Pydantic Types  (EmailStr, AnyUrl)
# ============================================================
# Instead of writing your own @field_validator for emails or URLs,
# Pydantic ships ready-made smart types:
#
#   EmailStr  -> checks @, domain, valid TLD automatically
#   AnyUrl    -> checks scheme (https://) + host automatically
#
# NOTE: EmailStr needs:  pip install pydantic[email]

class PatientV6(BaseModel):
    name: str
    email: EmailStr         # no custom validator needed — EmailStr does it all
    linkedin_url: AnyUrl    # no custom validator needed — AnyUrl does it all
    age: int

print("=== STEP 7: Special Types (EmailStr, AnyUrl) ===")
try:
    p7 = PatientV6(name='Nitish', email='nitish@example.com',
                   linkedin_url='https://linkedin.com/in/nitish', age=35)
    print("Valid  ->", p7.name, p7.email, p7.linkedin_url)
except ValidationError as e:
    print(e)

try:
    PatientV6(name='Nitish', email='notanemail',
              linkedin_url='https://linkedin.com', age=35)
except ValidationError as e:
    print("Bad email ->", e.errors()[0]['msg'])

try:
    PatientV6(name='Nitish', email='nitish@example.com',
              linkedin_url='linkedin.com', age=35)  # missing https://
except ValidationError as e:
    print("Bad URL   ->", e.errors()[0]['msg'])
print()


# ============================================================
# STEP 8: Field() Constraints
# ============================================================
# For simple rules (length, numeric range), use Field() inline.
# No @field_validator needed — much less code.
#
#   max_length=N  -> string/list can have at most N chars/items
#   gt=N          -> number must be > N  (strictly greater than)
#   lt=N          -> number must be < N  (strictly less than)
#   ge=N          -> number must be >= N
#   le=N          -> number must be <= N
#   default=...   -> default value if field not provided

class PatientV7(BaseModel):
    name: str               = Field(max_length=50)
    email: EmailStr
    age: int                = Field(gt=0, lt=120)   # replaces the age @field_validator above
    weight: float           = Field(gt=0)
    married: bool           = False
    allergies: Optional[List[str]] = Field(default=None, max_length=5)  # list max 5 items
    contact_details: Dict[str, str]

print("=== STEP 8: Field() Constraints ===")
try:
    p8 = PatientV7(name='Nitish', email='n@example.com', age=35,
                   weight=72.5, contact_details={'phone': '9999'})
    print("Valid  ->", p8.name, p8.age, p8.allergies)
except ValidationError as e:
    print(e)

try:
    PatientV7(name='A'*51, email='n@example.com', age=35,
              weight=72.5, contact_details={'phone': '9999'})
except ValidationError as e:
    print("Name too long  ->", e.errors()[0]['msg'])

try:
    PatientV7(name='Nitish', email='n@example.com', age=0,
              weight=72.5, contact_details={'phone': '9999'})
except ValidationError as e:
    print("age=0 (gt=0)   ->", e.errors()[0]['msg'])
print()


# ============================================================
# STEP 9: Annotated + Field Metadata
# ============================================================
# Field() can carry METADATA that doesn't affect validation
# but enriches your API docs (Swagger UI in FastAPI):
#
#   title='...'       -> human-friendly label in Swagger
#   description='...' -> explanation of what the field means
#   examples=[...]    -> sample values shown in Swagger
#
# Style A (simple):
#   name: str = Field(max_length=50, title='Name of the patient')
#
# Style B — Annotated (recommended in Pydantic v2, cleaner for many args):
#   name: Annotated[str, Field(max_length=50, title='Name of the patient')]
#
# Both work identically. Annotated[TYPE, FIELD] keeps type and rules together.

class PatientV8(BaseModel):
    name: Annotated[
        str,
        Field(
            max_length=50,
            title='Name of the patient',
            description='Full name in less than 50 characters',
            examples=['Nitish', 'Amit']
        )
    ]
    email: Annotated[
        EmailStr,
        Field(title='Email', description='Valid email address',
              examples=['patient@hospital.com'])
    ]
    age: Annotated[
        int,
        Field(gt=0, lt=120, title='Age',
              description='Patient age 1-119', examples=[25, 35])
    ]

print("=== STEP 9: Annotated + Field Metadata ===")
try:
    p9 = PatientV8(name='Nitish', email='n@example.com', age=35)
    print("Valid ->", p9)
except ValidationError as e:
    print(e)

# Schema carries both constraints AND metadata — FastAPI reads this for Swagger
schema = PatientV8.model_json_schema()
name_field = schema['properties']['name']
print("Schema for 'name' field:")
print("  title      :", name_field.get('title'))
print("  description:", name_field.get('description'))
print("  examples   :", name_field.get('examples'))
print("  maxLength  :", name_field.get('maxLength'))
print()


# ============================================================
# SUMMARY
# ============================================================
# [1] Richer types     : float, bool, List[str], Dict[str,str]
# [2] Optional+default : Optional[str]=None, List[str]=[]
# [3] field_validator  : mode='after' (default) — value already typed
# [4] field_validator  : mode='before' — value is raw, runs first
# [5] Model methods    : model_dump, model_dump_json, model_copy
# [6] Nested models    : Address inside Patient — both validated
# [7] Special types    : EmailStr, AnyUrl — zero boilerplate
# [8] Field()          : max_length, gt, lt — inline constraints
# [9] Annotated        : title, description, examples — API docs
# ============================================================
