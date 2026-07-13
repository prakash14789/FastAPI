# ============================================================
# 5_nested_models.py  -  A model inside another model
# ============================================================
# Real-world data is structured — a Patient has an Address,
# an Order has a Product, etc.
#
# In Pydantic you can use one BaseModel as a FIELD TYPE in another.
# Pydantic validates BOTH the outer and inner model automatically.
#
# How it works:
#   1. You pass the nested data as a plain dict.
#   2. Pydantic auto-converts that dict into the nested model object.
#   3. If the inner data is wrong -> ValidationError on that field.
#
# Benefits:
#   - Clean, structured data — access as  patient.address.city
#   - model_dump() flattens everything to a nested dict automatically
#   - model_json_schema() documents the nested structure for Swagger
#
# Special types (built-in smart validators, no custom code needed):
#   EmailStr  -> validates email format (@, domain, TLD)
#                requires:  pip install pydantic[email]
#   AnyUrl    -> validates URL format (must have https:// + host)
# ============================================================

from pydantic import BaseModel, ValidationError, EmailStr, AnyUrl


# --- The nested model (inner) ---
class Address(BaseModel):
    city: str
    state: str
    pin: str    # str not int — pin codes can have leading zeros (e.g. '01234')


# --- The outer model uses Address as a field type ---
class Patient(BaseModel):
    name: str
    gender: str
    age: int
    address: Address    # Pydantic will validate this as an Address object
    email: EmailStr     # built-in email validator — no custom code needed
    linkedin: AnyUrl    # built-in URL validator  — no custom code needed


print("=== Nested Models ===")

# Pass address as a plain dict — Pydantic auto-converts it to Address
try:
    p = Patient(
        name='Nitish', gender='male', age=35,
        address={
            'city': 'Gurgaon',
            'state': 'Haryana',
            'pin': '122002'         # dict gets converted to Address object
        },
        email='nitish@example.com',
        linkedin='https://linkedin.com/in/nitish'
    )
    print("Valid patient ->", p.name, p.age)
    print("  city  :", p.address.city)          # access nested fields
    print("  state :", p.address.state)
    print("  pin   :", p.address.pin)
    print("  email :", p.email)
    print("  linkedin:", p.linkedin)
    print()
    print("model_dump() ->", p.model_dump())    # address appears as nested dict
except ValidationError as e:
    print(e)

print()

# --- What if the nested data is wrong? ---
print("=== Invalid nested data ===")
try:
    p = Patient(
        name='Nitish', gender='male', age=35,
        address={
            'city': 'Gurgaon',
            'state': 'Haryana',
            # pin is missing — it's a required field in Address
        },
        email='nitish@example.com',
        linkedin='https://linkedin.com/in/nitish'
    )
except ValidationError as e:
    print("Missing pin ->", e.errors()[0]['loc'], e.errors()[0]['msg'])

try:
    p = Patient(
        name='Nitish', gender='male', age=35,
        address={'city': 'Gurgaon', 'state': 'Haryana', 'pin': '122002'},
        email='not-an-email',       # bad email format
        linkedin='https://linkedin.com/in/nitish'
    )
except ValidationError as e:
    print("Bad email   ->", e.errors()[0]['msg'])

try:
    p = Patient(
        name='Nitish', gender='male', age=35,
        address={'city': 'Gurgaon', 'state': 'Haryana', 'pin': '122002'},
        email='nitish@example.com',
        linkedin='linkedin.com'     # missing https:// scheme
    )
except ValidationError as e:
    print("Bad URL     ->", e.errors()[0]['msg'])
