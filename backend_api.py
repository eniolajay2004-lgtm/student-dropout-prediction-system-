from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prediction_logic import StudentDropoutRiskLogic
import sqlite3

app = FastAPI(title="Student Risk API Engine")

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

@app.post("/predict")
async def handle_prediction(data: StudentInputSchema):
    # Process through our logic calculation layout
    result = StudentDropoutRiskLogic.evaluate_risk(data.dict())
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error_message"])
        
    # Persist directly into SQLite tables
    try:
        conn = sqlite3.connect('student_dropout.db')
        cursor = conn.cursor()
        
        # Build dynamic queries based on columns that exist in database
        columns = list(data.dict().keys()) + ['AI_Prediction_Verdict']
        placeholders = ", ".join(["?"] * len(columns))
        values = list(data.dict().values()) + [result["verdict"]]
        
        query = f"INSERT INTO student_records ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"⚠️ Database tracking warning: {db_err}")
        
    return result