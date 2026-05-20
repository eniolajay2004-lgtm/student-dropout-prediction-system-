import streamlit as st
import json
import os
import requests

st.set_page_config(page_title="Student Dropout Prediction", layout="wide")
st.title("🇳🇬 Student Dropout Risk Analytics Workspace")

# Cloudflare Tunnel Target Address Gateway Link Reference
# Change this URL string to match the address printed out by your cloudflared tunnel command!
BACKEND_URL = "http://127.0.0.1:8000/predict"

# Load lists from dataset configurations profile 
if os.path.exists('dataset_profile.json'):
    with open('dataset_profile.json', 'r') as f:
        menu_options = json.load(f)
else:
    st.error("Missing layout profiles. Execute 'py train_model.py' inside terminal panel first.")
    st.stop()

col1, col2, col3 = st.columns(3)

with col1:
    st.header("📚 Performance Data")
    level = st.selectbox("Current Level", [100, 200, 300, 400, 500])
    semester_gpa = st.slider("Latest Semester GPA", 0.0, 5.0, 3.5, 0.01)
    cumulative_gpa = st.slider("Cumulative GPA (CGPA)", 0.0, 5.0, 3.4, 0.01)
    courses_attempted = st.number_input("Courses Attempted", min_value=1, max_value=20, value=8)
    courses_passed = st.number_input("Courses Passed", min_value=0, max_value=20, value=7)
    failed_courses = st.number_input("Failed Courses", min_value=0, max_value=20, value=1)
    carryovers = st.number_input("Total Active Carryovers", min_value=0, max_value=30, value=1)

with col2:
    st.header("🏃‍♂️ Engagement Profile")
    attendance = st.slider("Class Attendance Rate (%)", 0.0, 100.0, 85.0, 0.1)
    lms_login = st.number_input("LMS Logins / Month", min_value=0, value=15)
    assignment_rate = st.slider("Assignment Submissions (%)", 0.0, 100.0, 90.0, 0.1)
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=15, max_value=60, value=20)
    entry_year = st.number_input("Entry Year", min_value=2018, max_value=2026, value=2025)

with col3:
    st.header("📋 Demographics & Finance")
    state_of_origin = st.selectbox("State of Origin", menu_options['State_of_Origin'])
    programme = st.selectbox("Programme/Course", menu_options['Programme'])
    medical = st.selectbox("Medical Challenges", menu_options['Medical_Challenges'])
    scholarship = st.selectbox("Scholarship Holder?", ["No", "Yes"])
    tuition_status = st.selectbox("Tuition Status", ["Paid", "Pending"])
    financial_stress = st.slider("Financial Stress Score (1-10)", 1, 10, 4)

st.divider()

if st.button("🔥 Run Dropout Risk Analysis", type="primary", use_container_width=True):
    payload = {
        "Gender": gender, "Age": age, "State_of_Origin": state_of_origin, "Programme": programme,
        "Entry_Year": entry_year, "Level": level, "Semester_GPA": semester_gpa, "Cumulative_GPA": cumulative_gpa,
        "Courses_Attempted": courses_attempted, "Courses_Passed": courses_passed, "Attendance_Percentage": attendance,
        "Failed_Courses": failed_courses, "Carryovers": carryovers, "Scholarship_Holder": scholarship,
        "Tuition_Status": tuition_status, "Financial_Stress_Score": financial_stress, "LMS_Login_Frequency": lms_login,
        "Assignment_Submission_Rate": assignment_rate, "Medical_Challenges": medical
    }
    
    try:
        response = requests.post(BACKEND_URL, json=payload)
        if response.status_code == 200:
            res_data = response.json()
            prob = res_data["dropout_probability"] * 100
            
            st.subheader("Analysis Verdict:")
            if res_data["verdict"] == "Dropout":
                st.error(f"⚠️ **High Risk of Dropout Identified.** (Calculated Risk: {prob:.2f}%)")
            else:
                st.success(f"✅ **Low Risk Student Status Verified.** (Calculated Risk: {prob:.2f}%)")
        else:
            st.error(f"Backend Server Error: {response.text}")
    except Exception as network_err:
        st.error(f"Failed connecting to the Backend Engine Router. Ensure uvicorn is running. Details: {network_err}")