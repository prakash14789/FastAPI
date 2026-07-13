# ============================================================
# THE PROBLEM: No Type Enforcement (What the Junior Dev Did)
# ============================================================
# A junior developer called insert_patient_data() and passed
# age as a STRING ('thirty') instead of an INTEGER (30).
# Python did NOT catch this mistake, and the bad data
# silently got inserted into the database — causing a BLUNDER.
# ============================================================

# def insert_patient_data(name, age):
#     print(name)
#     print(age)
#     print('inserted into database')
#
# insert_patient_data('nitish', 'thirty')  # BUG: 'thirty' is a string, not an int!
#                                          # Python accepted it without any error,
#                                          # corrupting the database record.


# ============================================================
# THE SOLUTION: Pydantic for Runtime Type Validation
# ============================================================
# With Pydantic, if anyone tries to pass age as a string that
# cannot be coerced into an integer, it will raise a
# ValidationError IMMEDIATELY — before touching the database.
# ============================================================

from pydantic import BaseModel, ValidationError


class PatientData(BaseModel):
    name: str   # must be a string
    age: int    # must be an integer — Pydantic will enforce this!


def insert_patient_data(patient: PatientData):
    """
    Inserts patient data into the database.
    Accepts a validated PatientData model to guarantee type safety.
    """
    print(patient.name)
    print(patient.age)
    print('inserted into database')


# Correct usage — works perfectly
try:
    patient = PatientData(name='nitish', age=30)
    insert_patient_data(patient)
except ValidationError as e:
    print(f"Validation Error: {e}")


# Wrong usage — mimics what the junior developer did
# Pydantic will raise a ValidationError and STOP execution
# before any bad data reaches the database.
try:
    bad_patient = PatientData(name='nitish', age='thirty')  # 'thirty' is invalid!
    insert_patient_data(bad_patient)
except ValidationError as e:
    print(f"\nValidation Error caught! Bad data blocked from database:")
    print(e)
