from datetime import datetime
from pymongo import MongoClient
import hashlib

# 1. Connect to MongoDB (local or Atlas URI)
# If running locally with default port, use "mongodb://localhost:27017/"
client = MongoClient("mongodb://localhost:27017/")

# 2. Create/Access the database
db = client["hrms_db"]


# --- Employee Operations ---
def add_employee(first_name, last_name, email, department, salary, role = "employee"):
  
  joining_date_str = datetime.now().strftime("%Y-%m-%d")

  initial_password_hash = hashlib.sha256(joining_date_str.encode()).hexdigest()
  employee_doc = {
      "first_name": first_name,
      "last_name": last_name,
      "email": email,
      "department": department,
      "base_salary": salary,
      "joining_date": joining_date_str,
      "password": initial_password_hash,
      "role":role,
      "status": "Active",
  }
  result = db.employees.insert_one(employee_doc)
  print(f"✅ Added employee with ID: {result.inserted_id}")


def get_all_employees():
  return list(db.employees.find({}, {"_id": 0}))  # Hide MongoDB's default _id


# --- Attendance Operations ---
def log_attendance(email, action):
  attendance_doc = {
      "email": email,
      "action": action,  # "Clock In" or "Clock Out"
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  }
  db.attendance.insert_one(attendance_doc)
  print(f"⏰ Recorded {action} for {email}")

  # ==========================================
# 3. LEAVE REQUEST OPERATIONS
# ==========================================
def apply_leave(email, leave_type, start_date, end_date, reason):
  leave_doc = {
      "email": email,
      "leave_type": leave_type,  # e.g., "Sick Leave", "Casual Leave"
      "start_date": start_date,
      "end_date": end_date,
      "reason": reason,
      "status": "Pending",  # Pending, Approved, Rejected
      "applied_on": datetime.now().strftime("%Y-%m-%d"),
  }
  result = db.leaves.insert_one(leave_doc)
  print(f"🏖️️ Leave request submitted for {email} (ID: {result.inserted_id})")


def update_leave_status(email, start_date, new_status):
  result = db.leaves.update_one(
      {"email": email, "start_date": start_date},
      {"$set": {"status": new_status}},
  )
  if result.modified_count > 0:
    print(f"📋 Leave status updated to '{new_status}' for {email}")
  else:
    print(f"⚠️ Leave request not found for {email} starting on {start_date}")


# ==========================================
# 4. PAYROLL & SALARY OPERATIONS
# ==========================================
def generate_payroll(email, month_year, bonus=0, deductions=0):
  employee = db.employees.find_one({"email": email})
  if not employee:
    print(f"❌ Error: Employee with email {email} not found.")
    return

  base_salary = employee["base_salary"]
  net_salary = base_salary + bonus - deductions

  payroll_doc = {
      "email": email,
      "month_year": month_year,  # e.g., "2026-10"
      "base_salary": base_salary,
      "bonus": bonus,
      "deductions": deductions,
      "net_salary": net_salary,
      "payment_status": "Generated",
      "generated_on": datetime.now().strftime("%Y-%m-%d"),
  }

  db.payroll.update_one(
      {"email": email, "month_year": month_year},
      {"$set": payroll_doc},
      upsert=True,
  )
  print(
      f"💰 Payroll generated for {email} ({month_year}) | Net Salary:"
      f" ${net_salary}"
  )


# --- Quick Test Execution ---
if __name__ == "__main__":
  print("Testing MongoDB Connection...")

  # Test adding a dummy employee
  add_employee("Alice", "Smith", "alice@company.com", "Engineering", 75000)

  # Test fetching employees
  print("\nCurrent Employees in Database:")
  for emp in get_all_employees():
    print(emp)

def verify_login(email, password):
  hashed_password = hashlib.sha256(password.encode()).hexdigest()

  user = db.employees.find_one({"email": email})
  if user:
    stored_password = user.get("password")
    joining_date = user.get("joining_date")
    if stored_password == hashed_password or password == joining_date:
      return{
        "status": "success",
        "role": user.get("role","employee"),
        "name":f"{user.get('first_name', '')} {user.get('last_name', '')}"
      }
  return{"status":"fail","message":"Invalid email or password"}

# ==========================================
# 5. NEW ADMIN PANEL HELPER FUNCTIONS
# ==========================================

def get_employee_attendance_count(email: str):
    """Counts how many times the employee has clocked in or marked present."""
    # Counts documents where email matches and action indicates presence
    return db.attendance.count_documents({"email": email, "$or": [{"action": "Clock In"}, {"action": "Present"}]})


def calculate_salary_by_attendance(email: str, daily_rate: float, month_year: str):
    """Calculates total salary by multiplying total attendance by the daily rate."""
    total_attendance = get_employee_attendance_count(email)
    total_salary = total_attendance * daily_rate
    
    payroll_doc = {
        "email": email,
        "month_year": month_year,
        "daily_rate": daily_rate,
        "total_attendance": total_attendance,
        "total_salary": total_salary,
        "payment_status": "Calculated",
        "generated_on": datetime.now().strftime("%Y-%m-%d")
    }
    
    db.payroll.update_one(
        {"email": email, "month_year": month_year},
        {"$set": payroll_doc},
        upsert=True
    )
    print(f"💰 Calculated salary for {email}: {total_attendance} days × ${daily_rate} = ${total_salary}")
    return total_salary


def get_pending_leaves():
    """Fetches all pending leave requests so the admin can view reasons instantly."""
    return list(db.leaves.find({"status": "Pending"}))