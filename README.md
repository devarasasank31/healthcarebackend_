# Healthcare Backend (Django + DRF + PostgreSQL + JWT)

This project is a backend system for a **healthcare application** built using **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT authentication (SimpleJWT)**.

## 📖 Documentation

**For complete, detailed documentation**, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)

**For API testing results**, see [API_TEST_RESULTS.md](API_TEST_RESULTS.md)

The comprehensive documentation includes:
- Complete project structure explanation
- Database schema with all data types and relationships
- Detailed explanation of models, serializers, views, URLs, and admin
- Step-by-step request-response flows
- All settings explained in detail
- Authentication & security mechanisms
- Beginner-friendly explanations (no Django knowledge required)

The API test results include:
- 22 comprehensive test scenarios executed
- All endpoints verified and working
- Authentication, validation, and error handling tested
- 100% success rate on all tests

---

## Features

- Django + DRF backend
- PostgreSQL database (configured via `DATABASE_URL`)
- JWT authentication using `djangorestframework-simplejwt`
- REST APIs for Patients, Doctors, and Patient–Doctor Mappings
- Error handling + validation
- Environment variables for sensitive configuration
- Admin panel for data management

---

## Tech Stack

- Python 3.9+ (3.10+ recommended)
- Django 4.2 (LTS)
- Django REST Framework
- djangorestframework-simplejwt (JWT auth)
- PostgreSQL (any online provider supported)
- dj-database-url (parses `DATABASE_URL`)
- python-dotenv (loads `.env`)

---

## Project Structure

```
healthcare_backend_simple/
├─ manage.py
├─ requirements.txt
├─ .env.example
├─ api/
│  ├─ models.py
│  ├─ serializers.py
│  ├─ views.py
│  ├─ urls.py
│  ├─ admin.py
│  └─ migrations/
└─ healthcare_simple/
   ├─ settings.py
   ├─ urls.py
   ├─ wsgi.py
   └─ asgi.py
```

### What each package/file is for

#### `healthcare_simple/` (project package)
- `settings.py`
  - Loads environment variables from `.env`
  - Configures **PostgreSQL** using `DATABASE_URL`
  - Configures DRF + SimpleJWT authentication
- `urls.py`
  - Routes all API calls under `/api/` to `api.urls`
- `wsgi.py` / `asgi.py`
  - Deployment entry points (WSGI/ASGI)

#### `api/` (single app for all APIs)
- `models.py`
  - Contains database models:
    - `TimeStampedModel`: abstract base model with `created_at` and `updated_at`
    - `Patient`: owned by a user (`owner`)
    - `Doctor`
    - `PatientDoctorMapping`: mapping between a Patient and a Doctor (unique per pair)
- `serializers.py`
  - Request/response validation and transformation:
    - `RegisterSerializer`: creates a Django user using `{name, email, password}`
    - `EmailTokenObtainPairSerializer`: logs in using `{email, password}` and returns JWT tokens
    - `PatientSerializer`, `DoctorSerializer`: CRUD serializers
    - `PatientDoctorMappingSerializer`: validates ownership + prevents duplicate assignments
- `views.py`
  - API implementation:
    - `RegisterView`: `POST /api/auth/register/`
    - `LoginView`: `POST /api/auth/login/`
    - `PatientViewSet`: `/api/patients/` CRUD (scoped to logged-in user)
    - `DoctorViewSet`: `/api/doctors/` CRUD
    - `MappingListCreateView`: `GET/POST /api/mappings/`
    - `MappingDetailView`:
      - `GET /api/mappings/<patient_id>/` → doctors for that patient
      - `DELETE /api/mappings/<id>/` → deletes mapping by mapping id
- `urls.py`
  - Defines all routes as required by the assignment

---

## Setup and Run

### 1) Create virtual environment
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY` (required)
- `DATABASE_URL` (required; must be PostgreSQL)

Example:
```env
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
```

> Note: Many hosted Postgres providers require SSL; keep `sslmode=require` if needed.

### 4) Run migrations
```bash
python manage.py migrate
```

> **Note:** Migrations have been consolidated into a single initial migration (`0001_initial.py`). No need to run `makemigrations` unless you modify models.

### 5) Create a superuser (optional, for admin panel)
```bash
python manage.py createsuperuser
```

Access admin panel at: `http://127.0.0.1:8000/admin/`

### 6) Run the server
```bash
python manage.py runserver
```

API base URL:
- `http://127.0.0.1:8000/api/`

---

## Authentication (JWT)

### Register
`POST /api/auth/register/`

Request JSON:
```json
{
  "name": "Asha",
  "email": "asha@example.com",
  "password": "StrongPass123"
}
```

### Login (returns JWT tokens)
`POST /api/auth/login/`

Request JSON:
```json
{
  "email": "asha@example.com",
  "password": "StrongPass123"
}
```

Response JSON:
```json
{
  "refresh": "....",
  "access": "...."
}
```

### Use the access token
Add this header to all protected requests:
```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### 1) Authentication
- `POST /api/auth/register/`  
  Register a new user with `name, email, password`
- `POST /api/auth/login/`  
  Login and get JWT tokens

(Extra standard endpoint)
- `POST /api/auth/token/refresh/`  
  Use refresh token to get a new access token

### 2) Patient Management (Authenticated users only)
- `POST /api/patients/`  
  Create a patient (owned by the logged-in user)
- `GET /api/patients/`  
  List patients created by the logged-in user
- `GET /api/patients/<id>/`  
  Retrieve a specific patient (only if owned by user)
- `PUT /api/patients/<id>/`  
  Update a patient (only if owned by user)
- `DELETE /api/patients/<id>/`  
  Delete a patient (only if owned by user)

Patient JSON fields:
```json
{
  "name": "John Doe",
  "age": 30,
  "gender": "male",
  "address": "Pune"
}
```
> `gender` must be one of: `male`, `female`, `other`

### 3) Doctor Management (Authenticated users only)
- `POST /api/doctors/`
- `GET /api/doctors/`
- `GET /api/doctors/<id>/`
- `PUT /api/doctors/<id>/`
- `DELETE /api/doctors/<id>/`

Doctor JSON fields:
```json
{
  "name": "Dr. Smith",
  "specialization": "Cardiology"
}
```

### 4) Patient–Doctor Mapping
- `POST /api/mappings/`  
  Assign a doctor to a patient (patient must belong to the logged-in user)
- `GET /api/mappings/`  
  List mappings for the logged-in user’s patients
- `GET /api/mappings/<patient_id>/`  
  Get all doctors assigned to a specific patient (patient must belong to user)
- `DELETE /api/mappings/<id>/`  
  Remove a doctor from a patient (deletes mapping by mapping id)

Create mapping request JSON:
```json
{
  "patient": 1,
  "doctor": 2
}
```

---

## Validation and Error Handling (simple and clear)

- **Patients are user-scoped**
  - You only see/modify/delete patients you created.
- **Mappings are protected**
  - You cannot assign doctors to someone else’s patient.
  - Duplicate assignments are blocked (same patient + doctor).
- **Delete safety**
  - Patients and doctors use `on_delete=PROTECT` in mappings.
  - If you try to delete a patient/doctor that still has mappings, you get a clear error:
    - “Cannot delete ... Please delete all associated patient-doctor mappings first.”

---

## Notes / Design Decisions

- Email login is supported by storing `username = email` internally for simplicity.
- The assignment specifies:
  - `GET /api/mappings/<patient_id>/`
  - `DELETE /api/mappings/<id>/`
  To keep URLs minimal and match the spec, the same path is used and interpreted by method:
  - **GET** treats the path parameter as `patient_id`
  - **DELETE** treats the path parameter as `mapping_id`

---

## Troubleshooting

### Django says DATABASE_URL is not set
Create `.env` (copy from `.env.example`) and set a PostgreSQL connection string.

### Login works but protected endpoints return 401
Ensure you send the header:
```
Authorization: Bearer <access_token>
```

### Invalid gender value
Send lowercase values: `male`, `female`, or `other`.
