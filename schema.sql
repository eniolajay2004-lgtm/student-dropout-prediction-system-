DROP TABLE IF EXISTS student_records;

CREATE TABLE student_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Student_ID TEXT,
    Matric_No TEXT,
    Full_Name TEXT,
    Gender TEXT,
    Age INTEGER,
    State_of_Origin TEXT,
    Programme TEXT,
    Entry_Year INTEGER,
    Level INTEGER,
    Semester_GPA REAL,
    Cumulative_GPA REAL,
    Courses_Attempted INTEGER,
    Courses_Passed INTEGER,
    Attendance_Percentage REAL,
    Failed_Courses INTEGER,
    Carryovers INTEGER,
    Scholarship_Holder TEXT,
    Tuition_Status TEXT,
    Financial_Stress_Score INTEGER,
    LMS_Login_Frequency INTEGER,
    Assignment_Submission_Rate REAL,
    Medical_Challenges TEXT,
    AI_Prediction_Verdict TEXT,
    Prediction_Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);