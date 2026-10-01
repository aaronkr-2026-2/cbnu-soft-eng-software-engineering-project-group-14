from datetime import datetime
from pymongo import MongoClient

# 1. Connect to MongoDB (local or Atlas URI)
# If running locally with default port, use "mongodb://localhost:27017/"
client = MongoClient("mongodb://localhost:27017/")

# 2. Create/Access the database
db = client["hrms_db"]


# --- Employee Operations ---
def add_employee(first_name, last_name, email, department, salary):
  employee_doc = {
      "first_name": first_name,
      "last_name": last_name,
      "email": email,
      "department": department,
      "base_salary": salary,
      "joining_date": datetime.now().strftime("%Y-%m-%d"),
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


# --- Quick Test Execution ---
if __name__ == "__main__":
  print("Testing MongoDB Connection...")

  # Test adding a dummy employee
  add_employee("Alice", "Smith", "alice@company.com", "Engineering", 75000)

  # Test fetching employees
  print("\nCurrent Employees in Database:")
  for emp in get_all_employees():
    print(emp)