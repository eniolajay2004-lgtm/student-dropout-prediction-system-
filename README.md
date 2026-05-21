# Student Dropout Prediction System

An intelligent student retention dashboard that predicts dropout risk using machine learning and rule-based analytics. Built for Nigerian university administrators to identify at-risk students and prioritize support interventions.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.53-red)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8-orange)

## Features

- **Executive Overview** — Cohort-level KPIs, risk distribution charts, and attendance/GPA analytics
- **Risk Intelligence Desk** — Prioritized support queue sorted by composite risk index
- **Student Console** — Individual student lookup with full risk profile and driver breakdown
- **Sandbox Simulation** — Simulate hypothetical student profiles and see predicted outcomes
- **Data Intake Studio** — Upload, validate, and commit new student records with batch risk preview
- **CSV Export** — Download filtered cohort data and risk queue for offline analysis
- **ML-Powered Predictions** — Gradient Boosting model blended with interpretable rule-based scoring

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit with custom CSS theming |
| ML Model | scikit-learn GradientBoostingClassifier |
| API | FastAPI + Uvicorn |
| Database | SQLite |
| Data | Pandas, NumPy |
| Charts | Altair |

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the ML model

```bash
python train_model.py
```

This generates:
- `dropout_model.joblib` — trained classifier
- `label_encoders.joblib` — categorical encoders
- `dataset_profile.json` — UI dropdown options

### 3. Run the dashboard

```bash
python -m streamlit run app.py
```

The app opens at **http://localhost:8501**

### 4. (Optional) Run the API server

```bash
python -m uvicorn backend_api:app --reload
```

API docs available at **http://localhost:8000/docs**

## Project Structure

```
├── app.py                  # Streamlit dashboard (main application)
├── prediction_logic.py     # ML + rule-based risk engine
├── train_model.py          # Model training pipeline
├── backend_api.py          # FastAPI REST endpoint
├── init_db.py              # SQLite database initializer
├── schema.sql              # Database schema definition
├── generate_migration.py   # SQL migration generator
├── requirements.txt        # Python dependencies
├── dataset_profile.json    # UI dropdown configurations
├── student_dropout.db      # SQLite database
├── dropout_model.joblib    # Trained ML model
├── label_encoders.joblib   # Categorical encoders
├── .streamlit/config.toml  # Streamlit server config
└── updated_nigerian_student_dropout_dataset_5000.csv  # Dataset
```

## How the Prediction Works

The system uses a **blended approach** (70% ML / 30% rules):

1. **ML Model** — A Gradient Boosting classifier trained on 16 features including GPA, attendance, backlog, and financial indicators
2. **Rule Engine** — A transparent, point-based scoring system across 4 risk dimensions:
   - Academic standing (CGPA) — up to 30 points
   - Curriculum backlog (failed + carryover courses) — up to 25 points
   - Attendance compliance — up to 25 points
   - Financial exposure (tuition + stress) — up to 20 points

If the ML model is unavailable, the system falls back to pure rule-based scoring.

## Dataset

5,000 synthetic student records modeled on Nigerian university patterns, including:
- Demographics (name, age, gender, state of origin)
- Academic metrics (GPA, courses, attendance)
- Financial indicators (tuition status, stress score)
- Engagement signals (LMS logins, assignment submission rate)

## License

See [LICENSE](LICENSE) for details.
