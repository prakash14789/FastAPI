# 🏥 FastAPI & Pydantic Learning Project

A hands-on learning project covering **FastAPI** REST API development and **Pydantic** data validation in Python.

---

## 📁 Project Structure

```
├── Fast API/
│   ├── main.py          # FastAPI application — Patient Management System
│   └── patients.json    # JSON file used as the data store
│
└── Pydantic tutorial/
    ├── 1_pydantic_why.py        # Why Pydantic? Introduction & motivation
    ├── 2_field_validator.py     # Field-level validators
    ├── 3_model_validator.py     # Model-level validators
    ├── 4_field_constraints.py   # Field constraints (gt, lt, min_length, etc.)
    ├── 5_nested_models.py       # Nested Pydantic models
    └── 6_serialization.py       # Serialization with model_dump / model_dump_json
```

---

## 🚀 Fast API — Patient Management System

A fully functional REST API built with **FastAPI** and **Pydantic** to manage patient records stored in a JSON file.

### Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/about` | About the API |
| `GET` | `/view` | Retrieve all patients |
| `GET` | `/patient/{patient_id}` | Get a patient by ID (path param) |
| `GET` | `/sort` | Sort patients by `height`, `weight`, or `bmi` |
| `POST` | `/create` | Add a new patient (request body validated by Pydantic) |

### Patient Model Fields

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | `str` | Required |
| `name` | `str` | Required |
| `city` | `str` | Required |
| `age` | `int` | Required, 1–119 |
| `gender` | `Literal` | `male`, `female`, or `others` |
| `height` | `float` | Required, > 0 (in metres) |
| `weight` | `float` | Required, > 0 (in kg) |
| `bmi` | `float` | **Auto-computed** — `weight / height²` |
| `verdict` | `str` | **Auto-computed** — Underweight / Normal / Overweight / Obese |

### Running the API

```bash
# Navigate into the Fast API folder
cd "Fast API"

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn

# Start the development server
uvicorn main:app --reload
```

Then open your browser at:
- **Swagger UI (interactive docs):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Example — Create a Patient (POST /create)

```json
{
  "id": "P010",
  "name": "Rahul Gupta",
  "city": "Delhi",
  "age": 25,
  "gender": "male",
  "height": 1.75,
  "weight": 70
}
```

> `bmi` and `verdict` are automatically computed — do **not** include them in the request body.

---

## 📘 Pydantic Tutorial

A series of standalone Python scripts covering Pydantic v2 concepts progressively:

| File | Topic |
|------|-------|
| `1_pydantic_why.py` | Introduction — why Pydantic over plain dicts |
| `2_field_validator.py` | `@field_validator` — custom per-field validation |
| `3_model_validator.py` | `@model_validator` — cross-field validation |
| `4_field_constraints.py` | `Field(gt=, lt=, min_length=, ...)` constraints |
| `5_nested_models.py` | Composing models inside models |
| `6_serialization.py` | `model_dump()`, `model_dump_json()`, `model_json_schema()` |

### Running a tutorial script

```bash
cd "Pydantic tutorial"
python 1_pydantic_why.py
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI** — modern, fast web framework for building APIs
- **Pydantic v2** — data validation and settings management
- **Uvicorn** — ASGI server for running FastAPI
- **JSON** — lightweight file-based data storage

---

## 📚 Key Concepts Covered

- Pydantic `BaseModel`, `Field`, `Annotated`
- `@computed_field` + `@property` for derived fields
- `Literal` types for enum-like validation
- Path parameters, query parameters, and request bodies in FastAPI
- HTTP methods: `GET` and `POST`
- Proper HTTP status codes and `HTTPException` handling
- Auto-generated interactive API documentation (Swagger UI)
