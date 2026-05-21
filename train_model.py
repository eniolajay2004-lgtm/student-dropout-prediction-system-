import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

CSV_NAME = "updated_nigerian_student_dropout_dataset_5000.csv"
MODEL_PATH = "dropout_model.joblib"
ENCODERS_PATH = "label_encoders.joblib"
PROFILE_PATH = "dataset_profile.json"

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


def generate_risk_target(df: pd.DataFrame) -> pd.Series:
    """
    Derive a binary dropout-risk target from domain knowledge rules.
    A student is labeled 'at risk' (1) if their composite score >= 50.
    """
    cgpa = df["Cumulative_GPA"].fillna(5.0)
    attendance = df["Attendance_Percentage"].fillna(100.0)
    carryovers = df["Carryovers"].fillna(0)
    failed = df["Failed_Courses"].fillna(0)
    stress = df["Financial_Stress_Score"].fillna(1)
    tuition = df["Tuition_Status"].fillna("Paid").astype(str).str.strip().str.lower()

    risk = pd.Series(0.0, index=df.index)
    risk += cgpa.lt(1.5) * 30
    risk += cgpa.ge(1.5).mul(cgpa.lt(2.5)) * 15

    backlog = carryovers + failed
    risk += backlog.gt(4) * 25
    risk += backlog.gt(1).mul(backlog.le(4)) * 10

    risk += attendance.lt(70.0) * 25
    risk += attendance.ge(70.0).mul(attendance.lt(80.0)) * 10

    risk += (tuition.eq("pending") | stress.gt(7)) * 20
    risk += tuition.ne("pending").mul(stress.gt(4)).mul(stress.le(7)) * 10

    return (risk >= 50).astype(int)


def generate_data_profile(df: pd.DataFrame) -> None:
    """Generate dropdown option lists for the Streamlit UI."""
    profile = {
        "Programme": sorted(df["Programme"].dropna().unique().tolist()),
        "State_of_Origin": sorted(df["State_of_Origin"].dropna().unique().tolist()),
        "Medical_Challenges": sorted(df["Medical_Challenges"].dropna().unique().tolist()),
    }
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=4)
    print("📋 Saved UI dropdown configurations to dataset_profile.json")


def train_model() -> None:
    print("🚀 Starting model training pipeline...")

    if not os.path.exists(CSV_NAME):
        print(f"❌ Error: {CSV_NAME} not found.")
        return

    df = pd.read_csv(CSV_NAME)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed:")]
    print(f"📊 Loaded {len(df)} records with {len(df.columns)} columns")

    # Generate UI profile
    generate_data_profile(df)

    # Generate target labels from domain rules
    df["dropout_target"] = generate_risk_target(df)
    counts = df["dropout_target"].value_counts().to_dict()
    print(f"🎯 Target distribution — Active: {counts.get(0, 0)}, At Risk: {counts.get(1, 0)}")

    # Prepare features
    features = df[FEATURE_COLUMNS].copy()

    # Encode categorical columns
    encoders = {}
    for col in CATEGORICAL_COLUMNS:
        le = LabelEncoder()
        features[col] = le.fit_transform(features[col].fillna("Unknown").astype(str))
        encoders[col] = le

    # Fill remaining NaN in numeric columns
    features = features.fillna(0)
    target = df["dropout_target"]

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )

    # Train a Gradient Boosting classifier
    model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n📈 Model Accuracy: {accuracy:.4f}")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Active", "At Risk"]))

    # Feature importance ranking
    importance = pd.DataFrame(
        {"Feature": FEATURE_COLUMNS, "Importance": model.feature_importances_}
    ).sort_values("Importance", ascending=False)
    print("\n🔍 Top Feature Importances:")
    print(importance.to_string(index=False))

    # Persist model and encoders
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    print(f"\n💾 Model saved to {MODEL_PATH}")
    print(f"💾 Encoders saved to {ENCODERS_PATH}")


if __name__ == "__main__":
    train_model()