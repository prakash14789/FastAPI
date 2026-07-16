# 🏥 FastAPI & Pydantic Learning Project

> A hands-on, well-documented learning project covering **FastAPI** REST API development and **Pydantic v2** data validation in Python — built from scratch to teach real-world API patterns.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic)](https://docs.pydantic.dev/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-purple)](https://www.uvicorn.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [FastAPI — Patient Management System](#-fastapi--patient-management-system)
  - [Features & Endpoints](#features--endpoints)
  - [Patient Data Model](#patient-data-model)
  - [Auto-Computed Fields (BMI & Verdict)](#auto-computed-fields-bmi--verdict)
  - [Running the API](#running-the-api)
  - [API Usage Examples](#api-usage-examples)
  - [Error Handling](#error-handling)
  - [Data Storage](#data-storage)
- [Pydantic Tutorial](#-pydantic-tutorial)
  - [1 — Why Pydantic?](#1--why-pydantic)
  - [2 — Field Validators](#2--field-validators)
  - [3 — Model Validators](#3--model-validators)
  - [4 — Field Constraints](#4--field-constraints)
  - [5 — Nested Models](#5--nested-models)
  - [6 — Serialization](#6--serialization)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Key Concepts Covered](#-key-concepts-covered)
- [Learning Path](#%EF%B8%8F-learning-path)
- [Contributing](#-contributing)

---

## 🔭 Overview

This project is a **structured, code-first learning resource** for two of the most important Python backend tools:

| Tool | Role in this Project |
|------|----------------------|
| **FastAPI** | Builds the REST API — routing, request handling, HTTP responses |
| **Pydantic v2** | Validates all incoming data — types, constraints, computed fields |

The **FastAPI section** builds a complete **Patient Management System** — a real-world-style REST API that stores patient records in a JSON file and exposes endpoints for reading, filtering, sorting, and creating patients.

The **Pydantic section** is a progressive, 6-file tutorial that teaches every major Pydantic v2 feature from scratch, with detailed inline comments explaining *why* each feature exists.

---

## 📁 Project Structure

```
FastAPI/                          ← root of this repository
│
├── Fast API/
│   ├── main.py                   # FastAPI app — Patient Management System
│   ├── patients.json             # JSON file used as a flat-file database
│   └── venv/                     # Python virtual environment (not committed)
│
├── Pydantic tutorial/
│   ├── 1_pydantic_why.py         # Why Pydantic? BaseModel, types, ValidationError
│   ├── 2_field_validator.py      # @field_validator — per-field custom validation
│   ├── 3_model_validator.py      # @model_validator — cross-field validation
│   ├── 4_field_constraints.py    # Field(gt=, lt=, min_length=, ...) constraints
│   ├── 5_nested_models.py        # Composing Pydantic models inside models
│   └── 6_serialization.py        # model_dump(), model_dump_json(), model_validate()
│
├── .gitignore                    # Excludes venv/, __pycache__/, etc.
└── README.md                     # This file
```

---

## 🚀 FastAPI — Patient Management System

A fully functional REST API that manages patient health records. Patients are stored in a JSON flat file (`patients.json`) and are validated by a Pydantic model before being saved.

### Features & Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/` | Welcome message | — |
| `GET` | `/about` | About the API | — |
| `GET` | `/view` | Retrieve **all** patients | — |
| `GET` | `/patient/{patient_id}` | Get a **single** patient by ID | Path param: `patient_id` (e.g. `P001`) |
| `GET` | `/sort` | Sort patients by a numeric field | Query params: `sort_by`, `order` |
| `POST` | `/create` | Add a **new** patient | JSON request body |

---

### Patient Data Model

The `Patient` Pydantic model defines **what a valid patient looks like**. FastAPI uses it to:
- Automatically validate incoming POST request bodies
- Reject bad data with a `422 Unprocessable Entity` error
- Generate the Swagger UI form automatically

```python
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal

class Patient(BaseModel):
    id:     Annotated[str,   Field(..., description='ID of the patient', examples=['P001'])]
    name:   Annotated[str,   Field(..., description='Name of the patient')]
    city:   Annotated[str,   Field(..., description='City where the patient lives')]
    age:    Annotated[int,   Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender')]
    height: Annotated[float, Field(..., gt=0, description='Height in metres')]
    weight: Annotated[float, Field(..., gt=0, description='Weight in kg')]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:   return 'Underweight'
        elif self.bmi < 25:   return 'Normal'
        elif self.bmi < 30:   return 'Overweight'
        else:                 return 'Obese'
```

**Field reference table:**

| Field | Type | Rule | Notes |
|-------|------|------|-------|
| `id` | `str` | Required | Used as the key in the JSON store (e.g. `"P001"`) |
| `name` | `str` | Required | Full name of the patient |
| `city` | `str` | Required | City of residence |
| `age` | `int` | Required, `1 <= age <= 119` | `gt=0, lt=120` enforced by Pydantic |
| `gender` | `Literal` | `male` / `female` / `others` | Any other value → `422` error |
| `height` | `float` | Required, `> 0` | In **metres** (e.g. `1.75`) |
| `weight` | `float` | Required, `> 0` | In **kilograms** (e.g. `70.0`) |
| `bmi` | `float` | **Auto-computed** | `weight / height²`, rounded to 2 d.p. |
| `verdict` | `str` | **Auto-computed** | Derived from BMI range (see below) |

---

### Auto-Computed Fields (BMI & Verdict)

`bmi` and `verdict` are **never sent by the client** — they are computed server-side by Pydantic using `@computed_field` + `@property`.

**BMI Formula:**
```
BMI = weight (kg) / height (m)²
```

**Verdict Classification (WHO Standard):**

| BMI Range | Verdict |
|-----------|---------|
| `< 18.5` | `Underweight` |
| `18.5 – 24.9` | `Normal` |
| `25.0 – 29.9` | `Overweight` |
| `>= 30.0` | `Obese` |

**Example:**
- `weight = 70 kg`, `height = 1.75 m`
- `BMI = 70 / (1.75²) = 70 / 3.0625 = 22.86` → **Normal**

---

### Running the API

#### Prerequisites

- Python 3.10 or higher
- `pip` (comes with Python)

#### Setup

```bash
# 1. Clone the repository
git clone https://github.com/prakash14789/FastAPI.git
cd FastAPI

# 2. Navigate into the Fast API folder
cd "Fast API"

# 3. Create and activate a virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install fastapi uvicorn

# 5. Start the development server
uvicorn main:app --reload
```

#### Access the API

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Root endpoint |
| `http://127.0.0.1:8000/docs` | **Swagger UI** — interactive API explorer |
| `http://127.0.0.1:8000/redoc` | **ReDoc** — alternative API documentation |

> Tip: The Swagger UI at `/docs` lets you test every endpoint directly from the browser — no Postman or curl needed.

---

### API Usage Examples

#### GET /view — Retrieve all patients

```bash
curl http://127.0.0.1:8000/view
```

**Response:**
```json
{
  "P001": {
    "name": "Ananya Sharma",
    "city": "Guwahati",
    "age": 28,
    "gender": "female",
    "height": 1.65,
    "weight": 90.0,
    "bmi": 33.06,
    "verdict": "Obese"
  }
}
```

---

#### GET /patient/{patient_id} — Get a single patient

```bash
curl http://127.0.0.1:8000/patient/P001
```

**Response (200 OK):**
```json
{
  "name": "Ananya Sharma",
  "city": "Guwahati",
  "age": 28,
  "gender": "female",
  "height": 1.65,
  "weight": 90.0,
  "bmi": 33.06,
  "verdict": "Obese"
}
```

**Response (404 Not Found):**
```json
{ "detail": "Patient not found" }
```

---

#### GET /sort — Sort patients by a field

```bash
# Sort by BMI ascending (default)
curl "http://127.0.0.1:8000/sort?sort_by=bmi"

# Sort by weight descending
curl "http://127.0.0.1:8000/sort?sort_by=weight&order=desc"
```

**Valid values:**
- `sort_by`: `height` | `weight` | `bmi`
- `order`: `asc` (default) | `desc`

**Error (400 Bad Request):**
```json
{ "detail": "Invalid field select from ['height', 'weight', 'bmi']" }
```

---

#### POST /create — Add a new patient

```bash
curl -X POST http://127.0.0.1:8000/create \
  -H "Content-Type: application/json" \
  -d '{
    "id": "P010",
    "name": "Rahul Gupta",
    "city": "Delhi",
    "age": 25,
    "gender": "male",
    "height": 1.75,
    "weight": 70
  }'
```

> Do NOT include `bmi` or `verdict` in the request body — they are auto-computed server-side.

**Response (201 Created):**
```json
{ "message": "patient created successfully" }
```

**Response (400 — duplicate ID):**
```json
{ "detail": "Patient already exists" }
```

**Response (422 — validation failure):**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "Input should be less than 120",
      "type": "less_than"
    }
  ]
}
```

---

### Error Handling

The API uses standard HTTP status codes and `HTTPException` for all error responses:

| Status Code | Meaning | When it Happens |
|-------------|---------|-----------------|
| `200 OK` | Success | Successful GET requests |
| `201 Created` | Resource created | Successful `POST /create` |
| `400 Bad Request` | Client error | Duplicate patient ID, invalid sort field/order |
| `404 Not Found` | Not found | `GET /patient/{id}` with a non-existent ID |
| `422 Unprocessable Entity` | Validation error | Invalid field types or constraint violations in POST body |

---

### Data Storage

Patient data is stored in a flat JSON file (`patients.json`). Each patient is keyed by their `id`:

```json
{
  "P001": {
    "name": "Ananya Sharma",
    "city": "Guwahati",
    "age": 28,
    "gender": "female",
    "height": 1.65,
    "weight": 90.0,
    "bmi": 33.06,
    "verdict": "Obese"
  }
}
```

> **Note:** `id` is stored as the dictionary key (not a field inside the object) to avoid redundancy. When creating a patient, `model_dump(exclude=['id'])` is used to serialize only the non-key fields.

---

## 📘 Pydantic Tutorial

A **6-file progressive series** teaching Pydantic v2 from the ground up. Each file is standalone — run it directly with `python filename.py`.

```bash
cd "Pydantic tutorial"
python 1_pydantic_why.py
```

---

### 1 — Why Pydantic?

**File:** `1_pydantic_why.py`

Introduces the core problem Pydantic solves: validating raw, untrusted input data without writing endless `if/else` checks.

**What you will learn:**
- Declaring a `BaseModel` with type hints
- Pydantic's automatic type validation and coercion
- `Optional` fields with defaults
- How `ValidationError` works and how to read its output

**Key demo:**
```python
from pydantic import BaseModel, ValidationError

class Patient(BaseModel):
    name: str
    age: int
    weight: float
    married: bool
    allergies: List[str]

# Passing a string where int is expected raises ValidationError
try:
    bad = Patient(name='Nitish', age='not_a_number', ...)
except ValidationError as e:
    for err in e.errors():
        print(f"field: {err['loc'][0]} -> {err['msg']}")
```

---

### 2 — Field Validators

**File:** `2_field_validator.py`

Teaches `@field_validator` — a decorator that lets you write custom validation logic for individual fields, beyond what built-in type constraints can express.

**What you will learn:**
- Writing `@field_validator` methods
- Validating string formats (capitalizing names, checking patterns)
- `mode='before'` vs `mode='after'` — when the validator runs
- Raising `ValueError` from inside a validator

**Key demo:**
```python
from pydantic import BaseModel, field_validator

class Patient(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def name_must_be_capitalized(cls, v: str) -> str:
        if not v[0].isupper():
            raise ValueError('Name must start with a capital letter')
        return v
```

---

### 3 — Model Validators

**File:** `3_model_validator.py`

Teaches `@model_validator` — used when validation logic needs to look at **multiple fields at once** (cross-field validation).

**What you will learn:**
- `@model_validator(mode='after')` — runs after all fields are validated
- Accessing `self` to read multiple fields simultaneously
- Implementing business rules that span fields

**Key demo:**
```python
from pydantic import BaseModel, model_validator

class Patient(BaseModel):
    age: int
    emergency_contact: str | None = None

    @model_validator(mode='after')
    def check_emergency_contact(self) -> 'Patient':
        if self.age > 60 and not self.emergency_contact:
            raise ValueError('Emergency contact is required for patients over 60')
        return self
```

---

### 4 — Field Constraints

**File:** `4_field_constraints.py`

Explores the full range of `Field(...)` constraints — a declarative way to enforce rules without writing custom validators.

**Constraint reference:**

| Constraint | Meaning | Example |
|------------|---------|---------|
| `gt=0` | Greater than 0 | `age: int = Field(gt=0)` |
| `lt=120` | Less than 120 | `age: int = Field(lt=120)` |
| `ge=18` | Greater than or equal to 18 | — |
| `le=100` | Less than or equal to 100 | — |
| `min_length=2` | String/list min length | `name: str = Field(min_length=2)` |
| `max_length=50` | String/list max length | — |
| `pattern=r'^[A-Z]'` | Regex match | — |

---

### 5 — Nested Models

**File:** `5_nested_models.py`

Shows how to compose Pydantic models inside other models — the standard approach for representing structured, hierarchical data.

**What you will learn:**
- Embedding one `BaseModel` as a field in another
- How Pydantic recursively validates nested structures
- The difference between passing a nested dict vs. a model instance

**Key demo:**
```python
class Address(BaseModel):
    city: str
    state: str
    pin: str  # str not int — pin codes can have leading zeros

class Patient(BaseModel):
    name: str
    address: Address  # Pydantic validates Address fields recursively

# Pass a raw dict — Pydantic auto-converts it to Address
p = Patient(name='Rahul', address={'city': 'Delhi', 'state': 'Delhi', 'pin': '110001'})
```

---

### 6 — Serialization

**File:** `6_serialization.py`

Covers converting Pydantic models to and from Python dicts and JSON strings — essential for working with APIs, databases, and file storage.

**What you will learn:**

| Method | Direction | Output |
|--------|-----------|--------|
| `model_dump()` | Model → Python dict | `dict` |
| `model_dump_json()` | Model → JSON string | `str` |
| `model_validate(dict)` | Python dict → Model | `BaseModel` |
| `model_validate_json(str)` | JSON string → Model | `BaseModel` |

**Advanced options:**
```python
# Include only specific fields
patient.model_dump(include={'name', 'email'})

# Exclude specific fields (or nested sub-fields)
patient.model_dump(exclude={'address': ['state']})

# Only fields explicitly set by the user — useful for PATCH requests
patient.model_dump(exclude_unset=True)
```

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Core language |
| **FastAPI** | 0.100+ | Web framework — routing, dependency injection, OpenAPI |
| **Pydantic v2** | 2.x | Data validation, serialization, computed fields |
| **Uvicorn** | Latest | ASGI server — runs the FastAPI application |
| **JSON** | Built-in | Flat-file data storage for patients |

---

## 📚 Key Concepts Covered

### Pydantic v2
- `BaseModel` — defining data schemas with type hints
- `Field(...)` — constraints (`gt`, `lt`, `min_length`, `pattern`), metadata (`description`, `examples`)
- `Annotated[type, Field(...)]` — combining type + constraints cleanly
- `@field_validator` — custom per-field validation
- `@model_validator` — cross-field / business rule validation
- `@computed_field` + `@property` — auto-calculated fields (never sent by client)
- `Literal[...]` — enum-like type restriction
- `Optional[T]` — nullable fields with defaults
- `model_dump()` / `model_dump_json()` — serialization
- `model_validate()` / `model_validate_json()` — deserialization
- `ValidationError` — catching and reading validation errors

### FastAPI
- `@app.get` / `@app.post` — defining HTTP route handlers
- Path parameters — `@app.get('/patient/{patient_id}')` + `Path(...)`
- Query parameters — `Query(...)` with description and defaults
- Request body — Pydantic model as function parameter for POST endpoints
- `HTTPException` — returning structured error responses
- `JSONResponse` — returning custom status codes (e.g. `201 Created`)
- `status` module — using named HTTP status code constants
- Auto-generated docs — Swagger UI (`/docs`) and ReDoc (`/redoc`)

---

## 🗺️ Learning Path

Recommended order to work through this project:

```
1. Pydantic tutorial/1_pydantic_why.py       → Understand the core value proposition
2. Pydantic tutorial/2_field_validator.py    → Write custom field-level rules
3. Pydantic tutorial/3_model_validator.py    → Write cross-field rules
4. Pydantic tutorial/4_field_constraints.py  → Master declarative constraints
5. Pydantic tutorial/5_nested_models.py      → Model complex, nested data
6. Pydantic tutorial/6_serialization.py      → Convert models to/from dicts and JSON
                        ↓
7. Fast API/main.py                          → See it all come together in a real API
```

---

## 🤝 Contributing

Contributions are welcome! If you find a bug, want to add a new endpoint, or improve the tutorial examples:

1. Fork this repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add: description of change"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

*Built with love as a learning resource for Python developers getting started with FastAPI and Pydantic.*
