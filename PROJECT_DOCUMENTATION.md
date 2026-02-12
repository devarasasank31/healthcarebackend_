# Healthcare Backend - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Technology Stack & Dependencies](#technology-stack--dependencies)
4. [Database Schema & Models](#database-schema--models)
5. [API Architecture](#api-architecture)
6. [Component Deep Dive](#component-deep-dive)
7. [Request-Response Flow](#request-response-flow)
8. [Configuration & Settings](#configuration--settings)
9. [Authentication & Security](#authentication--security)

---

## 🎯 Project Overview

This is a **Healthcare Management System** backend API built with Django and Django REST Framework. It allows users to:
- Register and authenticate
- Manage patient records
- Manage doctor information
- Create relationships between patients and doctors (patient-doctor mappings)

**Key Features:**
- User authentication with JWT (JSON Web Tokens)
- Role-based data access (users can only see their own patients)
- RESTful API endpoints
- Database protection against accidental data deletion
- Admin panel for system administration

---

## 📁 Project Structure

```
healthcare_backend_simple/
│
├── manage.py                      # Django's command-line utility
├── requirements.txt               # Python dependencies
├── README.md                      # Project readme
├── db.sqlite3                     # SQLite database file (generated)
├── .env                          # Environment variables (SECRET_KEY, DATABASE_URL)
├── .env.example                  # Template for environment variables
│
├── healthcare_simple/            # Main project configuration folder
│   ├── __init__.py              # Makes this a Python package
│   ├── settings.py              # All project settings and configuration
│   ├── urls.py                  # Root URL routing
│   ├── wsgi.py                  # WSGI server entry point for deployment
│   └── asgi.py                  # ASGI server entry point (for async)
│
└── api/                          # Our main application folder
    ├── __init__.py              # Makes this a Python package
    ├── apps.py                  # App configuration
    ├── models.py                # Database models (Patient, Doctor, Mapping)
    ├── serializers.py           # Data validation & JSON conversion
    ├── views.py                 # Business logic & request handlers
    ├── urls.py                  # API endpoint definitions
    ├── admin.py                 # Admin panel configuration
    │
    └── migrations/              # Database schema versions
        ├── __init__.py
        └── 0001_initial.py      # Initial database structure
```

### What Each Folder Does:

**`healthcare_simple/`** - Project Configuration
- Contains global settings, URL routing, and server configuration
- Think of this as the "control center" of the entire project

**`api/`** - Application Logic
- Contains all business logic for our healthcare system
- Models define data structure, views handle requests, serializers validate data

**`migrations/`** - Database Version Control
- Tracks changes to database structure over time
- Allows rolling back or updating database schema safely

---

## 🔧 Technology Stack & Dependencies

### Core Framework
**Django (v4.2.13+)**
- A high-level Python web framework
- Provides: database ORM, admin panel, authentication, security features
- Think of it as the foundation of the house

**Django REST Framework (v3.14+)**
- Extends Django to build RESTful APIs
- Provides: serializers (data validation), viewsets (CRUD operations), permissions
- Converts Python objects to JSON and vice versa

### Dependencies Explained

#### 1. **djangorestframework-simplejwt (v5.5+)**
**Purpose:** Authentication using JWT tokens

**What is JWT?**
- JSON Web Token - a secure way to authenticate users
- Instead of cookies, client receives a token after login
- Token is sent with each request to prove identity

**Why we use it:**
- Stateless authentication (server doesn't store sessions)
- Secure - tokens are cryptographically signed
- Mobile-friendly - works with any client (web, mobile, desktop)

**How it works in our project:**
1. User logs in → receives `access_token` (valid 60 minutes) and `refresh_token` (valid 1 day)
2. Client includes `access_token` in requests: `Authorization: Bearer <token>`
3. When `access_token` expires → use `refresh_token` to get a new one

#### 2. **psycopg2-binary (v2.9+)**
**Purpose:** PostgreSQL database adapter

**What it does:**
- Allows Django to communicate with PostgreSQL database
- PostgreSQL is a powerful, production-grade database
- More reliable than SQLite for real applications

**Why PostgreSQL over SQLite:**
- Better for multiple users accessing simultaneously
- More data types and features
- Industry standard for production apps

#### 3. **dj-database-url (v2.1+)**
**Purpose:** Parse database URLs

**What it does:**
- Converts a database URL into Django settings
- Example: `postgresql://user:pass@host:5432/dbname` → Django config

**Why it's useful:**
- Makes deployment easier (just set one environment variable)
- Common format used by hosting platforms (Heroku, Render, Railway)

#### 4. **python-dotenv (v1.0+)**
**Purpose:** Load environment variables from `.env` file

**What it does:**
- Reads `.env` file and makes variables available to Python
- Keeps secrets (passwords, API keys) out of code

**Example `.env` file:**
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DEBUG=True
```

**Why it's important:**
- Security: Never commit secrets to Git
- Flexibility: Different settings for dev/staging/production

---

## 💾 Database Schema & Models

### What is a Model?
A **model** is a Python class that represents a database table. Each attribute is a column in the table.

### Database Tables

#### 1. **User Table** (Built-in Django Model)
Manages user accounts and authentication.

| Column       | Data Type    | Description                          | Constraints        |
|--------------|--------------|--------------------------------------|--------------------|
| id           | Integer      | Unique identifier                    | Primary Key, Auto  |
| username     | String(150)  | Login username (we use email here)   | Unique, Required   |
| email        | String(254)  | User's email address                 | Required           |
| password     | String(128)  | Hashed password (never plain text)   | Required           |
| first_name   | String(150)  | User's name                          | Optional           |
| is_active    | Boolean      | Account is active                    | Default: True      |
| date_joined  | DateTime     | When user registered                 | Auto               |

**Why we don't modify this:** Django provides a robust, tested user system. We reuse it.

---

#### 2. **Patient Table**
Stores patient information.

```python
class Patient(TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")
    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    address = models.TextField(blank=True)
```

| Column       | Data Type    | Description                          | Constraints             |
|--------------|--------------|--------------------------------------|-------------------------|
| id           | BigInteger   | Unique identifier                    | Primary Key, Auto       |
| owner_id     | Integer      | User who created this patient        | Foreign Key → User      |
| name         | String(120)  | Patient's full name                  | Required                |
| age          | Integer      | Patient's age                        | Required, Positive Only |
| gender       | String(10)   | Patient's gender                     | Choices: male/female/other |
| address      | Text         | Patient's address                    | Optional (blank=True)   |
| created_at   | DateTime     | When record was created              | Auto, Read-only         |
| updated_at   | DateTime     | When record was last modified        | Auto-updates            |

**Field Type Explanations:**

- **ForeignKey(User, on_delete=CASCADE)**: 
  - Links each patient to a user (owner)
  - `on_delete=CASCADE`: If user is deleted → all their patients are deleted
  - `related_name="patients"`: Access user's patients via `user.patients.all()`

- **CharField(max_length=120)**:
  - Stores text up to 120 characters
  - Becomes VARCHAR(120) in database

- **PositiveIntegerField()**:
  - Only accepts positive numbers (0 and above)
  - Database enforces this constraint

- **TextField(blank=True)**:
  - Stores unlimited text
  - `blank=True`: Can be empty when submitting forms

- **DateTimeField(auto_now_add=True)**:
  - Automatically sets to current time when created
  - Never changes after creation

- **DateTimeField(auto_now=True)**:
  - Updates to current time whenever record is saved

**Gender Choices:**
```python
class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
```
- Restricts gender field to these three values only
- First value stored in DB, second shown to users

---

#### 3. **Doctor Table**
Stores doctor information.

```python
class Doctor(TimeStampedModel):
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120)
```

| Column          | Data Type    | Description                     | Constraints       |
|-----------------|--------------|-------------------------------- |-------------------|
| id              | BigInteger   | Unique identifier               | Primary Key, Auto |
| name            | String(120)  | Doctor's full name              | Required          |
| specialization  | String(120)  | Medical specialization          | Required          |
| created_at      | DateTime     | When record was created         | Auto, Read-only   |
| updated_at      | DateTime     | When record was last modified   | Auto-updates      |

**Note:** Doctors are global (not owned by specific users). Any user can assign any doctor to their patients.

---

#### 4. **PatientDoctorMapping Table**
Creates relationships between patients and doctors.

```python
class PatientDoctorMapping(TimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="mappings")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="mappings")
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["patient", "doctor"], name="uniq_patient_doctor")
        ]
```

| Column       | Data Type   | Description                        | Constraints             |
|--------------|-------------|------------------------------------|-------------------------|
| id           | BigInteger  | Unique identifier                  | Primary Key, Auto       |
| patient_id   | Integer     | Reference to patient               | Foreign Key → Patient   |
| doctor_id    | Integer     | Reference to doctor                | Foreign Key → Doctor    |
| created_at   | DateTime    | When mapping was created           | Auto, Read-only         |
| updated_at   | DateTime    | When mapping was last modified     | Auto-updates            |

**Special Constraints:**

1. **on_delete=PROTECT**: 
   - Cannot delete a patient or doctor if they have mappings
   - Must delete all mappings first
   - Prevents accidental data loss

2. **UniqueConstraint(fields=["patient", "doctor"])**:
   - Same patient-doctor pair cannot exist twice
   - Database enforces this at the database level
   - Prevents duplicate assignments

**Example Relationship:**
```
Patient "John Doe" (ID: 1) → Mapping → Doctor "Dr. Smith - Cardiology" (ID: 3)
Patient "John Doe" (ID: 1) → Mapping → Doctor "Dr. Lee - Neurology" (ID: 7)
```

---

### Database Relationships Diagram

```
┌─────────────┐
│    User     │
│  (Django)   │
│             │
│ - id        │
│ - username  │
│ - email     │
│ - password  │
└──────┬──────┘
       │
       │ 1:N (One user has many patients)
       │ CASCADE (delete user → delete patients)
       ▼
┌─────────────┐
│   Patient   │
│             │
│ - id        │
│ - owner_id  │◄─────────────────┐
│ - name      │                  │
│ - age       │                  │
│ - gender    │                  │
│ - address   │                  │
└──────┬──────┘                  │
       │                         │
       │ N:M (Many-to-Many)      │
       │ Via PatientDoctorMapping│
       │ PROTECT                 │
       ▼                         │
┌──────────────────┐             │
│ PatientDoctor    │             │
│    Mapping       │             │
│                  │             │
│ - id             │             │
│ - patient_id     ├─────────────┘
│ - doctor_id      ├──────────────┐
└──────────────────┘              │
                                  │
                                  │ PROTECT
                                  │
                                  ▼
                           ┌─────────────┐
                           │   Doctor    │
                           │             │
                           │ - id        │
                           │ - name      │
                           │ - specialty │
                           └─────────────┘
```

---

## 🏗️ API Architecture

### What is a RESTful API?

**REST** = Representational State Transfer

A way to design web APIs where:
- Each URL represents a resource (patient, doctor, etc.)
- HTTP methods define actions (GET, POST, PUT, DELETE)
- Data exchanged in JSON format

**HTTP Methods:**
- `GET`: Retrieve data (read)
- `POST`: Create new data
- `PUT`: Update entire resource
- `PATCH`: Update partial resource
- `DELETE`: Remove data

---

### API Endpoints

#### Authentication Endpoints

| Method | Endpoint              | Purpose                    | Auth Required |
|--------|-----------------------|----------------------------|---------------|
| POST   | `/api/auth/register/` | Create new user account    | No            |
| POST   | `/api/auth/login/`    | Login and get JWT tokens   | No            |
| POST   | `/api/auth/token/refresh/` | Refresh access token  | No (needs refresh token) |

#### Patient Endpoints

| Method | Endpoint              | Purpose                    | Auth Required |
|--------|-----------------------|----------------------------|---------------|
| GET    | `/api/patients/`      | List all user's patients   | Yes           |
| POST   | `/api/patients/`      | Create new patient         | Yes           |
| GET    | `/api/patients/{id}/` | Get specific patient       | Yes           |
| PUT    | `/api/patients/{id}/` | Update entire patient      | Yes           |
| PATCH  | `/api/patients/{id}/` | Update some patient fields | Yes           |
| DELETE | `/api/patients/{id}/` | Delete patient             | Yes           |

#### Doctor Endpoints

| Method | Endpoint             | Purpose                    | Auth Required |
|--------|----------------------|----------------------------|---------------|
| GET    | `/api/doctors/`      | List all doctors           | Yes           |
| POST   | `/api/doctors/`      | Create new doctor          | Yes           |
| GET    | `/api/doctors/{id}/` | Get specific doctor        | Yes           |
| PUT    | `/api/doctors/{id}/` | Update entire doctor       | Yes           |
| PATCH  | `/api/doctors/{id}/` | Update some doctor fields  | Yes           |
| DELETE | `/api/doctors/{id}/` | Delete doctor              | Yes           |

#### Mapping Endpoints

| Method | Endpoint               | Purpose                           | Auth Required |
|--------|------------------------|-----------------------------------|---------------|
| GET    | `/api/mappings/`       | List all patient-doctor mappings  | Yes           |
| POST   | `/api/mappings/`       | Assign doctor to patient          | Yes           |
| GET    | `/api/mappings/{id}/`  | Get doctors for specific patient  | Yes           |
| DELETE | `/api/mappings/{id}/`  | Remove patient-doctor assignment  | Yes           |

---

## 🔍 Component Deep Dive

### 1. Models (`api/models.py`)

**Purpose:** Define database structure and business logic

**What models do:**
- Define table structure (columns, data types)
- Define relationships between tables
- Provide helper methods (like `__str__` for display)
- Enforce data validation at database level

**Key Concepts:**

#### Abstract Base Model
```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

- `abstract = True`: This is NOT a real table, just a template
- Other models inherit these fields automatically
- DRY principle: Don't Repeat Yourself

#### Model Inheritance
```python
class Patient(TimeStampedModel):
    # Automatically has created_at and updated_at
    name = models.CharField(max_length=120)
    # ... other fields
```

#### String Representation
```python
def __str__(self):
    return f"{self.name} ({self.age})"
```
- Defines how object appears in admin panel or when printed
- Makes debugging easier

---

### 2. Serializers (`api/serializers.py`)

**Purpose:** Convert between Python objects and JSON, validate data

**What serializers do:**
- **Deserialization:** Convert JSON → Python objects (when receiving data)
- **Serialization:** Convert Python objects → JSON (when sending response)
- **Validation:** Check data is correct before saving to database
- **Custom logic:** Transform data during conversion

**Think of serializers as:**
- Translators between your database and the outside world
- Gatekeepers that validate incoming data

#### Example Flow:

**Client sends JSON:**
```json
{
    "name": "John Doe",
    "age": 45,
    "gender": "male",
    "address": "123 Main St"
}
```

**Serializer validates:**
- ✓ Is `name` present and under 120 chars?
- ✓ Is `age` a positive integer?
- ✓ Is `gender` one of the allowed choices?
- ✓ Is `address` optional?

**If valid:** Saves to database
**If invalid:** Returns error response

#### Serializer Types

**1. ModelSerializer**
```python
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "age", "gender", "address", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
```

- Automatically creates fields from model
- `fields`: Which model fields to include
- `read_only_fields`: Cannot be modified by client

**2. Custom Serializer**
```python
class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
```

- Manually define each field
- Used when not directly mapping to a model

#### Custom Validation

**Field-level validation:**
```python
def validate_email(self, value: str) -> str:
    if User.objects.filter(username=value).exists():
        raise serializers.ValidationError("A user with this email already exists.")
    return value
```

- Method name: `validate_<field_name>`
- Runs automatically when field is present
- Raise `ValidationError` if invalid

**Object-level validation:**
```python
def validate(self, attrs):
    patient = attrs.get("patient")
    doctor = attrs.get("doctor")
    
    if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
        raise serializers.ValidationError("This doctor is already assigned.")
    return attrs
```

- Validates multiple fields together
- Access all data via `attrs` dictionary

#### Custom Create Logic
```python
def create(self, validated_data):
    user = User.objects.create_user(
        username=validated_data["email"],
        email=validated_data["email"],
        password=validated_data["password"],
        first_name=validated_data["name"],
    )
    return user
```

- Defines how to create object from validated data
- Can add custom logic (like hashing passwords)

---

### 3. Views (`api/views.py`)

**Purpose:** Handle HTTP requests and return responses

**What views do:**
- Receive HTTP requests from clients
- Extract data from request (query params, body, headers)
- Call business logic (usually via serializers)
- Return HTTP responses (JSON, status codes)

**View Types:**

#### 1. APIView (Basic)
```python
class MappingDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id: int):
        # Handle GET request
        pass
    
    def delete(self, request, id: int):
        # Handle DELETE request
        pass
```

- Most flexible
- Define handlers for each HTTP method
- Full control over logic

#### 2. Generic Views
```python
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
```

- Pre-built views for common patterns
- Less code, automatic behavior
- `CreateAPIView`: Handles POST to create resources

**Common Generic Views:**
- `ListAPIView`: GET list of objects
- `CreateAPIView`: POST to create
- `RetrieveAPIView`: GET single object
- `UpdateAPIView`: PUT/PATCH to update
- `DestroyAPIView`: DELETE to remove
- `ListCreateAPIView`: GET list + POST create

#### 3. ViewSets (Most Powerful)
```python
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Patient.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

- Combines multiple views into one class
- Automatically handles: list, create, retrieve, update, delete
- Works with routers for automatic URL generation

**ViewSet Methods:**
- `get_queryset()`: Define which objects this user can see
- `perform_create()`: Custom logic before saving
- `perform_update()`: Custom logic before updating
- `perform_destroy()`: Custom logic before deleting

#### Permission Classes

**What they do:** Control who can access endpoints

```python
permission_classes = [IsAuthenticated]
```

- `AllowAny`: Anyone can access (public)
- `IsAuthenticated`: Must be logged in
- `IsAdminUser`: Must be staff/admin

**How it works:**
1. View checks permission before executing
2. If permission denied → 401/403 error
3. If allowed → continues to handler

#### Request Object

The `request` object contains all information about the HTTP request:

```python
request.user         # Currently authenticated user
request.data         # Request body (JSON)
request.query_params # URL query parameters (?page=1)
request.headers      # HTTP headers
request.method       # GET, POST, etc.
```

#### Response Object

```python
from rest_framework.response import Response
from rest_framework import status

return Response(data, status=status.HTTP_200_OK)
```

**Common Status Codes:**
- `200 OK`: Success
- `201 CREATED`: Resource created
- `204 NO_CONTENT`: Success, no body
- `400 BAD_REQUEST`: Invalid data
- `401 UNAUTHORIZED`: Not logged in
- `403 FORBIDDEN`: No permission
- `404 NOT_FOUND`: Resource doesn't exist
- `500 INTERNAL_SERVER_ERROR`: Server error

---

### 4. URLs (`api/urls.py`)

**Purpose:** Map URLs to views

**How URL routing works:**

#### Router (for ViewSets)
```python
router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patients")
router.register(r"doctors", DoctorViewSet, basename="doctors")
```

**Automatically creates these URLs:**
```
GET    /api/patients/          → list()
POST   /api/patients/          → create()
GET    /api/patients/{id}/     → retrieve()
PUT    /api/patients/{id}/     → update()
PATCH  /api/patients/{id}/     → partial_update()
DELETE /api/patients/{id}/     → destroy()
```

#### Manual URL Patterns
```python
urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("mappings/", MappingListCreateView.as_view(), name="mappings"),
    path("mappings/<int:id>/", MappingDetailView.as_view(), name="mapping_detail"),
]
```

**URL Components:**
- `"auth/register/"`: URL path
- `RegisterView.as_view()`: View to call
- `name="register"`: Internal name for reverse lookup
- `<int:id>`: Capture integer as `id` parameter

#### Including Other URLs
```python
path("", include(router.urls))
```
- Includes all router-generated URLs
- Useful for organizing large projects

---

### 5. Admin (`api/admin.py`)

**Purpose:** Configure Django admin panel

**What is Django Admin?**
- Built-in web interface for managing database
- Automatically generated from models
- Useful for staff to manage data without API

**Configuration:**

```python
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "age", "gender", "owner", "created_at")
    search_fields = ("name", "owner__username", "owner__email")
    list_filter = ("gender",)
```

**Options explained:**
- `@admin.register(Patient)`: Register this model in admin
- `list_display`: Columns to show in list view
- `search_fields`: Fields to search in search box
- `list_filter`: Add filters in sidebar
- `owner__username`: Follow foreign key relationship

**Access admin panel:**
- URL: `http://localhost:8000/admin/`
- Must create superuser: `python manage.py createsuperuser`

---

### 6. Apps (`api/apps.py`)

**Purpose:** App configuration

```python
class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
```

**What it does:**
- `default_auto_field`: Use 64-bit integers for auto IDs
- `name`: App name (must match folder name)

**When to modify:**
- Add app-specific settings
- Register signal handlers
- Run startup code

---

## 🔄 Request-Response Flow

### Example: Creating a New Patient

Let's trace a complete request from client to database and back.

#### Step 1: Client Sends Request

```http
POST /api/patients/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "name": "John Doe",
    "age": 45,
    "gender": "male",
    "address": "123 Main St"
}
```

#### Step 2: Django Receives Request

1. **Middleware Processing**
   - `SecurityMiddleware`: Checks security headers
   - `SessionMiddleware`: Handles sessions (not used with JWT)
   - `AuthenticationMiddleware`: Identifies user from JWT token

2. **URL Routing** (`healthcare_simple/urls.py` → `api/urls.py`)
   - Matches `/api/patients/` to `PatientViewSet`
   - POST method → calls `create()` method

#### Step 3: View Processing

```python
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

1. **Permission Check**
   - `IsAuthenticated` checks if user is logged in
   - If not → returns 401 Unauthorized
   - If yes → continues

2. **Get Queryset** (for filtering)
   - Not used for create, but defines accessible objects

3. **Serialization**
   - Creates `PatientSerializer` with request data
   - Validates data:
     * Is name present and ≤ 120 chars? ✓
     * Is age a positive integer? ✓
     * Is gender one of [male, female, other]? ✓
     * Is address valid (optional)? ✓

4. **Custom Create Logic**
   - `perform_create()` adds current user as owner
   - Saves to database

#### Step 4: Database Operation

```sql
INSERT INTO api_patient (owner_id, name, age, gender, address, created_at, updated_at)
VALUES (1, 'John Doe', 45, 'male', '123 Main St', '2026-02-12 10:30:00', '2026-02-12 10:30:00');
```

#### Step 5: Response Serialization

```python
PatientSerializer converts Patient object to JSON:
{
    "id": 42,
    "name": "John Doe",
    "age": 45,
    "gender": "male",
    "address": "123 Main St",
    "created_at": "2026-02-12T10:30:00Z",
    "updated_at": "2026-02-12T10:30:00Z"
}
```

#### Step 6: Client Receives Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": 42,
    "name": "John Doe",
    "age": 45,
    "gender": "male",
    "address": "123 Main St",
    "created_at": "2026-02-12T10:30:00Z",
    "updated_at": "2026-02-12T10:30:00Z"
}
```

---

### Example: User Registration Flow

#### Step 1: Client Request

```http
POST /api/auth/register/
Content-Type: application/json

{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "password": "securePassword123"
}
```

#### Step 2: View Processing

```python
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # No login required
    serializer_class = RegisterSerializer
```

#### Step 3: Serializer Validation

```python
class RegisterSerializer(serializers.Serializer):
    def validate_email(self, value: str) -> str:
        # Check if email already exists
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        # Create user with hashed password
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],  # Automatically hashed
            first_name=validated_data["name"]
        )
        return user
```

#### Step 4: Database Operations

```sql
-- Check if email exists
SELECT COUNT(*) FROM auth_user WHERE username = 'alice@example.com';

-- If doesn't exist, create user
INSERT INTO auth_user (username, email, password, first_name, date_joined, is_active)
VALUES ('alice@example.com', 'alice@example.com', 
        'pbkdf2_sha256$...', 'Alice Johnson', NOW(), true);
```

**Note:** Password is hashed using PBKDF2 with SHA256. Never stored in plain text!

#### Step 5: Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": 7,
    "name": "Alice Johnson",
    "email": "alice@example.com"
}
```

**Security Note:** Password is NOT returned in response (marked `write_only=True`)

---

### Example: Login Flow with JWT

#### Step 1: Client Login Request

```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "alice@example.com",
    "password": "securePassword123"
}
```

#### Step 2: Custom JWT Serializer

```python
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Map email → username (since we store email as username)
        email = attrs.get("email")
        password = attrs.get("password")
        return super().validate({"username": email, "password": password})
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to token
        token["email"] = user.email
        token["name"] = user.first_name
        return token
```

#### Step 3: Authentication Check

1. Fetch user from database: `User.objects.get(username='alice@example.com')`
2. Verify password: `user.check_password('securePassword123')`
3. If valid → generate JWT tokens
4. If invalid → return 401 error

#### Step 4: Token Generation

**Access Token Payload:**
```json
{
    "token_type": "access",
    "exp": 1707736200,  // Expires in 60 minutes
    "user_id": 7,
    "email": "alice@example.com",
    "name": "Alice Johnson"
}
```

**Refresh Token Payload:**
```json
{
    "token_type": "refresh",
    "exp": 1707822600,  // Expires in 1 day
    "user_id": 7
}
```

Both tokens are cryptographically signed with `SECRET_KEY`.

#### Step 5: Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA3NzM2MjAwLCJ1c2VyX2lkIjo3LCJlbWFpbCI6ImFsaWNlQGV4YW1wbGUuY29tIiwibmFtZSI6IkFsaWNlIEpvaG5zb24ifQ.xyz...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNzgyMjYwMCwidXNlcl9pZCI6N30.abc..."
}
```

#### Step 6: Using Access Token

Client stores tokens and includes in future requests:

```http
GET /api/patients/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Server validates token:
1. Verify signature (using SECRET_KEY)
2. Check expiration
3. Extract user_id
4. Attach user to request object

---

## ⚙️ Configuration & Settings

### Settings File Deep Dive (`healthcare_simple/settings.py`)

#### 1. Base Configuration

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```
- **Purpose:** Root directory of project
- **Usage:** Reference files relative to project root
- **Example:** `BASE_DIR / "uploads"` → `/path/to/project/uploads`

```python
load_dotenv(BASE_DIR / ".env")
```
- **Purpose:** Load environment variables from `.env` file
- **When:** Before accessing `os.getenv()`
- **Why:** Keep secrets out of code

#### 2. Security Settings

```python
SECRET_KEY = os.getenv("SECRET_KEY")
```
- **Purpose:** Cryptographic signing key
- **Used for:**
  - Session cookies
  - Password reset tokens
  - JWT token signing
  - CSRF tokens
- **Security:** Must be random, long (50+ chars), kept secret
- **Generation:** `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

```python
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")
```
- **Purpose:** Enable/disable debug mode
- **When True:**
  - Shows detailed error pages
  - Reloads code automatically
  - Slower performance
- **When False:**
  - Production mode
  - Generic error pages
  - Better performance
- **⚠️ Warning:** NEVER set DEBUG=True in production (security risk)

```python
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
```
- **Purpose:** Which domains can access this site
- **Example:** `["example.com", "www.example.com", "api.example.com"]`
- **Security:** Prevents HTTP Host header attacks
- **Development:** `["localhost", "127.0.0.1"]`

#### 3. Installed Apps

```python
INSTALLED_APPS = [
    "django.contrib.admin",           # Admin panel
    "django.contrib.auth",            # User authentication
    "django.contrib.contenttypes",    # Content type system
    "django.contrib.sessions",        # Session framework
    "django.contrib.messages",        # Messaging framework
    "django.contrib.staticfiles",     # Static file serving
    
    "rest_framework",                 # DRF for API
    "rest_framework_simplejwt",       # JWT authentication
    
    "api",                            # Our app
]
```

**Each app provides:**

- **django.contrib.admin**
  - Web-based admin interface
  - CRUD operations on models
  - Access at `/admin/`

- **django.contrib.auth**
  - User model
  - Authentication backends
  - Password hashing
  - Permissions system

- **django.contrib.contenttypes**
  - Track all models in project
  - Generic relations
  - Required by many apps

- **django.contrib.sessions**
  - Session management
  - Not used with JWT, but required by admin

- **django.contrib.messages**
  - Flash messages (success, error, etc.)
  - Used by admin panel

- **django.contrib.staticfiles**
  - Collect and serve static files (CSS, JS, images)
  - Development server serves automatically

- **rest_framework**
  - API views, serializers, routers
  - Browsable API interface
  - Authentication, permissions

- **rest_framework_simplejwt**
  - JWT token generation
  - Token verification
  - Token refresh mechanism

- **api**
  - Our custom application
  - Contains models, views, serializers

#### 4. Middleware

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",           # Security headers
    "django.contrib.sessions.middleware.SessionMiddleware",    # Session handling
    "django.middleware.common.CommonMiddleware",               # Common operations
    "django.middleware.csrf.CsrfViewMiddleware",              # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware", # Attach user to request
    "django.contrib.messages.middleware.MessageMiddleware",    # Flash messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Clickjacking protection
]
```

**Middleware = Layers that process every request/response**

**Order matters!** Requests flow top-to-bottom, responses bottom-to-top.

**What each does:**

1. **SecurityMiddleware**
   - Sets security headers (HSTS, X-Content-Type-Options)
   - Enforces HTTPS in production

2. **SessionMiddleware**
   - Manages session data
   - Stores session ID in cookie

3. **CommonMiddleware**
   - URL normalization (trailing slash)
   - ETags for caching
   - Content-Length header

4. **CsrfViewMiddleware**
   - Protects against Cross-Site Request Forgery
   - Checks CSRF token on POST/PUT/DELETE
   - **Note:** DRF uses own CSRF for browsable API

5. **AuthenticationMiddleware**
   - Adds `request.user` (current user)
   - If not logged in → `AnonymousUser`

6. **MessageMiddleware**
   - Enables flash messages
   - Used by admin panel

7. **XFrameOptionsMiddleware**
   - Prevents site from being embedded in iframe
   - Protects against clickjacking attacks

#### 5. Database Configuration

```python
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL is not set...")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,  # Connection pooling: keep connections for 10 minutes
    )
}
```

**Database URL Format:**
```
postgresql://username:password@host:port/database_name?sslmode=require
```

**Connection Pooling (`conn_max_age=600`):**
- Reuses database connections instead of creating new ones
- Improves performance
- 600 seconds = 10 minutes

**Example URLs:**
```
# PostgreSQL
postgresql://myuser:mypass@localhost:5432/healthcaredb

# PostgreSQL with SSL (production)
postgresql://user:pass@db.example.com:5432/prod?sslmode=require

# SQLite (development only)
sqlite:///db.sqlite3
```

#### 6. Password Validation

```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
```

**Validators enforce password strength:**

1. **UserAttributeSimilarityValidator**
   - Password can't be too similar to username/email/name
   - Prevents: username="john" password="john123"

2. **MinimumLengthValidator**
   - Password must be at least 8 characters
   - Default: 8 (can be configured)

3. **CommonPasswordValidator**
   - Checks against list of 20,000+ common passwords
   - Prevents: "password", "123456", "qwerty"

4. **NumericPasswordValidator**
   - Password can't be entirely numeric
   - Prevents: "12345678"

#### 7. Internationalization

```python
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True   # Internationalization (translations)
USE_TZ = True     # Use timezone-aware datetimes
```

- **LANGUAGE_CODE:** Default language for site
- **TIME_ZONE:** Timezone for storing dates (always use UTC in DB)
- **USE_TZ:** All datetimes stored with timezone info

#### 8. Static Files

```python
STATIC_URL = "static/"
```

- **Purpose:** URL prefix for static files (CSS, JS, images)
- **Development:** Django serves automatically
- **Production:** Must collect files: `python manage.py collectstatic`

#### 9. REST Framework Configuration

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
```

**Default Authentication:**
- All API requests authenticated via JWT
- Checks `Authorization: Bearer <token>` header
- Can be overridden per-view

**Default Permissions:**
- All endpoints require authentication by default
- Can be overridden with `permission_classes = [AllowAny]`

#### 10. JWT Configuration

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
```

**Access Token:**
- Short-lived (60 minutes)
- Used for API requests
- When expired → use refresh token

**Refresh Token:**
- Long-lived (1 day)
- Used to get new access token
- When expired → must login again

**Why two tokens?**
- Security: If access token stolen, only valid 60 minutes
- Convenience: Don't need to login every hour

---

## 🔐 Authentication & Security

### How JWT Authentication Works

#### 1. Registration
```
Client → POST /api/auth/register/
Server → Creates user, hashes password
Server → Returns user info (no tokens yet)
```

#### 2. Login
```
Client → POST /api/auth/login/ {email, password}
Server → Verifies credentials
Server → Generates access + refresh tokens
Server → Returns both tokens
Client → Stores tokens (localStorage or secure cookie)
```

#### 3. Authenticated Request
```
Client → GET /api/patients/
         Authorization: Bearer <access_token>
Server → Validates token signature
Server → Checks expiration
Server → Extracts user_id from token
Server → Attaches user to request
Server → Processes request
Server → Returns data
```

#### 4. Token Refresh
```
Client → POST /api/auth/token/refresh/ {refresh}
Server → Validates refresh token
Server → Generates new access token
Server → Returns new access token
Client → Updates stored access token
```

### Security Features

#### 1. Password Hashing
```python
# Never stored in plain text
User.objects.create_user(password="securePass123")
# Stored as: pbkdf2_sha256$260000$...
```

- Algorithm: PBKDF2 with SHA256
- 260,000 iterations (slow = more secure)
- Unique salt per password

#### 2. CSRF Protection
- Enabled for all state-changing requests (POST, PUT, DELETE)
- Not needed for JWT (stateless)
- Still active for admin panel

#### 3. SQL Injection Prevention
```python
# Django ORM automatically escapes queries
Patient.objects.filter(name=user_input)  # Safe
# Generated SQL uses parameterized queries
```

#### 4. XSS Protection
- All data escaped in templates
- API returns JSON (client responsible for sanitization)

#### 5. Data Access Control
```python
def get_queryset(self):
    # Users only see their own patients
    return Patient.objects.filter(owner=self.request.user)
```

- Row-level permissions
- Prevents accessing other users' data

---

## 📊 Database Schema Visual

### Full Schema with Constraints

```sql
-- Users Table (Django built-in)
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    is_active BOOLEAN DEFAULT true,
    date_joined TIMESTAMP NOT NULL
);

-- Patients Table
CREATE TABLE api_patient (
    id BIGSERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0),
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    address TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
CREATE INDEX api_patient_owner_id ON api_patient(owner_id);

-- Doctors Table
CREATE TABLE api_doctor (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    specialization VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Patient-Doctor Mappings
CREATE TABLE api_patientdoctormapping (
    id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES api_patient(id) ON DELETE PROTECT,
    doctor_id BIGINT NOT NULL REFERENCES api_doctor(id) ON DELETE PROTECT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT uniq_patient_doctor UNIQUE (patient_id, doctor_id)
);
CREATE INDEX api_patientdoctormapping_patient_id ON api_patientdoctormapping(patient_id);
CREATE INDEX api_patientdoctormapping_doctor_id ON api_patientdoctormapping(doctor_id);
```

---

## 🚀 Getting Started Guide

### 1. Installation

```bash
# Clone or download project
cd healthcare_backend_simple

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (use your favorite editor)
# Set SECRET_KEY and DATABASE_URL
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### 4. Run Server

```bash
# Development server
python manage.py runserver

# Server runs at: http://localhost:8000/
```

### 5. Test API

```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"securePass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"securePass123"}'

# Use access token in future requests
curl http://localhost:8000/api/patients/ \
  -H "Authorization: Bearer <your_access_token>"
```

---

## 📝 Summary

### What We Built
A complete healthcare management system with:
- User registration and JWT authentication
- Patient management (CRUD operations)
- Doctor management (CRUD operations)
- Patient-doctor relationship mapping
- Role-based access control
- Admin panel for management

### Key Technologies
- **Django:** Web framework, ORM, admin panel
- **Django REST Framework:** API views, serializers, permissions
- **JWT:** Stateless authentication
- **PostgreSQL:** Production database
- **Python-dotenv:** Environment configuration

### Architecture Patterns
- **MVT (Model-View-Template):** Django's pattern
  - Model: Data structure (models.py)
  - View: Business logic (views.py)
  - Template: Not used (API returns JSON)
- **RESTful API:** Standard HTTP methods, resource-based URLs
- **Repository Pattern:** Models abstract database access
- **Serializer Pattern:** Convert between formats, validate data

### Best Practices Implemented
✅ Environment variables for secrets  
✅ Password hashing (never plain text)  
✅ JWT for stateless authentication  
✅ Row-level permissions (users see only their data)  
✅ Database constraints (unique, foreign keys, protect)  
✅ Validation at multiple layers (serializer, model, database)  
✅ Automatic timestamps (created_at, updated_at)  
✅ Admin panel for management  
✅ Migration system for database changes  

---

## 🎓 Concepts for Beginners

### What is an API?
An API (Application Programming Interface) lets different programs talk to each other. Our API lets mobile apps, websites, or other services interact with our healthcare system.

### What is REST?
REST (Representational State Transfer) is a way to design APIs where:
- Each URL represents a "resource" (patient, doctor)
- HTTP methods indicate actions (GET = read, POST = create, etc.)
- Data exchanged in JSON format

### What is JSON?
JavaScript Object Notation - a way to structure data:
```json
{
    "name": "John Doe",
    "age": 45,
    "patients": [1, 2, 3]
}
```

### What is a Database?
Organized storage for data. Like an Excel spreadsheet with:
- Tables (sheets)
- Rows (records)
- Columns (fields)
- Relationships between tables

### What is Authentication?
Proving who you are. Like showing ID at airport.
- Registration: Create account
- Login: Prove identity
- Token: "Ticket" proving you logged in

### What is Authorization?
What you're allowed to do. Like different access levels:
- User can see own patients only
- Admin can see all patients

---

## 📚 Further Learning

### To Understand Django Better:
1. Official Django Tutorial: https://docs.djangoproject.com/
2. Django for Beginners book
3. Two Scoops of Django (best practices)

### To Understand REST APIs:
1. RESTful API Design course
2. HTTP protocol basics
3. Postman (API testing tool)

### To Understand Databases:
1. SQL basics course
2. Database normalization
3. PostgreSQL documentation

---

**End of Documentation**

This project demonstrates a complete, production-ready API architecture. Each component serves a specific purpose, and together they create a secure, scalable healthcare management system.

