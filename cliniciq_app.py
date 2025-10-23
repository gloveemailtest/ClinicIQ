import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import os

# ------------------------------
# SETUP
# ------------------------------
st.set_page_config(page_title="ClinicIQ", layout="wide")
st.title("💡 ClinicIQ – AI Dashboard for PT Clinics")

st.write("Upload your clinic’s exported data below to see instant insights.\nSupported formats: CSV or Excel files.")

# Sidebar file uploads
st.sidebar.header("📂 Upload Your Data Files")
visits_file = st.sidebar.file_uploader("Upload Visits.csv", type=["csv", "xlsx"])
referrals_file = st.sidebar.file_uploader("Upload Referrals.csv", type=["csv", "xlsx"])
therapists_file = st.sidebar.file_uploader("Upload Therapists.csv", type=["csv", "xlsx"])

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def load_file(file):
    if file is None:
        return None
    if file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Auto-rename common variations
    rename_map = {
        "revenue_($)": "revenue",
        "total_revenue": "revenue",
        "revenue_usd": "revenue",
        "therapist_name": "therapist",
        "date_of_visit": "date"
    }
    df.rename(columns=rename_map, inplace=True)
    return df

def generate_ai_summary(visits, therapists, referrals):
    """Send uploaded data to OpenRouter API for GPT-style insights."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY", st.secrets.get("OPENROUTER_API_KEY", None))
    if not openrouter_key:
        return "⚠️ Missing OpenRouter API key. Please add it in Streamlit Secrets."

    summary_prompt = f"""
    You are an expert business analyst for physical therapy clinics.
    Analyze the following datasets and generate 3–5 insights:
    1. Clinic volume or growth trends.
    2. Therapist productivity and performance.
    3. Referral source effectiveness.
    4. One risk or opportunity.
    5. One actionable recommendation.

    Visits sample:
    {visits.head(5).to_string(index=False)}

    Therapists sample:
    {therapists.head(5).to_string(index=False)}

    Referrals sample:
    {referrals.head(5).to_string(index=False)}
    """

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": summary_prompt}],
        "max_tokens": 250
    }

    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI Summary could not be generated: {e}"

# ------------------------------
# LOAD DATA
# ------------------------------
visits = load_file(visits_file)
referrals = load_file(referrals_file)
therapists = load_file(therapists_file)

# ------------------------------
# MAIN DASHBOARD
# ------------------------------
if visits is not None and referrals is not None and therapists is not None:
    st.success("✅ Data uploaded successfully! Scroll down for analytics.")

    # --- AI Summary ---
    st.subheader("📊 AI Summary")
    with st.spinner("Analyzing your clinic data..."):
        summary = generate_ai_summary(visits, therapists, referrals)
        st.write(summary)

    # --- CLINIC OVERVIEW ---
    st.header("🏥 Clinic Overview")

    if "revenue" in visits.columns:
        total_revenue = visits["revenue"].sum()
        avg_revenue = visits["revenue"].mean()
    else:
        st.error("⚠️ Your Visits file must include a 'Revenue' column.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Visits", len(visits))
    col2.metric("Total Revenue", f"${total_revenue:,.0f}")
    col3.metric("Avg Revenue/Visit", f"${avg_revenue:,.0f}")

    if "date" in visits.columns and "therapist" in visits.columns:
        fig_visits = px.histogram(visits, x="date", y="revenue", color="therapist", barmode="group", title="Revenue by Date and Therapist")
        st.plotly_chart(fig_visits, use_container_width=True)

    # --- THERAPIST PERFORMANCE ---
    st.header("💪 Therapist Performance")
    st.dataframe(therapists)
    if "therapist" in therapists.columns and "revenue_this_week" in therapists.columns:
        fig_ther = px.bar(therapists, x="therapist", y="revenue_this_week", color="therapist", title="Revenue per Therapist")
        st.plotly_chart(fig_ther, use_container_width=True)

    # --- REFERRAL SOURCES ---
    st.header("🔗 Referral Source Performance")
    st.dataframe(referrals)
    if "referral_source" in referrals.columns and "avg_revenue_per_patient" in referrals.columns:
        fig_ref = px.bar(referrals, x="referral_source", y="avg_revenue_per_patient", color="specialty", title="Revenue per Referral Source")
        st.plotly_chart(fig_ref, use_container_width=True)

    # --- ADD-ONS ---
    st.header("📄 Export & Sharing")

    # 1️⃣ Download AI summary as text
    summary_bytes = io.BytesIO(summary.encode())
    st.download_button("📥 Download AI Summary", summary_bytes, file_name="clinic_summary.txt")

    # 2️⃣ Export combined CSV (optional example)
    combined_csv = io.BytesIO(visits.to_csv(index=False).encode())
    st.download_button("📊 Download Visits CSV", combined_csv, file_name="visits_data.csv")

    # 3️⃣ Email placeholder (would require integration later)
    st.info("📧 Email report feature coming soon — will automatically send summaries to clinic owners.")

else:
    st.warning("Please upload all three files (Visits, Referrals, Therapists) to see your dashboard.")
