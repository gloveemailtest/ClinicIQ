import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ClinicIQ", layout="wide")

st.title("💡 ClinicIQ – AI Dashboard for PT Clinics")

st.sidebar.header("📂 Upload Clinic Data")
visits_file = st.sidebar.file_uploader("Upload Visits.csv", type="csv")
referrals_file = st.sidebar.file_uploader("Upload Referrals.csv", type="csv")
therapists_file = st.sidebar.file_uploader("Upload Therapists.csv", type="csv")

if visits_file and referrals_file and therapists_file:
    visits = pd.read_csv(visits_file)
    referrals = pd.read_csv(referrals_file)
    therapists = pd.read_csv(therapists_file)

    st.subheader("📊 AI Summary (coming soon)")
    st.info("AI insights will appear here once GPT integration is added.")

    st.header("🏥 Clinic Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Visits", len(visits))
    col2.metric("Total Revenue", f"${visits['Revenue'].sum():,.0f}")
    col3.metric("Avg Revenue/Visit", f"${visits['Revenue'].mean():.0f}")

    fig_visits = px.histogram(visits, x="Date", y="Revenue", color="Therapist", barmode="group", title="Revenue by Date and Therapist")
    st.plotly_chart(fig_visits, use_container_width=True)

    st.header("💪 Therapist Performance")
    st.dataframe(therapists)
    fig_ther = px.bar(therapists, x="Therapist", y="Revenue_This_Week", color="Therapist", title="Revenue per Therapist")
    st.plotly_chart(fig_ther, use_container_width=True)

    st.header("🔗 Referral Source Performance")
    st.dataframe(referrals)
    fig_ref = px.bar(referrals, x="Referral_Source", y="Avg_Revenue_Per_Patient", color="Specialty", title="Revenue per Referral Source")
    st.plotly_chart(fig_ref, use_container_width=True)
else:
    st.warning("Please upload all three CSV files to see the dashboard.")
