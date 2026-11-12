# Feature vs. Story Gap Map

| User Story | Implemented Feature | Status |
|---|---|---|
| 1. Admin login | FastAPI login form + `verify_login` function | **Shipped** |
| 2. Joining date login fallback | Plain-text comparison against `joining_date` in Python | **Shipped** |
| 3. Default role protection | `role="employee"` assigned during `add_employee` | **Shipped** |
| 4. Dynamic role lookup | Fetching `"role"` field from MongoDB document | **Shipped** |
| 5. Profile viewing | Basic authentication route redirection | **Shipped** |
| 6. Password hashing | `hashlib.sha256` implementation | **Shipped** |
| 7. Employee creation | `add_employee` database handler | **Shipped** |
| 8. Login error handling | HTML form feedback responses | **Shipped** |