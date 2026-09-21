# AI-Based Secure Data Transfer Between Organizations

This project separates the frontend and backend:

- `frontend/`: HTML, CSS, and JavaScript user interface
- `backend/`: Flask API, SQLite database, AES-GCM encryption, and basic AI monitoring hook

## Run

1. Open a terminal in `backend/`.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the backend:

```bash
python app.py
```

5. Open the frontend by visiting:

```text
http://127.0.0.1:5000
```

The backend serves the frontend files and exposes API routes.

Demo credentials:

- Username: `admin`
- Password: `admin123`

This is an educational prototype. Do not use it for real confidential data without professional security review, secure key management, HTTPS, production authentication, and proper deployment hardening.
