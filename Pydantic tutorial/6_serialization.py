# ============================================================
# 6_serialization.py  -  Converting models to dict / JSON
# ============================================================
# Serialization = converting a Pydantic model INTO another format
#   model_dump()      -> Python dict
#   model_dump_json() -> JSON string
#
# You can control WHAT gets serialized using:
#   include={...}  -> only these fields
#   exclude={...}  -> everything EXCEPT these fields
#
# Deserialization = creating a model FROM external data
#   model_validate(dict)      -> from a Python dict
#   model_validate_json(str)  -> from a JSON string
# ============================================================

from pydantic import BaseModel, EmailStr, AnyUrl


# --- Nested model (same as file 5) ---
class Address(BaseModel):
    city: str
    state: str
    pin: str    # str not int — pin codes can have leading zeros (e.g. '01234')


class Patient(BaseModel):
    name: str
    gender: str
    age: int
    address: Address
    email: EmailStr
    linkedin: AnyUrl


# --- Create a patient instance ---
address1 = Address(city='Gurgaon', state='Haryana', pin='122002')

patient_dict = {'name': 'nitish', 'gender': 'male', 'age': 35, 'address': address1,
                'email': 'nitish@example.com', 'linkedin': 'https://linkedin.com/in/nitish'}

patient1 = Patient(**patient_dict)

print("=== model_dump() — full dict ===")
print(patient1.model_dump())
print()

print("=== model_dump(exclude) — drop a nested field ===")
temp = patient1.model_dump(exclude={'address': ['state']})   # exclude address.state
print(temp)
print(type(temp))
print()

print("=== model_dump(include) — only specific fields ===")
print(patient1.model_dump(include={'name', 'email'}))
print()

print("=== model_dump_json() — JSON string ===")
json_str = patient1.model_dump_json()
print(json_str)
print(type(json_str))
print()

print("=== model_validate() — dict -> model ===")
data = {'name': 'Amit', 'gender': 'male', 'age': 28,
        'address': {'city': 'Delhi', 'state': 'Delhi', 'pin': '110001'},
        'email': 'amit@example.com', 'linkedin': 'https://linkedin.com/in/amit'}
p2 = Patient.model_validate(data)
print(p2)
print()

print("=== model_validate_json() — JSON string -> model ===")
p3 = Patient.model_validate_json(json_str)
print(p3.name, p3.address.city)
print()

# --- exclude_unset=True — only fields the user explicitly passed ---
# Useful when doing partial updates (PATCH requests in APIs)
# Default fields that were never touched won't appear in the dump

class PatientWithDefaults(BaseModel):
    name: str
    gender: str
    age: int
    city: str = 'Unknown'       # has a default
    is_active: bool = True      # has a default

p4 = PatientWithDefaults(name='Ravi', gender='male', age=30)  # city & is_active not passed

print("=== exclude_unset=True — only explicitly set fields ===")
print("With    exclude_unset:", p4.model_dump(exclude_unset=True))   # only name, gender, age
print("Without exclude_unset:", p4.model_dump())                      # includes city & is_active defaults
