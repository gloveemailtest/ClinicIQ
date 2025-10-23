import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ClinicIQ", layout="wide")

st.title("💡 ClinicIQ – AI Dashboard for PT Clinics")
st.write("Upload your clinic’s exported data below to see instant insights. \
Supported formats: CSV or Excel files.")

st.sidebar.header("📂 Upload Your Data Files")
visits_file = st.sidebar.file_uploader("Upload Visits.csv", type=["csv", "xlsx"])
referrals_file = st.sidebar.file_uploader("Upload Referrals.csv", type=["csv", "xlsx"])
therapists_file = st.sidebar.file_uploader("Upload Therapists.csv", type=["csv", "xlsx"])

def load_file(file):
    if file is None:
        return None
    if file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)
    # Clean column names: remove spaces, lowercase, replace symbols
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

visits = load_file(visits_file)
referrals = load_file(referrals_file)
therapists = load_file(therapists_file)

# When all uploaded
if visits is not None and referrals is not None and therapists is not None:
    st.success("✅ Data uploaded successfully! Scroll down for analytics.")
    
    st.subheader("📊 AI Summary (coming soon)")
    st.info("Your personalized insights will appear here once AI analysis is added.")

    # --- Clinic Overview ---
    st.header("🏥 Clinic Overview")

    # Check required columns before using them
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
        fig_visits = px.histogram(
            visits, x="date", y="revenue", color="therapist",
            barmode="group", title="Revenue by Date and Therapist"
        )
        st.plotly_chart(fig_visits, use_container_width=True)
    else:
        st.warning("Could not plot visits — please include 'Date' and 'Therapist' columns.")

    # --- Therapist Performance ---
    st.header("💪 Therapist Performance")
    st.dataframe(therapists)

    if "therapist" in therapists.columns and "revenue_this_week" in therapists.columns:
        fig_ther = px.bar(
            therapists, x="therapist", y="revenue_this_week", color="therapist",
            title="Revenue per Therapist"
        )
        st.plotly_chart(fig_ther, use_container_width=True)

    # --- Referral Sources ---
    st.header("🔗 Referral Source Performance")
    st.dataframe(referrals)

    if "referral_source" in referrals.columns and "avg_revenue_per_patient" in referrals.columns:
        fig_ref = px.bar(
            referrals, x="referral_source", y="avg_revenue_per_patient",
            color="specialty", title="Revenue per Referral Source"
        )
        st.plotly_chart(fig_ref, use_container_width=True)

else:
    st.warning("Please upload all three files (Visits, Referrals, Therapists) to see your dashboard.")

