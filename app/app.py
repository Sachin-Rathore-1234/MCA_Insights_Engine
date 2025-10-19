import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ------------------------------
# Load Datasets
# ------------------------------
@st.cache_data
def load_data():
    master_path = "data/processed/mca_master.csv"
    changes_path = "data/change_logs/daily_changes.csv"
    enriched_path = "data/enriched/enriched_companies.csv"

    master_df = pd.read_csv(master_path) if os.path.exists(master_path) else pd.DataFrame()
    changes_df = pd.read_csv(changes_path) if os.path.exists(changes_path) else pd.DataFrame()
    enriched_df = pd.read_csv(enriched_path) if os.path.exists(enriched_path) else pd.DataFrame()

    return master_df, changes_df, enriched_df

master_df, changes_df, enriched_df = load_data()

# ------------------------------
# Streamlit App Layout
# ------------------------------
st.set_page_config(page_title="MCA Insights Engine", layout="wide")

st.title("🏢 MCA Insights Engine")
st.markdown("### AI-powered Company Change Tracker & Insights System")

# Sidebar navigation
st.sidebar.title("📂 Navigation")
section = st.sidebar.radio("Go to", ["Search Company", "Change Logs", "Enriched Data", "AI Summary", "Chat with Data"])

# ------------------------------
# Search Company Section
# ------------------------------
if section == "Search Company":
    st.header("🔍 Search Company Details")
    query = st.text_input("Enter CIN or Company Name:")
    if query:
        results = master_df[
            master_df["COMPANY_NAME"].str.contains(query, case=False, na=False)
            | master_df["CIN"].astype(str).str.contains(query, case=False)
        ]
        if not results.empty:
            st.success(f"{len(results)} records found.")
            st.dataframe(results)
        else:
            st.warning("No matching records found.")

# ------------------------------
# Change Logs Section
# ------------------------------
elif section == "Change Logs":
    st.header("📈 Company Change Logs")
    if not changes_df.empty:
        state_filter = st.multiselect("Filter by State:", sorted(changes_df["STATE"].dropna().unique()))
        change_filter = st.multiselect("Filter by Change Type:", sorted(changes_df["Change_Type"].dropna().unique()))

        filtered = changes_df.copy()
        if state_filter:
            filtered = filtered[filtered["STATE"].isin(state_filter)]
        if change_filter:
            filtered = filtered[filtered["Change_Type"].isin(change_filter)]

        st.dataframe(filtered)
        st.bar_chart(filtered["Change_Type"].value_counts())
    else:
        st.info("No change log data available.")

# ------------------------------
# Enriched Data Section
# ------------------------------
elif section == "Enriched Data":
    st.header("🌐 Enriched Company Information")
    if not enriched_df.empty:
        st.dataframe(enriched_df)
        st.markdown("Example sources: ZaubaCorp, API Setu, GST Portal")
    else:
        st.info("No enriched data found. Please run enrichment script.")

# ------------------------------
# AI Summary Section
# ------------------------------
elif section == "AI Summary":
    st.header("🧠 AI-Generated Daily Summary")
    summary_path = "reports/daily_summary.json"

    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            summary = json.load(f)
        st.json(summary)
    else:
        st.warning("No summary file found. Please generate it after change detection.")

# ------------------------------
# Chatbot Section
# ------------------------------
elif section == "Chat with Data":
    st.header("💬 Chat with MCA Data")
    st.markdown("Ask questions like:")
    st.markdown("- *Show new incorporations in Maharashtra*")
    st.markdown("- *How many companies were struck off last month?*")
    st.markdown("- *List all companies with paid-up capital above 10 lakh*")

    user_query = st.text_input("Your question:")

    if user_query:
        response = ""
        q = user_query.lower()

        if "new incorporation" in q or "incorporated" in q:
            if "maharashtra" in q:
                count = len(changes_df[(changes_df["Change_Type"] == "New Incorporation") & (changes_df["STATE"] == "Maharashtra")])
                response = f"New incorporations in Maharashtra: {count}"
            else:
                count = len(changes_df[changes_df["Change_Type"] == "New Incorporation"])
                response = f"Total new incorporations: {count}"

        elif "struck off" in q or "deregistered" in q:
            count = len(changes_df[changes_df["Change_Type"].isin(["Struck Off", "Deregistered"])])
            response = f"Companies struck off or deregistered: {count}"

        elif "capital" in q or "paid-up" in q:
            response = "Listing companies with updated paid-up capital..."
            st.dataframe(changes_df[changes_df["Field_Changed"].str.contains("Paid", na=False)])

        else:
            response = "Sorry, I couldn’t understand your query. Please rephrase."

        st.success(response)
