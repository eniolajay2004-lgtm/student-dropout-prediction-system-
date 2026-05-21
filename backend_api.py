import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prediction_logic import StudentDropoutRiskLogic

app = FastAPI(
    title="Student Risk API Engine",
    description="Predicts student dropout risk using a trained ML model with rule-based fallback.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "student_dropout.db"

# Whitelist of allowed columns to prevent SQL injection via column names
ALLOWED_COLUMNS = [
    "Student_ID", "Matric_No", "Full_Name", "Gender", "Age",
    "State_of_Origin", "Programme", "Entry_Year", "Level",
    "Semester_GPA", "Cumulative_GPA", "Courses_Attempted",
    "Courses_Passed", "Attendance_Percentage", "Failed_Courses",
    "Carryovers", "Scholarship_Holder", "Tuition_Status",
    "Financial_Stress_Score", "LMS_Login_Frequency",
    "Assignment_Submission_Rate", "Medical_Challenges",
    "AI_Prediction_Verdict",
]


class StudentInputSchema(BaseModel):
    Student_ID: str = "NEW"
    Matric_No: str = "NEW"
    Full_Name: str = "Anonymous"
    Gender: str
    Age: int
    State_of_Origin: str
    Programme: str
    Entry_Year: int
    Level: int
    Semester_GPA: float
    Cumulative_GPA: float
    Courses_Attempted: int
    Courses_Passed: int
    Attendance_Percentage: float
    Failed_Courses: int
    Carryovers: int
    Scholarship_Holder: str
    Tuition_Status: str
    Financial_Stress_Score: int
    LMS_Login_Frequency: int
    Assignment_Submission_Rate: float
    Medical_Challenges: str


@contextmanager
def get_db():
    """Context manager for safe database connections."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Student Risk API Engine"}


@app.post("/predict")
async def handle_prediction(data: StudentInputSchema):
    result = StudentDropoutRiskLogic.evaluate_risk(data.model_dump())

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error_message"])

    # Persist prediction to SQLite
    try:
        record = data.model_dump()
        record["AI_Prediction_Verdict"] = result["verdict"]

        # Only use whitelisted columns
        safe_columns = [col for col in record.keys() if col in ALLOWED_COLUMNS]
        placeholders = ", ".join(["?"] * len(safe_columns))
        values = [record[col] for col in safe_columns]
        column_names = ", ".join(f"[{col}]" for col in safe_columns)

        with get_db() as conn:
            conn.execute(
                f"INSERT INTO student_records ({column_names}) VALUES ({placeholders})",
                values,
            )
            conn.commit()
    except Exception as db_err:
        # Log but don't fail the prediction response
        print(f"⚠️ Database tracking warning: {db_err}")

    return result