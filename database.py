from datetime import datetime
from pymongo import MongoClient
import hashlib
from bson import ObjectId

Mongo_url = "mongodb+srv://atikuzzamanemon4_db_user:Atik.zaman.99@cluster0.nwgr32l.mongodb.net/"
client = MongoClient(Mongo_url)

# Create/Access the database
db = client["hrms_db"]


# --- Employee Operations ---
def add_employee(first_name, last_name, email, department, salary, role="employee"):
    joining_date_str = datetime.now().strftime("%Y-%m-%d")
    initial_password_hash = hashlib.sha256(joining_date_str.encode()).hexdigest()
    
    employee_doc = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "department": department,
        "base_salary": float(salary),  # Stored base salary for automated calculations
        "joining_date": joining_date_str,
        "password": initial_password_hash,
        "role": role,
        "status": "Active",
    }
    result = db.employees.insert_one(employee_doc)
    print(f"✅ Added employee with ID: {result.inserted_id}")


def get_all_employees():
    return list(db.employees.find({}, {"_id": 0}))  # Hide MongoDB's default _id for general lists


# --- Attendance Operations ---
def mark_attendance(db_instance, email):
    """Marks attendance for today with date and check-in time."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    
    # Check if already clocked in today
    existing = db_instance.attendance.find_one({"email": email, "date": today})
    if not existing:
        db_instance.attendance.insert_one({
            "email": email,
            "date": today,
            "time": now.strftime("%H:%M:%S"),
            "status": "Present",
            "timestamp": now
        })
        print(f"⏰ Attendance marked for {email} on {today}")
        return True
    return False


def get_employee_attendance(db_instance, email):
    return list(db_instance.attendance.find({"email": email}).sort("date", -1))


# --- Leave Request Operations ---
def submit_leave_request(db_instance, email, start_date, end_date, reason):
    leave_doc = {
        "email": email,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "status": "Pending",
        "applied_on": datetime.now().strftime("%Y-%m-%d"),
    }
    result = db_instance.leaves.insert_one(leave_doc)
    print(f"🏖 Leave request submitted for {email} (ID: {result.inserted_id})")
    return result


def get_pending_leaves():
    """Fetches all pending leave requests so the admin can view reasons instantly."""
    return list(db.leaves.find({"status": "Pending"}))


def update_leave_status(email, start_date, new_status):
    result = db.leaves.update_one(
        {"email": email, "start_date": start_date},
        {"$set": {"status": new_status}},
    )
    if result.modified_count > 0:
        print(f"📋 Leave status updated to '{new_status}' for {email}")
    else:
        print(f"⚠️ Leave request not found for {email} starting on {start_date}")


# --- Payroll & Salary Operations ---
def get_employee_attendance_count(email: str):
    """Counts how many times the employee has checked in / marked present."""
    return db.attendance.count_documents({
        "email": email, 
        "$or": [{"action": "Clock In"}, {"action": "Present"}, {"status": "Present"}]
    })


def calculate_salary_by_attendance(email: str, month_year: str):
    """Calculates total salary automatically using the stored base_salary and total attendance count."""
    employee = db.employees.find_one({"email": email})
    if not employee:
        print(f"❌ Error: Employee with email {email} not found.")
        return 0

    # Safely get base_salary or fallback to 0, ensuring it's treated as a float
    base_salary = float(employee.get("base_salary", employee.get("salary", 0)))
    total_attendance = get_employee_attendance_count(email)
    
    # Automated calculation: Base Salary * Total Attendance Days
    total_salary = base_salary * total_attendance
    
    payroll_doc = {
        "email": email,
        "month_year": month_year,
        "base_salary": base_salary,
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
    print(f"💰 Calculated salary for {email}: {total_attendance} days × Base ${base_salary} = ${total_salary}")
    return total_salary


# --- Notice Board Helpers ---
def insert_notice(db_instance, title, filename, file_path):
    notice_doc = {
        "title": title,
        "filename": filename,
        "file_path": file_path,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    return db_instance.notices.insert_one(notice_doc)

def get_all_notices(db_instance):
    return list(db_instance.notices.find().sort("uploaded_at", -1))


# --- Authentication Helper ---
def verify_login(email, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = db.employees.find_one({"email": email})
    if user:
        stored_password = user.get("password")
        joining_date = user.get("joining_date")
        if stored_password == hashed_password or password == joining_date:
            return {
                "status": "success",
                "role": user.get("role", "employee"),
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')}"
            }
    return {"status": "fail", "message": "Invalid email or password"}


# --- Quick Test Execution ---
if __name__ == "__main__":
    print("Testing MongoDB Connection...")
    for emp in get_all_employees():
        print(emp)