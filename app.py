import os
from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, Form, Request, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import (
    add_employee,
    calculate_salary_by_attendance,
    db,
    get_all_employees,
    get_pending_leaves,
    update_leave_status,
    verify_login,
    mark_attendance,
    submit_leave_request,
)

app = FastAPI()

# Required so request.session works properly!
app.add_middleware(SessionMiddleware, secret_key="your-super-secret-key-change-me")

# Directory to store uploaded PDFs
UPLOAD_DIR = "static/notices"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files so /static/notices/ links work properly
app.mount("/static", StaticFiles(directory="static"), name="static")


# 1. Home / Login Page Route
@app.get("/", response_class=HTMLResponse)
def login_page():
    return """
    <html>
        <head>
            <title>HRMS Login</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 350px; }
                h2 { text-align: center; color: #333; margin-bottom: 25px; }
                input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
                button { width: 100%; padding: 12px; background-color: #4f46e5; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; }
                button:hover { background-color: #4338ca; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>HRMS Login</h2>
                <form action="/login" method="POST">
                    <input type="email" name="email" placeholder="Email Address" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Sign In</button>
                </form>
            </div>
        </body>
    </html>
    """


# 2. Handle Login Submission & Routing
@app.post("/login", response_class=HTMLResponse)
def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    result = verify_login(email, password)

    if result["status"] == "success":
        role = result["role"]
        name = result["name"]

        # Save user session info
        request.session["user"] = {
            "email": email,
            "name": name,
            "role": role,
            "first_name": name.split()[0] if name else "User",
            "last_name": name.split()[-1] if len(name.split()) > 1 else ""
        }

        if role == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        else:
            return RedirectResponse(url="/employee/dashboard", status_code=303)
    else:
        return """
        <div style="font-family:Arial; padding: 40px; text-align: center;">
            <h2 style="color: #dc2626;">❌ Invalid Email or Password</h2>
            <a href="/" style="color: #2563eb; text-decoration: none;">← Try Again</a>
        </div>
        """


# 3. Logout Route
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# ==========================================
# 4. ADMIN DASHBOARD
# ==========================================
@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard():
    employees = get_all_employees()
    pending_leaves = get_pending_leaves()

    employee_options = "".join(
        [
            f'<option value="{emp["email"]}">{emp["first_name"]} {emp["last_name"]} ({emp["email"]})</option>'
            for emp in employees
        ]
    )

    leave_rows = ""
    if pending_leaves:
        for leave in pending_leaves:
            leave_rows += f"""
                <tr>
                    <td>{leave.get("email")}</td>
                    <td><strong>{leave.get("reason")}</strong></td>
                    <td>{leave.get("start_date")} to {leave.get("end_date")}</td>
                    <td>
                        <form action="/admin/leave-action" method="POST" style="display:inline;">
                            <input type="hidden" name="leave_id" value="{leave.get("_id")}">
                            <input type="hidden" name="action" value="Approved">
                            <button type="submit" style="background: #16a34a; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 3px;">Approve</button>
                        </form>
                        <form action="/admin/leave-action" method="POST" style="display:inline;">
                            <input type="hidden" name="leave_id" value="{leave.get("_id")}">
                            <input type="hidden" name="action" value="Rejected">
                            <button type="submit" style="background: #dc2626; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 3px;">Reject</button>
                        </form>
                    </td>
                </tr>
            """
    else:
        leave_rows = '<tr><td colspan="4" style="text-align: center; color: #777;">No pending leave requests at the moment.</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>HRMS Admin Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 30px; background: #f4f7f6; }}
            .section {{ background: white; padding: 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            h1 {{ color: #1e293b; }}
            h2 {{ color: #0f172a; border-bottom: 2px solid #2563eb; padding-bottom: 8px; margin-top: 0; }}
            form div {{ margin-bottom: 12px; }}
            label {{ display: block; font-weight: bold; margin-bottom: 5px; color: #475569; }}
            input, select {{ width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 5px; box-sizing: border-box; }}
            button.btn {{ background: #2563eb; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 5px; font-weight: bold; }}
            button.btn:hover {{ background: #1d4ed8; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 10px; text-align: left; }}
            th {{ background-color: #f8fafc; color: #334155; }}
        </style>
    </head>
    <body>

        <h1>🛡️ Admin Control Panel</h1>
        <p><a href="/logout" style="color: #dc2626; text-decoration: none; font-weight: bold;">← Logout</a></p>

        <!-- SECTION 1: Add New Employee Form -->
        <div class="section">
            <h2>1. Add New Employee</h2>
            <form action="/admin/add-employee" method="POST">
                <div><label>First Name:</label><input type="text" name="first_name" required></div>
                <div><label>Last Name:</label><input type="text" name="last_name" required></div>
                <div><label>Email Address:</label><input type="email" name="email" required></div>
                <div><label>Department:</label><input type="text" name="department" required></div>
                <div><label>Base Salary ($):</label><input type="number" name="salary" required></div>
                <button type="submit" class="btn">Register Employee</button>
            </form>
        </div>

        <!-- SECTION 2: Attendance & Salary Calculation -->
        <div class="section">
            <h2>2. Attendance & Salary Calculation</h2>
            <form action="/admin/calculate-salary" method="POST">
                <div>
                    <label>Select Employee:</label>
                    <select name="email" required>{employee_options}</select>
                </div>
                <div><label>Daily Salary Rate ($):</label><input type="number" step="0.01" name="daily_rate" required placeholder="e.g., 50.00"></div>
                <div><label>Month & Year:</label><input type="text" name="month_year" value="2026-10" required></div>
                <button type="submit" class="btn">Calculate Total Salary</button>
            </form>
        </div>

        <!-- SECTION 3: Leave Requests Management -->
        <div class="section">
            <h2>3. Pending Leave Requests</h2>
            <table>
                <thead>
                    <tr><th>Employee Email</th><th>Reason</th><th>Dates</th><th>Action</th></tr>
                </thead>
                <tbody>{leave_rows}</tbody>
            </table>
        </div>

        <!-- SECTION 4: Upload PDF Notices -->
        <div class="section">
            <h2>4. Upload Notice (PDF)</h2>
            <form action="/admin/upload-notice" method="POST" enctype="multipart/form-data">
                <div><label>Notice Title:</label><input type="text" name="title" required placeholder="e.g. Public Holiday Notice"></div>
                <div><label>PDF File:</label><input type="file" name="file" accept="application/pdf" required></div>
                <button type="submit" class="btn">Upload Notice PDF</button>
            </form>
        </div>

    </body>
    </html>
    """


# ==========================================
# 5. ADMIN ACTIONS & HANDLERS
# ==========================================
@app.post("/admin/add-employee", response_class=HTMLResponse)
def handle_add_employee(first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), department: str = Form(...), salary: float = Form(...)):
    add_employee(first_name, last_name, email, department, salary)
    return """
        <div style="font-family:Arial; padding: 40px; text-align: center;">
            <h2 style="color: #16a34a;">✅ Employee Added Successfully!</h2>
            <a href="/admin/dashboard" style="color: #2563eb; text-decoration: none;">← Back to Admin Dashboard</a>
        </div>
    """


@app.post("/admin/calculate-salary", response_class=HTMLResponse)
def handle_calculate_salary(email: str = Form(...), daily_rate: float = Form(...), month_year: str = Form(...)):
    total_salary = calculate_salary_by_attendance(email, daily_rate, month_year)
    return f"""
        <div style="font-family:Arial; padding: 40px; text-align: center;">
            <h2 style="color: #16a34a;">💰 Salary Calculated Successfully!</h2>
            <p>Total Net Salary Computed: <b>${total_salary}</b></p>
            <a href="/admin/dashboard" style="color: #2563eb; text-decoration: none;">← Back to Admin Dashboard</a>
        </div>
    """


@app.post("/admin/leave-action", response_class=HTMLResponse)
def handle_leave_action(leave_id: str = Form(...), action: str = Form(...)):
    db.leaves.update_one({"_id": ObjectId(leave_id)}, {"$set": {"status": action}})
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@app.post("/admin/upload-notice")
async def upload_notice(request: Request, title: str = Form(...), file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    db.notices.insert_one({
        "title": title,
        "filename": file.filename,
        "file_path": f"/static/notices/{file.filename}",
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@app.get("/notices/download/{filename}")
async def download_notice(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=filename)
    raise HTTPException(status_code=404, detail="File not found")


# ==========================================
# 6. EMPLOYEE PORTAL & ACTIONS
# ==========================================
@app.get("/employee/dashboard", response_class=HTMLResponse)
async def employee_dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    notices = list(db.notices.find().sort("uploaded_at", -1))
    
    notice_rows = ""
    if notices:
        for notice in notices:
            notice_rows += f"""
                <tr>
                    <td>{notice.get("title")}</td>
                    <td>{notice.get("uploaded_at")}</td>
                    <td><a href="{notice.get("file_path")}" target="_blank" style="background: #2563eb; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Download PDF</a></td>
                </tr>
            """
    else:
        notice_rows = '<tr><td colspan="3" style="text-align: center; color: #777;">No notices available right now.</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Employee Portal - HRMS</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 30px; background: #f4f7f6; }}
            .container {{ max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            h2 {{ color: #0f172a; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }}
            .section {{ margin-bottom: 30px; }}
            button, .btn {{ background: #2563eb; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 5px; font-weight: bold; }}
            button:hover, .btn:hover {{ background: #1d4ed8; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 10px; text-align: left; }}
            th {{ background-color: #f8fafc; color: #334155; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 5px; box-sizing: border-box; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/logout" style="float: right; color: #dc2626; text-decoration: none; font-weight: bold;">Logout</a>
            <h2>👤 Employee Portal</h2>
            <p>Welcome back, <b>{user.get("name")}</b>!</p>
            <hr style="margin: 20px 0;">

            <!-- 1. Attendance Section -->
            <div class="section">
                <h3>Time & Attendance</h3>
                <form action="/employee/clock-in" method="POST">
                    <button type="submit">Clock In Today</button>
                </form>
            </div>

            <!-- 2. Leave Request Section -->
            <div class="section">
                <h3>Request Leave</h3>
                <form action="/employee/request-leave" method="POST">
                    <label>Start Date:</label>
                    <input type="date" name="start_date" required>
                    <label>End Date:</label>
                    <input type="date" name="end_date" required>
                    <label>Reason / Message:</label>
                    <input type="text" name="reason" required placeholder="e.g. Medical Leave">
                    <button type="submit">Submit Leave Request</button>
                </form>
            </div>

            <!-- 3. Notice Board Section -->
            <div class="section">
                <h3>Notice Board & Announcements</h3>
                <table>
                    <thead>
                        <tr><th>Title</th><th>Date Posted</th><th>Action</th></tr>
                    </thead>
                    <tbody>
                        {notice_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """


@app.post("/employee/clock-in")
async def employee_clock_in(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=303)
    mark_attendance(db, user["email"])
    return RedirectResponse(url="/employee/dashboard", status_code=303)


@app.post("/employee/request-leave")
async def request_leave(request: Request, start_date: str = Form(...), end_date: str = Form(...), reason: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=303)
    submit_leave_request(db, user["email"], start_date, end_date, reason)
    return RedirectResponse(url="/employee/dashboard", status_code=303)