import sqlite3
import pandas as pd
import os

DB_NAME = "student_dropout.db"
CSV_NAME = "updated_nigerian_student_dropout_dataset_5000.csv"

def initialize_production_database():
    print(f"📦 Initializing Database System: {DB_NAME}...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Dynamically read the CSV header first to build a matching database
    if not os.path.exists(CSV_NAME):
        print(f"❌ Error: '{CSV_NAME}' not found in this directory.")
        conn.close()
        return

    df = pd.read_csv(CSV_NAME)
    
    # Clean out the phantom "Unnamed" columns right away
    df = df.loc[:, ~df.columns.str.contains('^Unnamed:')]
    
    # Get the list of clean columns that actually exist in your CSV
    actual_columns = df.columns.tolist()
    print(f"🔍 Found {len(actual_columns)} valid columns in your CSV file.")
    
    # 2. Map standard SQL types based on the columns found
    sql_column_definitions = []
    for col in actual_columns:
        # Determine data type dynamically
        if df[col].dtype == 'int64':
            col_type = "INTEGER"
        elif df[col].dtype == 'float64':
            col_type = "REAL"
        else:
            col_type = "TEXT"
            
        sql_column_definitions.append(f"[{col}] {col_type}")
    
    # Append our tracking columns at the end
    sql_column_definitions.append("[AI_Prediction_Verdict] TEXT")
    sql_column_definitions.append("[Prediction_Timestamp] DATETIME DEFAULT CURRENT_TIMESTAMP")
    
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS student_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {', '.join(sql_column_definitions)}
        )
    """
    
    # Drop old broken table if it exists and create the clean one
    cursor.execute("DROP TABLE IF EXISTS student_records")
    cursor.execute(create_table_query)
    conn.commit()
    print("✅ Fresh database table schema generated based exactly on your CSV layout.")
    
    # 3. Migrate data rows cleanly
    try:
        df.to_sql('student_records', conn, if_exists='append', index=False)
        cursor.execute("SELECT COUNT(*) FROM student_records")
        print(f"🎉 Success! Database fully populated with {cursor.fetchone()[0]} rows from your CSV file.")
    except Exception as e:
        print(f"❌ Error during data migration: {str(e)}")
        
    conn.close()

if __name__ == '__main__':
    initialize_production_database()