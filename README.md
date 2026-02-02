# Simple Password Manager

A basic web-based password manager built with FastAPI. This application allows users to register, log in, and securely manage their passwords. Passwords are encrypted using per-user keys and stored in JSON files. **Note: This is an educational project and not intended for production use due to security limitations (e.g., file-based storage, no HTTPS by default). Use at your own risk.**

## Features

- **User Authentication**: Register new users with username and password. Login to access personal password vault.
- **Password Management**:
  - Add new password records (title, login, password, URL, notes).
  - View, edit, and delete existing records.
  - Passwords are encrypted using Fernet (symmetric encryption) with user-specific keys.
- **Encryption/Decryption**: Handles encryption on save and decryption on view/edit.
- **Stats Endpoint**: Simple stats like total records per user.
- **HTML Interface**: Basic web pages for login, registration, password list, add/edit forms, using Jinja2 templates.
- **API Endpoints**: RESTful API for passwords (GET, POST, PUT, PATCH, DELETE) with authentication middleware.
- **Middleware**: Enforces authentication for protected routes.

## Project Structure

- **users.json**: Stores user data (usernames, hashed passwords, encrypted user keys).
- **password_records.json**: Stores encrypted password records.
- **passwords.py**: Router for password-related endpoints (CRUD operations, encryption/decryption).
- **database.py**: Helper functions for loading/saving JSON data.
- **main.py**: Main FastAPI application entry point, includes routers and basic routes.
- **auth.py**: Handles user registration, login, and authentication utilities.
- **models.py**: Pydantic models for users and password records.
- **middleware.py**: Authentication middleware to protect routes.
- **templates/**: Jinja2 HTML templates (e.g., login.html, passwords.html, add.html, edit.html, etc.).
- **static/**: Static files (CSS, JS if any).

## Technologies Used

- **Framework**: FastAPI (ASGI web framework for Python).
- **Authentication**: Passlib for password hashing (bcrypt), Cryptography (Fernet) for encryption.
- **Templating**: Jinja2 for HTML rendering.
- **Server**: Uvicorn (ASGI server).
- **Other Libraries**: Pydantic for data validation, Base64 for key handling.
- **Storage**: JSON files (simple, file-based "database" – not suitable for production).

## Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/Luxzxc/Password_manager_kursovaya.git
   cd Password_manager_kursovaya
   ```

2. **Set Up Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```
   pip install fastapi uvicorn cryptography passlib[bcrypt] jinja2
   ```

4. **Create Data Files** (if not present):
   - The app will create `users.json` and `password_records.json` in `venv/app/` if they don't exist, but you can initialize them as empty arrays `[]`.

## Usage

1. **Run the Server**:
   ```
   uvicorn main:app --reload
   ```
   The app will be available at `http://127.0.0.1:8000/`.

2. **Access the App**:
   - Open a browser and go to `http://127.0.0.1:8000/`.
   - Register a new user or log in with existing credentials.
   - After login, you'll be redirected to `/passwords` where you can manage records.
   - Use forms to add/edit records; passwords are encrypted automatically.

3. **API Usage** (for developers):
   - API docs available at `/docs` (Swagger UI).
   - Endpoints like `/passwords/` (GET all), `/passwords/{record_id}` (GET one), etc.
   - Authentication via `X-Username` cookie (set on login).

4. **Example Workflow**:
   - Register: Go to `/register`, submit username/password.
   - Login: Submit credentials at `/`.
   - Add Password: Go to `/passwords/add`, fill form.
   - View: Click on records in the list.
   - Edit/Delete: Use respective forms.

## Security Notes

- **Encryption**: Each user has a unique Fernet key. Passwords are encrypted before storage and decrypted only for viewing/editing.
- **Hashing**: User passwords are hashed with bcrypt.
- **Limitations**:
  - JSON file storage is not secure or scalable (no concurrency handling, easy to tamper).
  - No session management beyond cookies; no CSRF protection.
  - No HTTPS – deploy with SSL in production.
  - For real-world use, migrate to a proper database (e.g., PostgreSQL) and add more security features.

