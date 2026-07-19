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

The repository is organised into two main folders:

- **Fast API/** — contains the FastAPI application (`main.py`) and the JSON flat-file database (`patients.json`)
- **Pydantic tutorial/** — contains six standalone Python scripts, one per major Pydantic topic
- **.gitignore** — excludes virtual environments, `__pycache__`, and other generated files
- **README.md** — this file

---

## 🚀 FastAPI — Patient Management System

A fully functional REST API that manages patient health records. Patients are stored in a JSON flat file and are validated by a Pydantic model before being saved.

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

**Field reference table:**

| Field | Type | Rule | Notes |
|-------|------|------|-------|
| `id` | `str` | Required | Used as the key in the JSON store (e.g. `"P001"`) |
| `name` | `str` | Required | Full name of the patient |
| `city` | `str` | Required | City of residence |
| `age` | `int` | Required, 1 to 119 | Enforced by Pydantic with `gt=0, lt=120` |
| `gender` | `Literal` | `male` / `female` / `others` | Any other value triggers a `422` error |
| `height` | `float` | Required, greater than 0 | In **metres** (e.g. `1.75`) |
| `weight` | `float` | Required, greater than 0 | In **kilograms** (e.g. `70.0`) |
| `bmi` | `float` | **Auto-computed** | weight divided by height squared, rounded to 2 d.p. |
| `verdict` | `str` | **Auto-computed** | Derived from BMI range using WHO classification |

---

### Auto-Computed Fields (BMI & Verdict)

`bmi` and `verdict` are **never sent by the client** — they are computed server-side automatically by Pydantic using `@computed_field` and `@property`.

- **BMI** is calculated as: weight (kg) divided by height (m) squared
- **Verdict** is then derived from the WHO BMI classification:

| BMI Range | Verdict |
|-----------|---------|
| Below 18.5 | Underweight |
| 18.5 to 24.9 | Normal |
| 25.0 to 29.9 | Overweight |
| 30.0 and above | Obese |

**Example:** A patient weighing 70 kg at 1.75 m height gets BMI = 22.86, which falls in the **Normal** range.

---

### Running the API

#### Prerequisites

- Python 3.10 or higher
- pip (comes with Python)

#### Setup Steps

1. Clone the repository and navigate into it
2. Move into the `Fast API` folder
3. Create and activate a Python virtual environment
4. Install dependencies: `fastapi` and `uvicorn`
5. Start the development server: `uvicorn main:app --reload`

#### Access the API

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Root endpoint |
| `http://127.0.0.1:8000/docs` | **Swagger UI** — interactive API explorer |
| `http://127.0.0.1:8000/redoc` | **ReDoc** — alternative API documentation |

> **Tip:** The Swagger UI at `/docs` lets you test every endpoint directly from the browser — no Postman or curl needed.

---

### Error Handling

The API uses standard HTTP status codes and `HTTPException` for all error responses:

| Status Code | Meaning | When it Happens |
|-------------|---------|-----------------|
| `200 OK` | Success | Successful GET requests |
| `201 Created` | Resource created | Successful `POST /create` |
| `400 Bad Request` | Client error | Duplicate patient ID or invalid sort field/order |
| `404 Not Found` | Not found | `GET /patient/{id}` with a non-existent ID |
| `422 Unprocessable Entity` | Validation error | Invalid field types or constraint violations in POST body |

---

### Data Storage

Patient data is stored in a flat JSON file (`patients.json`). Each patient is keyed by their `id`. The `id` is intentionally stored as the dictionary key — not as a field inside the object — to avoid redundancy. When creating a patient, Pydantic's serialization is used to exclude the `id` field from the stored value.

---

## 📘 Pydantic Tutorial

A **6-file progressive series** teaching Pydantic v2 from the ground up. Each file is standalone — you can run it directly with `python filename.py` from inside the `Pydantic tutorial/` folder.

---

### 1 — Why Pydantic?

**File:** `1_pydantic_why.py`

Introduces the core problem Pydantic solves: validating raw, untrusted input data without writing endless if/else checks.

**What you will learn:**
- Declaring a `BaseModel` with type hints
- Pydantic's automatic type validation and coercion
- `Optional` fields with defaults
- How `ValidationError` works and how to read its output
- Why Python type hints alone are not enough — Pydantic enforces them at runtime

---

### 2 — Field Validators

**File:** `2_field_validator.py`

Teaches `@field_validator` — a decorator that lets you write custom validation logic for individual fields, beyond what built-in type constraints can express.

**What you will learn:**
- Writing `@field_validator` methods on a model
- Validating string formats (e.g. capitalising names, checking patterns)
- `mode='before'` — validator runs on the raw input before Pydantic processes the field
- `mode='after'` — validator runs after the field has already been parsed and typed
- Raising `ValueError` from inside a validator to reject bad values

---

### 3 — Model Validators

**File:** `3_model_validator.py`

Teaches `@model_validator` — used when validation logic needs to look at **multiple fields at once** (cross-field validation). A single field validator cannot see other fields, so this is where model-level rules live.

**What you will learn:**
- `@model_validator(mode='after')` — runs after all individual fields are validated
- Accessing `self` to read multiple fields simultaneously
- Implementing business rules that span fields (e.g. patients over 60 must have an emergency contact)

---

### 4 — Field Constraints

**File:** `4_field_constraints.py`

Explores the full range of `Field(...)` constraints — a declarative way to enforce rules without writing custom validators.

**Constraint reference:**

| Constraint | Meaning |
|------------|---------|
| `gt=0` | Value must be greater than 0 |
| `lt=120` | Value must be less than 120 |
| `ge=18` | Value must be greater than or equal to 18 |
| `le=100` | Value must be less than or equal to 100 |
| `min_length=2` | String or list must have at least 2 characters/items |
| `max_length=50` | String or list must have at most 50 characters/items |
| `pattern=...` | String must match the given regular expression |

---

### 5 — Nested Models

**File:** `5_nested_models.py`

Shows how to compose Pydantic models inside other models — the standard approach for representing structured, hierarchical data like a patient with a full address.

**What you will learn:**
- Embedding one `BaseModel` as a field in another
- How Pydantic recursively validates nested structures automatically
- The difference between passing a nested dict vs. a model instance — Pydantic accepts both
- Why pin codes should be `str` not `int` (leading zeros would be lost with an integer type)

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

**Advanced serialization options:**
- `include={'name', 'email'}` — serialize only specific fields
- `exclude={'address': ['state']}` — exclude specific fields or nested sub-fields
- `exclude_unset=True` — only serialize fields explicitly set by the user (useful for PATCH requests)

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
- `Annotated[type, Field(...)]` — combining type and constraints cleanly
- `@field_validator` — custom per-field validation
- `@model_validator` — cross-field and business rule validation
- `@computed_field` with `@property` — auto-calculated fields that are never sent by the client
- `Literal[...]` — enum-like type restriction to a fixed set of values
- `Optional[T]` — nullable fields with default values
- `model_dump()` and `model_dump_json()` — serialization
- `model_validate()` and `model_validate_json()` — deserialization
- `ValidationError` — catching and reading validation errors

### FastAPI
- `@app.get` and `@app.post` — defining HTTP route handlers
- Path parameters — dynamic URL segments with automatic type validation
- Query parameters — optional or required URL query strings with descriptions and defaults
- Request body — Pydantic model as a function parameter for POST endpoints
- `HTTPException` — returning structured error responses with status codes
- `JSONResponse` — returning custom status codes (e.g. `201 Created`)
- `status` module — using named HTTP status code constants
- Auto-generated docs — Swagger UI (`/docs`) and ReDoc (`/redoc`)

---

## 🗺️ Learning Path

Recommended order to work through this project:

1. `Pydantic tutorial/1_pydantic_why.py` — Understand the core value proposition
2. `Pydantic tutorial/2_field_validator.py` — Write custom field-level rules
3. `Pydantic tutorial/3_model_validator.py` — Write cross-field rules
4. `Pydantic tutorial/4_field_constraints.py` — Master declarative constraints
5. `Pydantic tutorial/5_nested_models.py` — Model complex, nested data
6. `Pydantic tutorial/6_serialization.py` — Convert models to/from dicts and JSON
7. `Fast API/main.py` — See it all come together in a real API

---

## 🤝 Contributing

Contributions are welcome! If you find a bug, want to add a new endpoint, or improve the tutorial examples:

1. Fork this repository
2. Create a new branch
3. Make your changes and commit with a clear message
4. Push to your fork
5. Open a Pull Request

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

*Built with love as a learning resource for Python developers getting started with FastAPI and Pydantic.*
