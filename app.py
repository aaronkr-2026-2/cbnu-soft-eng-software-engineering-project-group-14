from database import add_employee, db, verify_login
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()


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
def login_user(email: str = Form(...), password: str = Form(...)):
  result = verify_login(email, password)

  if result["status"] == "success":
    role = result["role"]
    name = result["name"]

    if role == "admin":
      return f"""
                <div style="font-family:Arial; padding: 40px; text-align: center;">
                    <h1 style="color: #16a34a;">🛡️ Admin Dashboard</h1>
                    <p>Welcome back, <b>{name}</b>!</p>
                    <hr style="max-width: 500px; margin: 20px auto;">
                    <h3>Manage System</h3>
                    <a href="/add-employee" style="padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px;">Add New Employee</a>
                </div>
            """
    else:
      return f"""
                <div style="font-family:Arial; padding: 40px; text-align: center;">
                    <h1 style="color: #2563eb;">👤 Employee Portal</h1>
                    <p>Welcome back, <b>{name}</b>!</p>
                    <hr style="max-width: 500px; margin: 20px auto;">
                    <p>Here you can view your attendance and request leaves.</p>
                </div>
            """
  else:
    return """
        <div style="font-family:Arial; padding: 40px; text-align: center;">
            <h2 style="color: #dc2626;">❌ Invalid Email or Password</h2>
            <a href="/" style="color: #2563eb; text-decoration: none;">← Try Again</a>
        </div>
        """


# 3. Admin View: Add Employee Page
@app.get("/add-employee", response_class=HTMLResponse)
def add_employee_form():
  return """
    <html>
        <head>
            <title>Add Employee</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 400px; }
                h2 { text-align: center; color: #333; }
                input, select { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
                button { width: 100%; padding: 12px; background-color: #16a34a; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; }
                button:hover { background-color: #15803d; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Add New Employee</h2>
                <form action="/add-employee" method="POST">
                    <input type="text" name="first_name" placeholder="First Name" required>
                    <input type="text" name="last_name" placeholder="Last Name" required>
                    <input type="email" name="email" placeholder="Email Address" required>
                    <input type="text" name="department" placeholder="Department" required>
                    <input type="number" name="salary" placeholder="Base Salary ($)" required>
                    <button type="submit">Save Employee</button>
                </form>
            </div>
        </body>
    </html>
    """


# 4. Handle Adding Employee to MongoDB
@app.post("/add-employee", response_class=HTMLResponse)
def handle_add_employee(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    department: str = Form(...),
    salary: float = Form(...),
):
  add_employee(first_name, last_name, email, department, salary)
  return """
    <div style="font-family:Arial; padding: 40px; text-align: center;">
        <h2 style="color: #16a34a;">✅ Employee Added Successfully!</h2>
        <a href="/add-employee" style="color: #2563eb; text-decoration: none; margin-right: 15px;">Add Another</a>
    </div>
    """