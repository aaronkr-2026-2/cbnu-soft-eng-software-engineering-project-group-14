# Sprint 01: Core Authentication & Role-Based Routing

## 1. Sprint Goal
Deliver a secure MongoDB-backed login interface and role-based routing system so employees can log in using their initial joining date and administrators can access management panels.

---

## 2. Product Backlog Items (GitHub Issues & Labels)

| ID | Title | Type | Priority | Status |
|----||------|----------|--------|
| #1 | Setup MongoDB database collections (`employees`, `attendance`, `leaves`) | Engineering | High | `Doing` |
| #2 | Design and style FastAPI login HTML UI | User-facing | High | `Doing` |
| #3 | Implement `verify_login` backend logic with joining date fallback | Engineering | High | `Doing` |
| #4 | Test role-based redirection for Admin vs Employee | Test | Medium | `Planning` |
| #5 | Write unit tests for password hashing and validation | Bug/Test | Low | `Thinking` |

---

## 3. Refined Top Items & Acceptance Checks

### Issue #2: Design and style FastAPI login HTML UI
* **Acceptance Checks:**
  1. Renders a responsive card layout with email and password fields.
  2. Submits via POST request to `/login` endpoint.
  3. Displays error messages gracefully on invalid credentials.
* **Dependencies:** None
* **Estimate:** 3 Story Points

### Issue #3: Implement `verify_login` backend logic with joining date fallback
* **Acceptance Checks:**
  1. Verifies input email against the MongoDB collection.
  2. Compares password hash or falls back to matching the `joining_date` string.
  3. Returns a dictionary containing role (`admin` or `employee`) upon success.
* **Dependencies:** Issue #1
* **Estimate:** 5 Story Points

---

## 4. Task Breakdown & Check-ins
* **Tasks Assigned To:** Self (Solo Developer)
* **Likely Blockers:** Handling `python-multipart` form parsing dependencies in FastAPI.
* **Async Check-in Format:** Brief status updates posted as comments on GitHub Issues twice during the week.

---

## 5. Definition of Done (DoD) Checklist
- [ ] Code reviewed and tested locally.
- [ ] Automated or manual verification test passes (successful login & redirection).
- [ ] Changes committed and merged into `main` via a Pull Request referencing the GitHub Issue.
- [ ] User-visible acceptance check verified via browser (`http://127.0.0.1:8000`).