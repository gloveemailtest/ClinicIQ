import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ClinicIQ", layout="wide")

st.title("💡 ClinicIQ – AI Dashboard for PT Clinics")
st.write("Upload your clinic’s exported data below to see instant insights. \
Supported formats: CSV or Excel files.")

# Sidebar Uploads
st.sidebar.header("📂 Upload Your Data Files")
visits_file = st.sidebar.file_uploader("Upload Visits.csv", type=["csv", "xlsx"])
referrals_file = st.sidebar.file_uploader("Upload Referrals.csv", type=["csv", "xlsx"])
therapists_file = st.sidebar.file_uploader("Upload Therapists.csv", type=["csv", "xlsx"])

def load_file(file):
    if file is None:
        return None
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
        return pd.read_csv(file)

visits = load_file(visits_file)
referrals = load_file(referrals_file)
therapists = load_file(therapists_file)

# When all 3 uploaded
if visits is not None and referrals is not None and therapists is not None:
    st.success("✅ Data uploaded successfully! Scroll down for analytics.")
    
    st.subheader("📊 AI Summary (coming soon)")
    st.info("Your personalized insights will appear here once AI analysis is added.")

    # --- Clinic Overview ---
    st.header("🏥 Clinic Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Visits", len(visits))
    col2.metric("Total Revenue", f"${visits['Revenue'].sum():,.0f}")
    col3.metric("Avg Revenue/Visit", f"${visits['Revenue'].mean():.0f}")

    fig_visits = px.histogram(visits, x="Date", y="Revenue", color="Therapist",
                              barmode="group", title="Revenue by Date and Therapist")
    st.plotly_chart(fig_visits, use_container_width=True)

    # --- Therapist Performance ---
    st.header("💪 Therapist Performance")
    st.dataframe(therapists)

    fig_ther = px.bar(therapists, x="Therapist", y="Revenue_This_Week",
                      color="Therapist", title="Revenue per Therapist")
    st.plotly_chart(fig_ther, use_container_width=True)

    # --- Referral Sources ---
    st.header("🔗 Referral Source Performance")
    st.dataframe(referrals)

    fig_ref = px.bar(referrals, x="Referral_Source", y="Avg_Revenue_Per_Patient",
                     color="Specialty", title="Revenue per Referral Source")
    st.plotly_chart(fig_ref, use_container_width=True)

else:
    st.warning("Please upload all three files (Visits, Referrals, Therapists) to see your dashboard.")
