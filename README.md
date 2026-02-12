# 🏥 Healthcare Backend API

A RESTful backend service for managing **patients, doctors, and their relationships**, built using **Django REST Framework** with secure **JWT authentication**.

This project simulates the backend of a real healthcare platform where authenticated users can register, maintain patient records, assign doctors, and manage medical associations securely.

---

## Why I Built This

I wanted to understand how real production backends work — not just CRUD pages, but:

* user authentication
* permission-based data access
* relational database modeling
* API design used by frontend/mobile apps

So I designed a healthcare system because it naturally requires:

* ownership rules (a user can only access their own patients)
* relationships (many doctors ↔ many patients)
* validation and data protection

---

## Tech Stack

* **Backend:** Django, Django REST Framework
* **Authentication:** JWT (SimpleJWT)
* **Database:** PostgreSQL (via DATABASE_URL)
* **Environment Management:** python-dotenv
* **Deployment Ready:** dj-database-url compatible

---

## Core Features

### Authentication

* User registration
* Login with email & password
* JWT access + refresh tokens
* Protected endpoints using Bearer token

### Patient Management

Each user manages their own patients:

* Create, update, delete, list patients
* Data isolation (users cannot access other users' records)

### Doctor Management

* Add doctors with specialization
* Full CRUD operations

### Patient–Doctor Assignment

* Assign doctors to a patient
* Prevent duplicate assignments
* Prevent deleting records with active relationships

---

## API Overview

| Method   | Endpoint              | Description                |
| -------- | --------------------- | -------------------------- |
| POST     | `/api/auth/register/` | Register user              |
| POST     | `/api/auth/login/`    | Login & get JWT            |
| GET/POST | `/api/patients/`      | Manage patients            |
| GET/POST | `/api/doctors/`       | Manage doctors             |
| GET/POST | `/api/mappings/`      | Assign doctors to patients |

Protected routes require:

```
Authorization: Bearer <access_token>
```

---

## Database Design

Main models:

* **User** → owns patients
* **Patient** → belongs to a user
* **Doctor**
* **PatientDoctorMapping** → many-to-many relationship

Important rules implemented:

* A user cannot view another user’s patients
* A doctor cannot be assigned twice to the same patient
* Deleting records with active relations is prevented

---

## How to Run Locally

### 1. Clone repository

```
git clone https://github.com/devarasasank31/healthcarebackend_.git
cd healthcarebackend_
```

### 2. Create virtual environment

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure environment

Create a `.env` file:

```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
```

### 5. Run migrations

```
python manage.py migrate
```

### 6. Start server

```
python manage.py runserver
```

Server:

```
http://127.0.0.1:8000/
```

---

## Example Request

**Login**

```
POST /api/auth/login/
```

```
{
  "email": "user@email.com",
  "password": "password123"
}
```

Response:

```
{
  "refresh": "...",
  "access": "..."
}
```

---

## What I Learned

* Designing REST APIs using DRF ViewSets & Serializers
* Implementing JWT authentication
* Handling permissions and ownership logic
* Modeling relational data in PostgreSQL
* Structuring a scalable Django backend
* Using environment variables securely

---

## Future Improvements

* Docker containerization
* Rate limiting
* Appointment scheduling
* Medical record attachments
* Deployment (Render/AWS)

---

## Author

**Sasank Devarasetty**
Information Science Engineering Student
Aspiring Backend Developer
