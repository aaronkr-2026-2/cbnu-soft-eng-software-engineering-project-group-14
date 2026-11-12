# Current MVP Features List
1. FastAPI web framework server (`app.py`) connected to MongoDB (`database.py`).
2. HTML/CSS login interface supporting email input and password entry.
3. Joining date fallback authentication rule (`YYYY-MM-DD` plain text matching initial password).
4. Role-based redirection routing users dynamically to Admin or Employee dashboards based on database roles.
5. Secure password hashing using SHA-256 for standard user accounts.