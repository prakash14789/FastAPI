# ============================================================
# pydantic3.py  —  Pydantic In Depth
# ============================================================
# We already know WHY Pydantic exists (pydantic2.py).
# Now let's go DEEPER and understand:
#   1. Richer field types  (List, Dict, Optional, bool, float)
#   2. Default values      (fields that aren't always required)
#   3. Field validators    (custom rules beyond just "is it an int?")
#   4. Model methods       (model_dump, model_json_schema, etc.)
#   5. Nested models       (a model inside another model)
#   6. Special Pydantic types (EmailStr, AnyUrl — built-in smart validators)
#   7. Field()  — add constraints like max_length, gt, lt directly in model
# ============================================================

from pydantic import BaseModel, ValidationError, field_validator, EmailStr, AnyUrl, Field
from typing import List, Dict, Optional


# ============================================================
# STEP 1: Richer Field Types
# ============================================================
# So far we only had  name: str  and  age: int.
# Real-world data is richer. Let's build a proper Patient model.
#
#   name          → str            (plain string, we know this)
#   age           → int            (plain integer, we know this)
#   weight        → float          (decimal number, e.g. 72.5 kg)
#   married       → bool           (True / False)
#   allergies     → List[str]      (a list of allergy strings)
#   contact_details → Dict[str, str]  (key-value pairs like {"email": "a@b.com"})
#
# Pydantic validates ALL of these — not just str and int.
# ============================================================

class Patient(BaseModel):
    name: str
    age: int
    weight: float
    married: bool
    allergies: List[str]
    contact_details: Dict[str, str]


# Let's create a valid patient —
# every field matches exactly what the model expects.
patient_data = {
    'name': 'Nitish',
    'age': 35,
    'weight': 75.2,            # float  ✓
    'married': True,           # bool   ✓
    'allergies': ['pollen', 'dust'],                          # List[str]       ✓
    'contact_details': {'email': 'nitish@example.com', 'phone': '9999999999'}  # Dict[str,str] ✓
}

patient1 = Patient(**patient_data)
print("=== STEP 1: Richer Types ===")
print(patient1)
# Output: name='Nitish' age=35 weight=75.2 married=True allergies=[...] contact_details={...}
print()


# ============================================================
# STEP 2: Optional Fields & Default Values
# ============================================================
# Not every field is always available.
# For example, a patient might not have allergies — the list could be empty,
# OR maybe we don't collect it yet.
#
# Optional[str]  means the field can be  str  OR  None.
# We can also set a default value so the field isn't required at all.
#
#   allergies: List[str] = []        → defaults to empty list if not provided
#   email: Optional[str] = None      → defaults to None if not provided
#
# Without a default, the field is REQUIRED — Pydantic throws an error if missing.
# ============================================================

class PatientV2(BaseModel):
    name: str                           # REQUIRED — no default
    age: int                            # REQUIRED — no default
    weight: float                       # REQUIRED — no default
    married: bool = False               # OPTIONAL — defaults to False
    allergies: List[str] = []           # OPTIONAL — defaults to empty list        // yaha agar sirf list krte list ke andar string lena ha ya int wo define nahi kr pate isiliye List[str]
    email: Optional[str] = None         # OPTIONAL — defaults to None


# We can now create a patient with ONLY the required fields.
# Pydantic fills in the rest with defaults.
minimal_data = {
    'name': 'Ankit',
    'age': 28,
    'weight': 68.0
}

patient2 = PatientV2(**minimal_data)
print("=== STEP 2: Optional Fields & Defaults ===")
print(patient2)
# married=False, allergies=[], email=None  ← auto-filled by Pydantic
print()


# ============================================================
# STEP 3: Field Validators — Custom Rules
# ============================================================
# Pydantic checks TYPES automatically.
# But what if the type is correct yet the VALUE is still wrong?
#
# Example:  age = -5   → type is int ✓, but age can't be negative!
# Example:  name = ''  → type is str ✓, but empty name makes no sense!
#
# We use @field_validator to write our own custom logic.
# It runs AFTER Pydantic's own type check, so 'v' is already the right type.
# If our rule is broken, we raise a ValueError with a clear message.
# ============================================================

class PatientV3(BaseModel):
    name: str
    age: int
    email: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        # 'v' is the value passed for 'name'
        # .strip() removes whitespace — so '   ' also counts as empty
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace.')
        # We return the cleaned (stripped) name
        return v.strip().title()   # also capitalise nicely  e.g. 'nitish' → 'Nitish'

    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, v):
        # 'v' is the value passed for 'age'
        if v <= 0:
            raise ValueError(f'Age must be a positive integer, got {v}.')
        if v > 120:
            raise ValueError(f'Age {v} is unrealistically high.')
        return v


# --- Valid case ---
print("=== STEP 3: Field Validators ===")
try:
    p = PatientV3(name='  nitish  ', age=35)   # extra whitespace in name
    print(p)
    # name is automatically cleaned & title-cased → 'Nitish'
except ValidationError as e:
    print(e)

# --- Invalid case: empty name ---
try:
    p = PatientV3(name='   ', age=35)   # only whitespace — should fail
    print(p)
except ValidationError as e:
    print(f"\nCaught error: {e.errors()[0]['msg']}")

# --- Invalid case: negative age ---
try:
    p = PatientV3(name='Nitish', age=-5)   # age is negative — should fail
    print(p)
except ValidationError as e:
    print(f"Caught error: {e.errors()[0]['msg']}")

print()


# ============================================================
# STEP 4: Model Methods — What can you DO with a Pydantic model?
# ============================================================
# Once you have a validated Pydantic object, you get useful built-in methods:
#
#   .model_dump()          → convert the model to a plain Python dict
#   .model_dump_json()     → convert the model to a JSON string
#   .model_json_schema()   → see the full JSON schema (great for APIs/docs)
#   .model_copy()          → duplicate the model, optionally overriding some fields
#
# These are extremely useful in FastAPI where you need to
# serialize responses back to JSON.
# ============================================================

patient3 = PatientV2(name='Priya', age=25, weight=55.5, married=True,
                     allergies=['nuts'], email='priya@example.com')

print("=== STEP 4: Model Methods ===")

# 1. Convert to dict
patient_dict = patient3.model_dump()
print("model_dump()      ->", patient_dict)
# {'name': 'Priya', 'age': 25, 'weight': 55.5, 'married': True, ...}

# 2. Convert to JSON string
patient_json = patient3.model_dump_json()
print("model_dump_json() ->", patient_json)

# 3. See the JSON schema
schema = PatientV2.model_json_schema()
print("model_json_schema() ->", schema)

# 4. Copy and override one field
updated_patient = patient3.model_copy(update={'age': 26})
print("model_copy(update=...) ->", updated_patient)

print()


# ============================================================
# STEP 5: Nested Models — A Model inside a Model
# ============================================================
# In real projects, data is hierarchical.
# For example, an Address is its own structured object —
# not just a plain string inside Patient.
#
# We create a separate Address model and embed it inside Patient.
# Pydantic validates BOTH levels — the outer model AND the inner model.
#
# This keeps code clean and reusable:
#   Address can be used in Patient, Doctor, Hospital, etc.
# ============================================================

class Address(BaseModel):
    city: str
    state: str
    pin_code: str   # keeping as str because pin can have leading zeros


class PatientV4(BaseModel):
    name: str
    age: int
    address: Address   # nested model! Pydantic validates this too.


address_data = {'city': 'Mumbai', 'state': 'Maharashtra', 'pin_code': '400001'}
patient_data_v4 = {'name': 'Rahul', 'age': 40, 'address': address_data}

patient4 = PatientV4(**patient_data_v4)
print("=== STEP 5: Nested Models ===")
print(patient4)
# address is a fully validated Address object, not a raw dict

# Access nested fields like a normal object
print(f"City: {patient4.address.city}")
print(f"Pin:  {patient4.address.pin_code}")

# model_dump() also flattens the nested model into a plain dict
print("Nested model_dump() ->", patient4.model_dump())
print()


# ============================================================
# STEP 6: Special Pydantic Types — Built-in Smart Validators
# ============================================================
# So far we wrote OUR OWN validators using @field_validator.
# But Pydantic ships with READY-MADE smart types that already
# know how to validate common real-world data.
#
# The most useful ones:
#
#   EmailStr    -> validates that a string is a proper email address
#                  e.g.  'user@example.com'  is VALID
#                  e.g.  'notanemail'         raises ValidationError
#                  e.g.  'user@'              raises ValidationError (no domain)
#
#   HttpUrl     -> validates a proper URL (must start with http/https)
#                  e.g.  'https://google.com'  VALID
#                  e.g.  'google'              raises ValidationError
#
#   PositiveInt -> int that MUST be > 0, no @field_validator needed!
#
#   constr(...) -> constrained string: min/max length, regex pattern, etc.
#
# Why use these instead of writing your own @field_validator?
#   1. Less code — no boilerplate
#   2. Battle-tested logic by the Pydantic team
#   3. They show up correctly in the auto-generated JSON schema
#      (FastAPI uses this schema to build Swagger API docs)
#
# IMPORTANT: EmailStr needs an extra package to work.
#   Run this in your terminal first:
#       pip install pydantic[email]
#   Without it you will get an ImportError.
# ============================================================


class PatientV5(BaseModel):
    name: str
    email: EmailStr     # <-- EmailStr instead of plain str
                        # Pydantic will now automatically check:
                        #   - is there an '@' symbol?
                        #   - is there a domain name after '@'?
                        #   - does the domain have a valid TLD?
                        # You write ZERO extra code — EmailStr does it all.
    age: int


print("=== STEP 6: Special Pydantic Types (EmailStr) ===")

# --- Valid email ---
try:
    p = PatientV5(name='Nitish', email='nitish@example.com', age=35)
    print("Valid   ->", p)
    # email stored as-is after passing validation
except ValidationError as e:
    print(e)

# --- Invalid: no '@' at all ---
try:
    p = PatientV5(name='Nitish', email='notanemail', age=35)
    # 'notanemail' has no '@' or domain — clearly not an email
except ValidationError as e:
    print(f"Bad email 'notanemail'    -> {e.errors()[0]['msg']}")

# --- Invalid: '@' present but no domain after it ---
try:
    p = PatientV5(name='Nitish', email='nitish@', age=35)
    # '@' is there but nothing after it — still not valid
except ValidationError as e:
    print(f"Bad email 'nitish@'       -> {e.errors()[0]['msg']}")

print()


# ============================================================
# STEP 6b: AnyUrl  —  Validating Web Links / URLs
# ============================================================
# Just like EmailStr validates email format,
# AnyUrl validates that a field contains a proper URL.
#
# AnyUrl checks two things:
#   1. Does it have a SCHEME?  (http://, https://, ftp://, etc.)
#   2. Does it have a HOST?    (google.com, api.myapp.com, etc.)
#
# Examples:
#   'https://google.com'             -> VALID
#   'http://localhost:8000'          -> VALID  (useful in dev)
#   'https://linkedin.com/in/nitish' -> VALID
#   'linkedin.com/in/nitish'         -> INVALID  (no scheme!)
#   'not-a-url'                      -> INVALID  (no scheme, no host)
#
# Usage: declare the field as AnyUrl  —  that's it.
# No @field_validator, no regex, no custom logic needed.
#
# Real FastAPI use-cases:
#   - User profile / website links
#   - LinkedIn / social media URLs
#   - Webhook callback endpoints
# ============================================================


class PatientV6(BaseModel):
    name: str
    email: EmailStr         # validates email format   (from STEP 6 above)
    linkedin_url: AnyUrl    # validates URL format     (new in STEP 6b)
    age: int


print("=== STEP 6b: AnyUrl ===")

# --- Valid URL ---
try:
    p = PatientV6(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='https://linkedin.com/in/nitish',
        age=35
    )
    print("Valid patient ->")
    print("  name        :", p.name)
    print("  email       :", p.email)
    print("  linkedin    :", p.linkedin_url)
except ValidationError as e:
    print(e)

# --- Invalid: domain only, no 'https://' scheme ---
try:
    p = PatientV6(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='linkedin.com/in/nitish',   # missing 'https://'
        age=35
    )
except ValidationError as e:
    print(f"\nBad URL 'linkedin.com/in/nitish' -> {e.errors()[0]['msg']}")
    # Pydantic catches: URL scheme (http, https, etc.) is missing

# --- Invalid: total nonsense string ---
try:
    p = PatientV6(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='not-a-url',     # no scheme, no host at all
        age=35
    )
except ValidationError as e:
    print(f"Bad URL 'not-a-url'              -> {e.errors()[0]['msg']}")

print()


# ============================================================
# STEP 7: Field()  —  Adding Constraints Directly in the Model
# ============================================================
# So far, to add custom rules (e.g. age > 0), we used @field_validator.
# But for SIMPLE, COMMON constraints Pydantic gives us a shortcut: Field()
#
# Field() lets you define rules INLINE — right where you declare the field.
# No separate function, no decorator, no boilerplate.
#
# Most-used Field() parameters:
#
#   max_length=N    -> string (or list) can have at most N characters/items
#   min_length=N    -> string (or list) must have at least N characters/items
#   gt=N            -> number must be Greater Than N          (gt = greater than)
#   lt=N            -> number must be Less Than N             (lt = less than)
#   ge=N            -> number must be Greater than or Equal N (ge = >=)
#   le=N            -> number must be Less than or Equal N    (le = <=)
#   default=...     -> default value if the field is not provided
#   description=... -> human-readable note shown in API docs (Swagger)
#
# When to use Field() vs @field_validator?
#   Use Field()          for simple, single-field numeric/string limits
#   Use @field_validator  for complex logic (e.g. checking two fields together,
#                         calling an external service, applying regex, etc.)
# ============================================================


class PatientV7(BaseModel):
    # name: str   PLUS   max_length=50
    # -> name cannot be longer than 50 characters
    # -> if someone passes a 51-char name, Pydantic raises ValidationError
    name: str = Field(max_length=50)

    # email and linkedin are already smart types — no Field() needed here
    email: EmailStr
    linkedin_url: AnyUrl

    # age: int   PLUS   gt=0, lt=120
    # -> age must be > 0  (gt = greater than 0, so 0 itself is NOT allowed)
    # -> age must be < 120 (lt = less than 120, so 120 itself is NOT allowed)
    # This replaces the @field_validator we wrote in STEP 3 — same result, less code!
    age: int = Field(gt=0, lt=120)

    # weight: float   PLUS   gt=0
    # -> weight must be a positive float (cannot be 0 or negative)
    weight: float = Field(gt=0)

    # married has a plain default — no Field() needed, just = False
    married: bool = False

    # allergies: Optional[List[str]]   PLUS   max_length=5
    # -> the list itself can have at most 5 items
    # -> Optional means it can also be None (patient might have no allergies)
    # -> default=None means it is not required when creating a patient
    allergies: Optional[List[str]] = Field(default=None, max_length=5)

    # contact_details is a plain Dict — no extra constraints needed
    contact_details: Dict[str, str]


print("=== STEP 7: Field() Constraints ===")

# --- Valid: all constraints satisfied ---
try:
    p = PatientV7(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='https://linkedin.com/in/nitish',
        age=35,
        weight=72.5,
        allergies=['pollen', 'dust'],
        contact_details={'phone': '9999999999'}
    )
    print("Valid patient ->")
    print("  name      :", p.name)
    print("  age       :", p.age)
    print("  weight    :", p.weight)
    print("  allergies :", p.allergies)
except ValidationError as e:
    print(e)

# --- Invalid: name too long (> 50 chars) ---
try:
    p = PatientV7(
        name='A' * 51,          # 51 characters — exceeds max_length=50
        email='nitish@example.com',
        linkedin_url='https://linkedin.com/in/nitish',
        age=35,
        weight=72.5,
        contact_details={'phone': '9999999999'}
    )
except ValidationError as e:
    print(f"\nName too long     -> {e.errors()[0]['msg']}")

# --- Invalid: age = 0  (gt=0 means strictly greater than 0) ---
try:
    p = PatientV7(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='https://linkedin.com/in/nitish',
        age=0,                  # 0 is NOT > 0
        weight=72.5,
        contact_details={'phone': '9999999999'}
    )
except ValidationError as e:
    print(f"Age = 0 (gt=0)    -> {e.errors()[0]['msg']}")

# --- Invalid: age = 120  (lt=120 means strictly less than 120) ---
try:
    p = PatientV7(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='https://linkedin.com/in/nitish',
        age=120,                # 120 is NOT < 120
        weight=72.5,
        contact_details={'phone': '9999999999'}
    )
except ValidationError as e:
    print(f"Age = 120 (lt=120) -> {e.errors()[0]['msg']}")

# --- Invalid: too many allergies (> 5 items in the list) ---
try:
    p = PatientV7(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='https://linkedin.com/in/nitish',
        age=35,
        weight=72.5,
        allergies=['a', 'b', 'c', 'd', 'e', 'f'],  # 6 items — exceeds max_length=5
        contact_details={'phone': '9999999999'}
    )
except ValidationError as e:
    print(f"Too many allergies -> {e.errors()[0]['msg']}")

# --- Optional field: no allergies passed at all -> defaults to None ---
try:
    p = PatientV7(
        name='Nitish',
        email='nitish@example.com',
        linkedin_url='https://linkedin.com/in/nitish',
        age=35,
        weight=72.5,
        contact_details={'phone': '9999999999'}
        # allergies not passed -> defaults to None (Optional + default=None)
    )
    print(f"\nNo allergies passed -> allergies = {p.allergies}")
except ValidationError as e:
    print(e)

print()


# ============================================================
# SUMMARY — What we covered in pydantic3.py
# ============================================================
#
# IMPORTANT NOTE on List[str]  (user's own observation):
# -------------------------------------------------------
# Agar hum sirf  List  likhte (bina [str] ke), toh Python ko
# pata nahi ki list ke andar kya hoga — int? str? kuch bhi?
# List[str]  likhne se Pydantic guarantee karta hai ki list mein
# SIRF strings honge, koi int ya koi aur type nahi.
# Yahi reason hai hum  List[str]  likhte hain, not just  List.
#
# Checkboxes:
# [OK] Richer field types   : float, bool, List[str], Dict[str,str]
# [OK] Optional & defaults  : Optional[str] = None,  List[str] = []
# [OK] Field validators     : @field_validator for custom rules
# [OK] Model methods        : model_dump, model_dump_json, model_copy
# [OK] Nested models        : Address inside Patient
# [OK] Special types        : EmailStr -> email, AnyUrl -> URL validation
# [OK] Field() constraints  : max_length, gt, lt — inline rules without
#                             writing a separate @field_validator
#
# Next up -> pydantic4.py: model_config, strict mode,
#            computed fields, and model_validator (multi-field rules)
# ============================================================
