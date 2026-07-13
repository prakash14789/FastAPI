from pydantic import BaseModel

# ============================================================
# STEP 1: Define the Pydantic Model
# ============================================================
# We create a Patient class using Pydantic's BaseModel.
# This acts as a strict schema — it guarantees that:
#   - 'name' will always be a string (str)
#   - 'age'  will always be an integer (int)
# If anyone passes wrong types, Pydantic throws a ValidationError.

class Patient(BaseModel):
    name: str
    age: int


# ============================================================
# STEP 2: What we WERE doing (OLD WAY — the problem)
# ============================================================
# Earlier, the function accepted raw 'name' and 'age' directly.
# This was unsafe because Python does NOT enforce types on its own.
# A junior developer could call it like:
#   insert_patient_data('nitish', 'thirty')  <-- 'thirty' is a string!
# Python would NOT complain, and the bad data would go into the database.

# def insert_patient_data(name, age):   # <-- no type safety!
#     print(name)
#     print(age)
#     print('inserted')


# ============================================================
# STEP 3: What we are NOW doing (NEW WAY — the solution)
# ============================================================
# Instead of passing raw 'name' and 'age' separately,
# we now pass a fully validated Patient object.
# Pydantic has already verified the types BEFORE this function
# is even called, so we can trust patient.name and patient.age
# are exactly the correct types.

def insert_patient_data(patient: Patient):   # <-- type-safe Patient object
    print(patient.name)
    print(patient.age)
    print('inserted')


# ============================================================
# STEP 4: Creating and passing the Patient object
# ============================================================
# We store the data in a dictionary first.
# Then unpack it with ** into the Patient model.
# Pydantic validates it here — if age were 'thirty', it would
# CRASH here with a ValidationError, NOT silently in the database.

patient_info = {'name': 'nitish', 'age': 30}

patient1 = Patient(**patient_info)   # <-- Pydantic validates here

# Now we call the function with the validated object.
# By this point, we are 100% sure the data is correct.
insert_patient_data(patient1)


# ============================================================
# STEP 5: What happens if we pass 'thirty' instead of 30?
# ============================================================
# Let's deliberately make the same mistake the junior developer made.
# We pass age as the string 'thirty' instead of the integer 30.
# Pydantic will IMMEDIATELY raise a ValidationError —
# the bad data never reaches the function, never touches the database.

from pydantic import ValidationError

bad_patient_info = {'name': 'nitish', 'age': 'thirty'}  # <-- wrong type!

try:
    patient2 = Patient(**bad_patient_info)   # Pydantic catches it RIGHT HERE
    insert_patient_data(patient2)            # this line will NEVER be reached
except ValidationError as e:
    print("\n--- Pydantic caught the error! ---")
    print(e)
    print("--- Bad data was BLOCKED. Database is safe! ---")
