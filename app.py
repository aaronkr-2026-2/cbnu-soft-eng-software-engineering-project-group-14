import datetime
from google import genai
import pandas as pd
import streamlit as st

# Initialize GenAI Client (Make sure to set your GEMINI_API_KEY environment variable)
# client = genai.Client()

st.set_page_config(
    page_title="HRMS MVP Dashboard", page_icon="👥", layout="wide"
)

# Initialize Mock Data in Streamlit Session State
if "employees" not in st.session_state:
  st.session_state.employees = [
      {
          "id": 1,
          "name": "Alice Smith",
          "department": "Engineering",
          "salary": 75000,
      },
      {
          "id": 2,
          "name": "Bob Jones",
          "department": "HR",
          "salary": 60000,
      },
      {
          "id": 3,
          "name": "Charlie Brown",
          "department": "Marketing",
          "salary": 65000,
      },
  ]

if "attendance" not in st.session_state:
  st.session_state.attendance = []

if "leaves" not in st.session_state:
  st.session_state.leaves = []

st.title("🚀 AI-Powered HRMS Mini MVP")
st.markdown(
    "A lightweight prototype tracking employees, attendance, and an AI HR"
    " Assistant."
)

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["👥 Employees", "⏰ Attendance", "🏖️ Leave Requests", "🤖 AI HR Chatbot"]
)

# ----------------------------------------------------
# TAB 1: EMPLOYEE DIRECTORY & PROFILES
# ----------------------------------------------------
with tab1:
  st.header("Employee Directory")

  # Display current employees
  df_employees = pd.DataFrame(st.session_state.employees)
  st.dataframe(df_employees, use_container_width=True)

  st.subheader("Add New Employee")
  with st.form("add_employee_form"):
    name = st.text_input("Full Name")
    department = st.selectbox(
        "Department", ["Engineering", "HR", "Marketing", "Sales", "Finance"]
    )
    salary = st.number_input("Base Salary ($)", min_value=30000, step=5000)
    submitted = st.form_submit_button("Add Employee")

    if submitted and name:
      new_id = (
          max([e["id"] for e in st.session_state.employees]) + 1
          if st.session_state.employees
          else 1
      )
      st.session_state.employees.append(
          {"id": new_id, "name": name, "department": department, "salary": salary}
      )
      st.success(f"Employee {name} added successfully!")
      st.rerun()

# ----------------------------------------------------
# TAB 2: ATTENDANCE SIMULATOR
# ----------------------------------------------------
with tab2:
  st.header("Attendance Tracker")

  if not st.session_state.employees:
    st.warning("Please add an employee first.")
  else:
    emp_names = [e["name"] for e in st.session_state.employees]
    selected_emp = st.selectbox("Select Employee", emp_names, key="att_emp")

    col1, col2 = st.columns(2)
    with col1:
      if st.button("Clock In"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.attendance.append({
            "Employee": selected_emp,
            "Action": "Clock In",
            "Time": now,
        })
        st.success(f"{selected_emp} clocked in at {now}")

    with col2:
      if st.button("Clock Out"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.attendance.append({
            "Employee": selected_emp,
            "Action": "Clock Out",
            "Time": now,
        })
        st.info(f"{selected_emp} clocked out at {now}")

    st.subheader("Today's Attendance Log")
    if st.session_state.attendance:
      st.dataframe(
          pd.DataFrame(st.session_state.attendance), use_container_width=True
      )
    else:
      st.info("No attendance records yet today.")

# ----------------------------------------------------
# TAB 3: LEAVE MANAGEMENT
# ----------------------------------------------------
with tab3:
  st.header("Leave Requests")

  with st.form("leave_form"):
    emp_names = [e["name"] for e in st.session_state.employees]
    leave_emp = st.selectbox("Employee Name", emp_names, key="leave_emp")
    leave_type = st.selectbox(
        "Leave Type", ["Casual Leave", "Sick Leave", "Annual Leave"]
    )
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    reason = st.text_area("Reason")
    leave_submitted = st.form_submit_button("Submit Request")

    if leave_submitted:
      st.session_state.leaves.append({
          "Employee": leave_emp,
          "Type": leave_type,
          "From": str(start_date),
          "To": str(end_date),
          "Reason": reason,
          "Status": "Pending",
      })
      st.success("Leave request submitted successfully!")

  st.subheader("Submitted Leave Requests")
  if st.session_state.leaves:
    st.dataframe(
        pd.DataFrame(st.session_state.leaves), use_container_width=True
    )
  else:
    st.info("No leave requests found.")

# ----------------------------------------------------
# TAB 4: AI HR CHATBOT
# ----------------------------------------------------
with tab4:
  st.header("🤖 AI HR Assistant")
  st.markdown(
      "Ask questions about company data, employee headcount, or general HR"
      " queries."
  )

  user_query = st.text_input(
      "Ask your HR assistant something:",
      placeholder="e.g., How many employees do we have in Engineering?",
  )

  if st.button("Ask AI"):
    if not user_query:
      st.warning("Please enter a question.")
    else:
      with st.spinner("Thinking..."):
        # Compile current mock database state to pass context to the LLM
        context_data = f"""
                Current Employees: {st.session_state.employees}
                Attendance Logs: {st.session_state.attendance}
                Leave Requests: {st.session_state.leaves}
                """

        prompt = f"""
                You are a helpful HR management assistant. Answer the user's question based strictly on the provided company state data below. If you don't know, say you don't know.
                
                Company Data Context:
                {context_data}
                
                User Question: {user_query}
                """

        try:
          # Using the standard Google GenAI client call
          client = genai.Client()
          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=prompt
          )
          st.success("AI Response:")
          st.write(response.text)
        except Exception as e:
          st.error(
              f"Error connecting to AI API. Ensure your GEMINI_API_KEY is"
              f" set. Details: {e}"
          )