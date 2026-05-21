import os

import joblib
import numpy as np

MODEL_PATH = "dropout_model.joblib"
ENCODERS_PATH = "label_encoders.joblib"

FEATURE_COLUMNS = [
    "Age",
    "Entry_Year",
    "Level",
    "Semester_GPA",
    "Cumulative_GPA",
    "Courses_Attempted",
    "Courses_Passed",
    "Attendance_Percentage",
    "Failed_Courses",
    "Carryovers",
    "Financial_Stress_Score",
    "LMS_Login_Frequency",
    "Assignment_Submission_Rate",
    "Gender",
    "Scholarship_Holder",
    "Tuition_Status",
]

CATEGORICAL_COLUMNS = ["Gender", "Scholarship_Holder", "Tuition_Status"]


class StudentDropoutRiskLogic:
    _model = None
    _encoders = None
    _model_available = False

    @classmethod
    def _load_model(cls) -> None:
        """Load the trained model and encoders once on first call."""
        if cls._model is not None:
            return
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH):
                cls._model = joblib.load(MODEL_PATH)
                cls._encoders = joblib.load(ENCODERS_PATH)
                cls._model_available = True
        except Exception:
            cls._model_available = False

    @classmethod
    def _ml_predict(cls, data: dict) -> float | None:
        """
        Run the trained ML model on a single student record.
        Returns the predicted dropout probability, or None if unavailable.
        """
        cls._load_model()
        if not cls._model_available:
            return None

        try:
            features = []
            for col in FEATURE_COLUMNS:
                value = data.get(col, 0)
                if col in CATEGORICAL_COLUMNS:
                    encoder = cls._encoders.get(col)
                    if encoder is not None:
                        str_val = str(value).strip() if value else "Unknown"
                        if str_val in encoder.classes_:
                            value = encoder.transform([str_val])[0]
                        else:
                            value = 0
                    else:
                        value = 0
                else:
                    try:
                        value = float(value) if value is not None else 0.0
                    except (ValueError, TypeError):
                        value = 0.0
                features.append(value)

            X = np.array(features).reshape(1, -1)
            probability = cls._model.predict_proba(X)[0][1]
            return float(probability)
        except Exception:
            return None

    @staticmethod
    def _rule_based_score(data: dict) -> float:
        """
        Fallback rule-based scoring engine.
        Returns a risk score between 0 and 1.
        """
        risk_points = 0

        # CGPA metric (max 30 points)
        cgpa = float(data.get("Cumulative_GPA", 5.0) or 5.0)
        if cgpa < 1.5:
            risk_points += 30
        elif cgpa < 2.5:
            risk_points += 15

        # Failed courses and carryovers (max 25 points)
        carryovers = int(data.get("Carryovers", 0) or 0)
        failed = int(data.get("Failed_Courses", 0) or 0)
        if (carryovers + failed) > 4:
            risk_points += 25
        elif (carryovers + failed) > 1:
            risk_points += 10

        # Class attendance (max 25 points)
        attendance = float(data.get("Attendance_Percentage", 100.0) or 100.0)
        if attendance < 70.0:
            risk_points += 25
        elif attendance < 80.0:
            risk_points += 10

        # Financial status and stress (max 20 points)
        tuition = str(data.get("Tuition_Status", "Paid")).strip().lower()
        stress = int(data.get("Financial_Stress_Score", 1) or 1)
        if tuition == "pending" or stress > 7:
            risk_points += 20
        elif stress > 4:
            risk_points += 10

        return risk_points / 100

    @classmethod
    def evaluate_risk(cls, data: dict) -> dict:
        """
        Analyze a student record and return a dropout risk assessment.
        Uses the trained ML model when available, with a rule-based fallback.
        """
        try:
            ml_probability = cls._ml_predict(data)
            rule_probability = cls._rule_based_score(data)

            if ml_probability is not None:
                # Blend: 70% ML model, 30% rule-based for interpretability
                probability = (0.7 * ml_probability) + (0.3 * rule_probability)
                method = "ml_blended"
            else:
                probability = rule_probability
                method = "rule_based"

            verdict = "Dropout" if probability >= 0.50 else "Active"

            return {
                "success": True,
                "dropout_probability": round(probability, 4),
                "verdict": verdict,
                "method": method,
                "error_message": None,
            }
        except Exception as e:
            return {
                "success": False,
                "dropout_probability": 0.0,
                "verdict": "Unknown",
                "method": "error",
                "error_message": str(e),
            }