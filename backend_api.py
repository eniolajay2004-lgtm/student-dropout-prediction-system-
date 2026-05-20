from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from prediction_logic import StudentDropoutRiskLogic

app = FastAPI(title="Cloudflare D1 Native Risk API")

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
async def handle_prediction(data: StudentInputSchema, request: Request):
    # 1. Run the risk calculation rules engine
    result = StudentDropoutRiskLogic.evaluate_risk(data.dict())
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error_message"])
        
    try:
        # 2. Interact with Cloudflare D1 via the Worker Request Context
        # Cloudflare automatically attaches your D1 instance onto the request environment
        d1_database = request.scope["env"].DB
        
        # Build the dynamic SQL command strings
        data_dict = data.dict()
        columns = list(data_dict.keys()) + ['AI_Prediction_Verdict']
        col_names_str = ", ".join([f"[{c}]" for c in columns])
        
        # Build matching question-mark binding parameters for Cloudflare's driver
        placeholders = ", ".join(["?"] * len(columns))
        values = list(data_dict.values()) + [result["verdict"]]
        
        query = f"INSERT INTO student_records ({col_names_str}) VALUES ({placeholders})"
        
        # Execute the transaction across Cloudflare's edge network
        await d1_database.prepare(query).bind(*values).run()
        
    except Exception as d1_err:
        # If your local environment doesn't have D1 bound yet, print a warning but return the result
        print(f"⚠️ Cloudflare D1 Sync Warning: {d1_err}")
        
    return result