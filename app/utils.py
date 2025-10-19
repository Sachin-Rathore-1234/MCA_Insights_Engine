import pandas as pd
import json
from datetime import datetime
import os

# ------------------------------
# Data Loading Utilities
# ------------------------------
def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        print(f"⚠️ File not found: {path}")
        return pd.DataFrame()

def save_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)

# ------------------------------
# Change Detection Logic
# ------------------------------
def detect_changes(prev_df, curr_df):
    """Compares two MCA snapshots and detects changes."""
    changes = []

    common_cins = set(prev_df["CIN"]).intersection(set(curr_df["CIN"]))

    for cin in common_cins:
        prev_row = prev_df[prev_df["CIN"] == cin].iloc[0]
        curr_row = curr_df[curr_df["CIN"] == cin].iloc[0]

        for col in prev_df.columns:
            if prev_row[col] != curr_row[col]:
                changes.append({
                    "CIN": cin,
                    "Change_Type": "Field Update",
                    "Field_Changed": col,
                    "Old_Value": prev_row[col],
                    "New_Value": curr_row[col],
                    "Date": datetime.now().strftime("%Y-%m-%d")
                })

    # New incorporations
    new_cins = set(curr_df["CIN"]) - set(prev_df["CIN"])
    for cin in new_cins:
        changes.append({
            "CIN": cin,
            "Change_Type": "New Incorporation",
            "Field_Changed": "All",
            "Old_Value": None,
            "New_Value": "New company added",
            "Date": datetime.now().strftime("%Y-%m-%d")
        })

    # Deregistered companies
    removed_cins = set(prev_df["CIN"]) - set(curr_df["CIN"])
    for cin in removed_cins:
        changes.append({
            "CIN": cin,
            "Change_Type": "Deregistered",
            "Field_Changed": "All",
            "Old_Value": "Company existed before",
            "New_Value": None,
            "Date": datetime.now().strftime("%Y-%m-%d")
        })

    return pd.DataFrame(changes)


# ------------------------------
# AI Summary Generator
# ------------------------------
def generate_summary(changes_df, save_path="reports/daily_summary.json"):
    """Creates AI-style daily summary statistics."""
    summary = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "new_incorporations": int((changes_df["Change_Type"] == "New Incorporation").sum()),
        "deregistered": int((changes_df["Change_Type"] == "Deregistered").sum()),
        "field_updates": int((changes_df["Change_Type"] == "Field Update").sum()),
    }

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w") as f:
        json.dump(summary, f, indent=4)

    print(f"✅ Summary saved to {save_path}")
    return summary
