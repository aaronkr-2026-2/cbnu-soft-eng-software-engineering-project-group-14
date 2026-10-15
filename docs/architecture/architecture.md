## **System Architecture Diagram -** 

┌──────────────────────────────────────────────────────────────┐
 │                      PRESENTATION LAYER                      │
 │          HTML5 / CSS3 (Templates rendered via Jinja2)        │
 │  - Admin Dashboard (`admin.html`)                            │
 │  - Employee Portal & Login Interface                         │
 └──────────────────────────────┬───────────────────────────────┘
                                │ HTTP Requests (GET / POST) & Form Data
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │                      APPLICATION LAYER                       │
 │            FastAPI Framework Controller (`app.py`)           │
 │  - Route Endpoints (`/`, `/login`, `/admin/dashboard`)       │
 │  - Session Control & Role-Based Access Routing               │
 └──────────────────────────────┬───────────────────────────────┘
                                │ Python Function Calls & PyMongo Queries
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │                    BUSINESS LOGIC LAYER                      │
 │            Database Services & Helpers (`database.py`)       │
 │  - Authentication Engine (`verify_login`, SHA-256 Hashing)   │
 │  - Joining-Date Password Validation Rule (`YYYY-MM-DD`)      │
 │  - Payroll Multiplier Engine (Attendance × Daily Rate)       │
 │  - Leave Management Controller (Approve/Reject Logic)        │
 └──────────────────────────────┬───────────────────────────────┘
                                │ MongoDB Driver Protocol (BSON / TCP)
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │                      DATA STORAGE LAYER                      │
 │                 MongoDB Database (`hrms_db`)                 │
 │  - `employees` collection (User profiles, roles, passwords)  │
 │  - `attendance` collection (Clock-in / attendance records)   │
 │  - `leaves` collection (Leave requests & reason messages)    │
 │  - `payroll` collection (Computed monthly financial outputs) │
 └──────────────────────────────────────────────────────────────┘

## **Detailed Layer Breakdown -**


### **1. Presentation Layer (Frontend)**
**Technology:** Jinja2 HTML templates (templates/admin.html) and inline responsive CSS.

**Function:** Provides the user interface for both administrators and employees. It renders dynamic forms for employee registration, attendance-based payroll calculation fields, and real-time interactive leave approval tables.

### **2. Application Layer (Controller)**
**Technology:** FastAPI (app.py).

**Function:** Handles all incoming HTTP traffic. It matches URL routes to Python functions, extracts form inputs using FastAPI's Form dependencies, evaluates user permissions (admin vs employee), and routes users accordingly (e.g., sending authorized admins to /admin/dashboard).

### **3. Business Logic Layer (Services)**
**Technology:** Python scripts (database.py).

**Function:** Encapsulates the core rules of your system:

**Authentication:** Verifies credentials against MongoDB by comparing SHA-256 hashed passwords or matching the initial plain-text joining_date (YYYY-MM-DD).

**Payroll Calculation:** Dynamically queries the attendance collection, aggregates total presence counts, and multiplies them by the administrator's custom daily wage rate.

**Leave Handling:** Manages requests by fetching pending status messages and updating document flags instantly upon admin action.

### **4. Data Storage Layer (Persistence)**
**Technology:** MongoDB (hrms_db).

**Function:** Acts as the document store holding all application state across four specialized collections:

**employees:** Stores user credentials, names, departments, base salaries, and roles (admin/employee).

**attendance:** Records day-to-day clock-in and presence entries.

**leaves:** Captures employee leave applications along with reason messages and current request statuses.

**payroll:** Persists finalized payroll calculations, month-year tags, and total calculated wages.