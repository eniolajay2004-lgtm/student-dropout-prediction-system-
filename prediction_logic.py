class StudentDropoutRiskLogic:
    @staticmethod
    def evaluate_risk(data: dict) -> dict:
        """
        Analyzes academic and financial parameters to compute 
        an institutional risk index percentage.
        """
        try:
            risk_points = 0
            max_points = 100
            
            # 1. CGPA Metric (Max 30 points)
            cgpa = float(data.get('Cumulative_GPA', 5.0))
            if cgpa < 1.5:
                risk_points += 30  # Academic Probation Status
            elif cgpa < 2.5:
                risk_points += 15
                
            # 2. Failed Courses & Carryovers (Max 25 points)
            carryovers = int(data.get('Carryovers', 0))
            failed = int(data.get('Failed_Courses', 0))
            if (carryovers + failed) > 4:
                risk_points += 25
            elif (carryovers + failed) > 1:
                risk_points += 10
                
            # 3. Class Attendance (Max 25 points)
            attendance = float(data.get('Attendance_Percentage', 100.0))
            if attendance < 70.0:
                risk_points += 25  # Below exam sitting threshold
            elif attendance < 80.0:
                risk_points += 10
                
            # 4. Financial Status & Stress (Max 20 points)
            tuition = str(data.get('Tuition_Status', 'Paid')).strip().lower()
            stress = int(data.get('Financial_Stress_Score', 1))
            if tuition == 'pending' or stress > 7:
                risk_points += 20
            elif stress > 4:
                risk_points += 10
                
            # Calculate final results
            probability = risk_points / max_points
            verdict = "Dropout" if probability >= 0.50 else "Active"
            
            return {
                "success": True,
                "dropout_probability": round(probability, 4),
                "verdict": verdict,
                "error_message": None
            }
        except Exception as e:
            return {
                "success": False,
                "dropout_probability": 0.0,
                "verdict": "Unknown",
                "error_message": str(e)
            }