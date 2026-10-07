**Build: Travel Price Tracker API.**

**Stack: FastAPI, PostgreSQL, Redis, Celery, Docker.**

**Core features:**

1. JWT auth with roles
2. Fetch flight/hotel prices via free APIs
3. Celery jobs poll hourly
4. Redis caches search results
5. Email alerts on price drops
6. Rate limiting, pagination
7. LLM itinerary endpoint

Install these first:

Python 3.12+: python --version
Docker Desktop: docker --version
Git plus GitHub account: git --version
VS Code
Node.js LTS: node --version
Angular CLI: npm install -g @angular/cli
Postman or Bruno for API testing
DBeaver (optional) to view database

Python libraries (installed later): FastAPI, Uvicorn, SQLAlchemy, Alembic, Celery, Redis client, Pytest, HTTPX.
# Travel Price Tracker API

A FastAPI backend for the Travel Price Tracker project. The project is being built to allow users to sign up, track flight/hotel routes, check prices periodically, receive alerts on price drops, and later view price history through an Angular dashboard.

## Current Progress

Today we completed the initial backend foundation and user authentication flow.

### Tech Stack

- Python 3.14.5
- FastAPI
- Uvicorn
- PostgreSQL 16
- Docker / Docker Compose
- SQLAlchemy
- Alembic
- Pydantic
- Passlib
- bcrypt 4.0.1
- python-jose
- JWT authentication

---

## 1. Project Structure

Current backend structure:

```text
price-tracker/
├── docker-compose.yml
└── backend/
    ├── .venv/
    ├── alembic/
    │   └── versions/
    ├── alembic.ini
    ├── auth.py
    ├── database.py
    ├── main.py
    ├── models.py
    ├── schemas.py
    └── test_db.py
```

---

## 2. Python Virtual Environment

The backend uses a virtual environment so project dependencies remain isolated.

Activate it from the backend directory:

```bash
cd C:\Users\vrushab\price-tracker\backend
.venv\Scripts\activate
```

The terminal should show:

```text
(.venv)
```

---

## 3. PostgreSQL and Redis with Docker

Docker Compose is used to run the project services.

Start the containers:

```bash
docker compose up -d
```

Check their status:

```bash
docker compose ps
```

Current services:

- PostgreSQL 16
- Redis 7

PostgreSQL is available on:

```text
localhost:5432
```

Redis is available on:

```text
localhost:6379
```

If Docker Desktop has been closed, the containers may be stopped. Start them again with:

```bash
docker compose up -d
```

---

## 4. PostgreSQL Database

The current PostgreSQL connection is:

```text
postgresql://tracker:tracker@localhost:5432/tracker
```

The database configuration is in `database.py`.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://tracker:tracker@localhost:5432/tracker"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 5. Testing the Database Connection

`test_db.py` contains:

```python
from database import engine

with engine.connect() as connection:
    print("Database connected successfully")
```

Run:

```bash
python test_db.py
```

Expected:

```text
Database connected successfully
```

---

## 6. SQLAlchemy User Model

The current `User` model contains:

- `id`
- `email`
- `password_hash`

`models.py`:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
```

---

## 7. Alembic Migrations

Alembic was initialized with:

```bash
alembic init alembic
```

This should only be done once.

The migration environment was configured to use:

```python
from database import Base
from models import User

target_metadata = Base.metadata
```

The first migration created the `users` table.

A later migration added `password_hash`.

Because an existing user already existed, adding the new non-null column initially caused an integrity error. The migration was adjusted so the existing data could be migrated successfully.

Run migrations with:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

---

## 8. User Schemas

`schemas.py` currently validates registration and login requests.

```python
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
```

### Password Validation

The password must currently be:

- At least 8 characters
- At most 72 characters

The 72-character limit is because bcrypt has a 72-byte password limitation.

---

## 9. Password Hashing

Passwords are never stored directly in the database.

`auth.py` uses Passlib with bcrypt:

```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
```

A password such as:

```text
root12345
```

is converted into a bcrypt hash before being stored.

The API response does not expose the password or password hash.

---

## 10. bcrypt Compatibility Issue

An issue occurred with the installed bcrypt version.

The error included:

```text
AttributeError: module 'bcrypt' has no attribute '__about__'
```

and eventually:

```text
ValueError: password cannot be longer than 72 bytes
```

The problem was a compatibility issue between the installed Passlib version and the newer bcrypt package.

It was fixed by installing bcrypt 4.0.1:

```bash
pip uninstall bcrypt -y
pip install bcrypt==4.0.1
```

Verify the installed version:

```bash
pip show bcrypt
```

Expected:

```text
Version: 4.0.1
```

After this, password hashing worked correctly.

---

## 11. FastAPI Application

`main.py` currently contains these endpoints:

```text
GET  /health
GET  /users
POST /users
POST /login
GET  /me
```

Run the application:

```bash
uvicorn main:app --reload
```

FastAPI runs at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

---

## 12. Health Check

Endpoint:

```text
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

This confirms that the FastAPI application is running.

---

## 13. Create User

Endpoint:

```text
POST /users
```

Request:

```json
{
  "email": "vrushabzaveri@gmail.com",
  "password": "root12345"
}
```

Successful response:

```json
{
  "id": 3,
  "email": "vrushabzaveri@gmail.com"
}
```

The password is not returned.

The password is hashed before being stored in PostgreSQL.

---

## 14. Get Users

Endpoint:

```text
GET /users
```

This returns registered users using `UserResponse`.

Passwords and password hashes are not returned by this endpoint.

---

## 15. Login

Endpoint:

```text
POST /login
```

Request:

```json
{
  "email": "vrushabzaveri@gmail.com",
  "password": "root12345"
}
```

The endpoint:

1. Finds the user by email.
2. Verifies the submitted password against the stored bcrypt hash.
3. Creates a JWT if the password is correct.
4. Returns the JWT access token.

Successful response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 16. JWT Authentication

JWT configuration currently uses:

```python
SECRET_KEY = "change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

The token contains the user's ID in the `sub` claim and expires after 60 minutes.

Example payload conceptually:

```json
{
  "sub": "3",
  "exp": "..."
}
```

The secret key is currently hard-coded for development only.

It should later be moved into an environment variable.

---

## 17. Current User Authentication

The project uses FastAPI's:

```python
OAuth2PasswordBearer
```

The authentication dependency extracts the JWT from:

```text
Authorization: Bearer <token>
```

`get_current_user()`:

1. Reads the JWT.
2. Validates the JWT signature.
3. Checks the expiration.
4. Reads the user ID from `sub`.
5. Finds the corresponding user in PostgreSQL.
6. Returns the authenticated `User`.

---

## 18. Protected `/me` Endpoint

Endpoint:

```text
GET /me
```

The endpoint requires a valid JWT:

```python
@app.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

Without authentication:

```json
{
  "detail": "Not authenticated"
}
```

With a valid JWT:

```json
{
  "id": 3,
  "email": "vrushabzaveri@gmail.com"
}
```

---

## 19. Testing Authentication in Swagger

Open:

```text
http://localhost:8000/docs
```

### Step 1

Use:

```text
POST /login
```

to obtain an access token.

### Step 2

Click **Authorize** in Swagger.

### Step 3

Enter the access token.

### Step 4

Call:

```text
GET /me
```

The API should identify the logged-in user.

---

## 20. Important Commands

### Start Docker services

```bash
docker compose up -d
```

### Check Docker services

```bash
docker compose ps
```

### Activate Python environment

```bash
cd C:\Users\vrushab\price-tracker\backend
.venv\Scripts\activate
```

### Start FastAPI

```bash
uvicorn main:app --reload
```

### Run database test

```bash
python test_db.py
```

### Run migrations

```bash
alembic upgrade head
```

### Check migration

```bash
alembic current
```

### Open PostgreSQL

```bash
docker exec -it price-tracker-db-1 psql -U tracker -d tracker
```

Inside PostgreSQL:

```sql
\dt
```

Check users:

```sql
SELECT id, email, password_hash FROM users;
```

Exit PostgreSQL:

```sql
\q
```

---

## 21. Current Backend Flow

The current authentication flow is:

```text
User
  │
  ▼
POST /users
  │
  ▼
Validate email/password
  │
  ▼
Hash password with bcrypt
  │
  ▼
Store user in PostgreSQL
```

Login:

```text
User
  │
  ▼
POST /login
  │
  ▼
Find user by email
  │
  ▼
Verify bcrypt password
  │
  ▼
Create JWT
  │
  ▼
Return access token
```

Authenticated request:

```text
Client
  │
  │ Authorization: Bearer <JWT>
  ▼
GET /me
  │
  ▼
Validate JWT
  │
  ▼
Find user
  │
  ▼
Return current user
```

---

## 22. Current Project Status

Completed:

- [x] Python environment
- [x] FastAPI application
- [x] Uvicorn development server
- [x] Docker Compose
- [x] PostgreSQL
- [x] Redis container
- [x] SQLAlchemy
- [x] Database connection
- [x] Alembic
- [x] Users table
- [x] User registration
- [x] Password hashing
- [x] Password verification
- [x] Login endpoint
- [x] JWT creation
- [x] JWT validation
- [x] Protected `/me` endpoint
- [x] Swagger API testing

---

## 23. Next Development Steps

Planned next steps:

1. Move JWT `SECRET_KEY` into `.env`.
2. Add a proper settings/configuration system.
3. Improve authentication and authorization.
4. Add flight/hotel tracking models.
5. Add tracked routes for users.
6. Add price history.
7. Add scheduled price checking with Celery.
8. Use Redis as the Celery broker.
9. Add price-drop alerts.
10. Add automated tests with Pytest and HTTPX.
11. Build the Angular dashboard.
12. Add charts for price history.
13. Connect the frontend to the FastAPI API.
14. Prepare the application for deployment.
