import pandas as pd
import json
import os

CSV_NAME = 'updated_nigerian_student_dropout_dataset_5000.csv'

def generate_data_profile():
    print("📋 Analyzing dataset structure for configuration profile...")
    if not os.path.exists(CSV_NAME):
        print(f"❌ Error: {CSV_NAME} missing.")
        return
        
    df = pd.read_csv(CSV_NAME)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed:')]
    
    # Grab unique items for dropdown list components in UI
    profile = {
        "Programme": sorted(df['Programme'].dropna().unique().tolist()),
        "State_of_Origin": sorted(df['State_of_Origin'].dropna().unique().tolist()),
        "Medical_Challenges": sorted(df['Medical_Challenges'].dropna().unique().tolist())
    }
    
    with open('dataset_profile.json', 'w') as f:
        json.dump(profile, f, indent=4)
        
    print("💾 Saved dataset menu configurations to 'dataset_profile.json'!")

if __name__ == '__main__':
    generate_data_profile()