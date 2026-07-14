from fastapi import FastAPI, Path, HTTPException, Query, status
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal

app = FastAPI()


# ---------------------------------------------------------------
# Patient — Pydantic model used to validate POST request body
# ---------------------------------------------------------------
# When a client sends JSON to create a new patient, FastAPI
# automatically passes it to this model for validation.
#
# Annotated[type, Field(...)]  — combines type hint + validation rules
#   Field(...)  — '...' means the field is REQUIRED (no default)
#   gt=0        — greater than 0
#   lt=120      — less than 120
#   description — shown in Swagger UI /docs
#   examples    — sample value shown in Swagger UI
#
# Literal['male', 'female', 'others']
#   — restricts gender to only these 3 string values
#   — any other value -> 422 Validation Error
# ---------------------------------------------------------------
class Patient(BaseModel):
    id:     Annotated[str,   Field(..., description='ID of the patient', examples=['P001'])]
    name:   Annotated[str,   Field(..., description='Name of the patient')]
    city:   Annotated[str,   Field(..., description='City where the patient is living')]
    age:    Annotated[int,   Field(..., gt=0, lt=120, description='Age of the patient')]   # must be 1–119
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]  # only 3 allowed values
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]  # must be > 0
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]   # must be > 0

    # -----------------------------------------------------------
    # @computed_field + @property  — auto-calculated field
    # -----------------------------------------------------------
    # bmi is NOT sent by the client in the request body.
    # Pydantic computes it automatically from height and weight.
    # It is included in model_dump() and model_dump_json() output.
    #
    # Formula: BMI = weight(kg) / height(m)^2
    # round(..., 2) -> keeps 2 decimal places
    # -----------------------------------------------------------
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi

    # -----------------------------------------------------------
    # verdict — derived from the computed bmi value
    # -----------------------------------------------------------
    # BMI ranges (standard classification):
    #   < 18.5          -> Underweight
    #   18.5 to < 25    -> Normal
    #   25   to < 30    -> Overweight
    #   >= 30           -> Obese
    #
    # Uses self.bmi (the computed field above) — no extra input needed
    # -----------------------------------------------------------
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'


def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data


# saves the updated data dict back into patients.json
def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)


@app.get("/")
def hello():
    return {'message': 'Patient Management System API'}

@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}

@app.get('/view')
def view():
    data = load_data()

    return data


# path parameter
@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(...,description = 'id of a patient' , Example = 'P001')):
    # load all the patients
    data = load_data()
# status add kiya kyuki jab error tha tab bhi 200 hi http de rha tha 
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')


# query parameter
@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'),
                  order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')

    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data


# ============================================================
# SO FAR — we only used GET requests
# ============================================================
# Everything above uses @app.get(...)
#
# GET is used to READ / RETRIEVE data from the server.
# The client asks "give me this data" and the server responds.
#
# We covered:
#   GET /          -> welcome message
#   GET /about     -> about message
#   GET /view      -> all patients
#   GET /patient/{patient_id}  -> one patient by ID  (path parameter)
#   GET /sort      -> sorted patients by field/order  (query parameter)
#
# In GET requests:
#   - Data is passed via URL (path params or query params)
#   - No request body is sent
#   - Used only for fetching, never for creating/updating
#
# ============================================================
# NEXT — we will use POST to CREATE new data
# ============================================================
# POST is used to SEND data TO the server to create a new record.
#
# What is a REQUEST BODY?
# -----------------------
# A request body is the portion of an HTTP request that contains
# data sent by the client to the server.
# It is typically used in HTTP methods such as POST or PUT to
# transmit structured data (e.g., JSON, XML, form-data) for the
# purpose of creating or updating resources on the server.
# The server parses the request body to extract the necessary
# information and perform the intended operation.
#
# How the flow looks (from the diagram):
#
#   +--------+    HTTP request (POST)    +--------+
#   | Client | ------------------------> | Server |
#   +--------+                           +--------+
#        |
#      [JSON]         <- this JSON travels as the REQUEST BODY
#        |
#    request body
#
# In GET  -> no body, data is in the URL (path/query params)
# In POST -> data travels in the REQUEST BODY as JSON
#
# Key difference from GET:
#   - POST sends data in the REQUEST BODY (not in the URL)
#   - The body is usually JSON
#   - Pydantic model is used to validate that incoming JSON
#
# How it works in FastAPI:
#   1. Client sends a POST request with a JSON body
#   2. FastAPI reads the body and passes it to a Pydantic model
#   3. Pydantic validates all fields automatically
#   4. If valid -> we save it; if invalid -> 422 error is returned
#
# 3-step POST flow (from diagram):
# ---------------------------------
#   Step 1)  Client ---(POST)---> Server
#              [json]
#                ↓
#           request body        <- JSON sent by client lands here
#
#   Step 2)  [Validate] -------> Pydantic model
#            Pydantic checks every field:
#              - correct types?  e.g. age must be int, not "thirty"
#              - required fields present?
#              - constraints satisfied?
#
#            Type coercion example:
#              "thirty" (str)  ->  ❌ rejected  (expected int)
#               30      (int)  ->  ✅ accepted
#                           thirty  →  30  <- Pydantic won't guess, it rejects
#
#   Step 3)  json file ---------> new record added
#            After validation passes, we write the new patient
#            into patients.json as a new entry
#
# Example of what's coming:
#
#   @app.post('/create')
#   def create_patient(patient: Patient):
#
#       data = load_data()
#
#       # check if the patient already exists
#       if patient.id in data:
#           raise HTTPException(status_code=400, detail='Patient already exists')
#
#       # new patient add to the database
#       # exclude 'id' because it's used as the KEY in the JSON dict, not a value
#       data[patient.id] = patient.model_dump(exclude=['id'])
#
#       # save into the json file
#       save_data(data)
#
#       return JSONResponse(status_code=201, content={'message': 'patient created successfully'})
# ============================================================


@app.post('/create')
def create_patient(patient: Patient):

    data = load_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database
    # exclude 'id' because it's used as the KEY in the JSON dict, not a value
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into the json file
    save_data(data)

    return JSONResponse(status_code=201, content={'message': 'patient created successfully'})
