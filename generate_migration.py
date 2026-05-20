import pandas as pd
import os

CSV_NAME = "updated_nigerian_student_dropout_dataset_5000.csv"

if os.path.exists(CSV_NAME):
    df = pd.read_csv(CSV_NAME)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed:')]
    
    # Add empty placeholders for the prediction tracking columns
    df['AI_Prediction_Verdict'] = 'Baseline'
    
    with open('migration.sql', 'w', encoding='utf-8') as f:
        print("Creating migration.sql file...")
        for _, row in df.iterrows():
            columns = ", ".join([f"[{col}]" for col in df.columns])
            
            # Format values cleanly for SQL
            formatted_values = []
            for val in row.values:
                if pd.isna(val):
                    formatted_values.append("NULL")
                elif isinstance(val, str):
                    # Escape single quotes in text fields (like names)
                    safe_str = val.replace("'", "''")
                    formatted_values.append(f"'{safe_str}'")
                else:
                    formatted_values.append(str(val))
                    
            values_str = ", ".join(formatted_values)
            f.write(f"INSERT INTO student_records ({columns}) VALUES ({values_str});\n")
            
    print("🎉 Success! migration.sql generated.")