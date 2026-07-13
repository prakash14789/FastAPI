# ============================================================
# 2_field_validator.py  -  Custom field-level validation rules
# ============================================================
# @field_validator lets you write your OWN rules for a single field.
# When Pydantic's built-in type check is not enough.
#
# TWO modes:
#   mode='after'  (DEFAULT) — Pydantic converts type FIRST, your code runs second.
#                             'v' inside your function is already the correct type.
#                             Use when: you want to CHECK a value after it's typed.
#
#   mode='before'           — Your code runs FIRST on the raw input.
#                             'v' could be str, float, int — anything the caller sent.
#                             Use when: you want to CLEAN or TRANSFORM messy input.
# ============================================================

from pydantic import BaseModel, ValidationError, field_validator


# --------------------------------------------------------
# Part A: mode='after'  (default — no need to write mode=)
# --------------------------------------------------------
# 'v' is already the right type (str, int) — Pydantic converted it first.
# Good for: range checks, format checks, business rules.
class Patient(BaseModel):
    name: str
    age: int

    @field_validator('name')        # mode='after' is the default
    @classmethod
    def name_not_empty(cls, v):
        # v is already a str here
        if not v.strip():
            raise ValueError('Name cannot be empty.')
        return v.strip().title()    # clean whitespace + capitalise: 'nitish' -> 'Nitish'

    @field_validator('age')         # mode='after' default — v is already int
    @classmethod
    def age_valid(cls, v):
        if v <= 0 or v >= 120:
            raise ValueError('Age must be between 1 and 119.')
        return v


print("=== mode='after' (default) ===")
try:
    p = Patient(name='  nitish  ', age=35)
    print("Valid ->", p)            # name cleaned to 'Nitish'
except ValidationError as e:
    print(e)

try:
    Patient(name='', age=35)        # empty name -> error
except ValidationError as e:
    print("Empty name ->", e.errors()[0]['msg'])

try:
    Patient(name='Nitish', age=-5)  # invalid age -> error
except ValidationError as e:
    print("age=-5     ->", e.errors()[0]['msg'])
print()


# --------------------------------------------------------
# Part B: mode='before'
# --------------------------------------------------------
# Your function runs FIRST before Pydantic converts the type.
# 'value' is the RAW input — could be '35' (string), 35.9 (float), etc.
# Good for: cleaning messy input, transforming before type check.
#
# Comparison (mode='after' version, commented out):
#   @field_validator('age')          <- no mode = mode='after'
#   def validate_age(cls, v):
#       # v is already int here, Pydantic converted it
#       if 0 < v < 100: return v
#       raise ValueError('Age should be between 0 and 100')
class PatientStrict(BaseModel):
    name: str
    age: int

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, value):
        # value is RAW — could be '35' (a string) sent by mistake
        # We check the range BEFORE Pydantic casts it to int
        if 0 < value < 100:
            return value            # Pydantic will then cast this to int
        else:
            raise ValueError('Age should be between 0 and 100')


print("=== mode='before' ===")
try:
    p = PatientStrict(name='Nitish', age=35)
    print("Valid  ->", p)
except ValidationError as e:
    print(e)

try:
    PatientStrict(name='Nitish', age=150)
except ValidationError as e:
    print("age=150 ->", e.errors()[0]['msg'])

try:
    PatientStrict(name='Nitish', age=-5)
except ValidationError as e:
    print("age=-5  ->", e.errors()[0]['msg'])
