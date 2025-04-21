import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime


def run():
    st.title("📊 Dashboard: Insights & Metrics")
    st.markdown("Explore how resumes match jobs, model performance, and trends over time.")

    # === Load Data ===
    data_path = "data/prediction_history.csv"
    if not os.path.exists(data_path):
        st.warning("No prediction history found yet.")
        return

    df = pd.read_csv(data_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # === Summary Metrics ===
    st.subheader("🔢 Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", len(df))
    with col2:
        st.metric("Avg Match Score", f"{df['match_score'].mean():.2f}%")
    with col3:
        st.metric("Top Model", df["model_used"].mode()[0])

    st.markdown("---")

    # === Filters ===
    st.sidebar.header("📂 Filter Data")
    selected_job = st.sidebar.selectbox("Select Job Title", ["All"] + sorted(df["job_title"].unique().tolist()))
    selected_model = st.sidebar.selectbox("Select Model", ["All"] + sorted(df["model_used"].unique().tolist()))

    filtered_df = df.copy()
    if selected_job != "All":
        filtered_df = filtered_df[filtered_df["job_title"] == selected_job]
    if selected_model != "All":
        filtered_df = filtered_df[filtered_df["model_used"] == selected_model]

    # === Match Score Over Time ===
    st.subheader("📈 Match Score Trend")
    trend_fig = px.line(filtered_df.sort_values("timestamp"), x="timestamp", y="match_score", 
                        title="Match Score Over Time", markers=True, color="model_used")
    st.plotly_chart(trend_fig, use_container_width=True)

    # === Model Comparison ===
    st.subheader("⚖️ Model Comparison")
    model_avg = df.groupby("model_used")["match_score"].mean().reset_index()
    bar_fig = px.bar(model_avg, x="model_used", y="match_score", color="model_used",
                     title="Average Match Score by Model")
    st.plotly_chart(bar_fig, use_container_width=True)

    # === Skill Match Pie Chart ===
    st.subheader("🧩 Skills & Fit Breakdown")
    pie_fig = px.pie(filtered_df, values="skill_match", names="model_used", 
                     title="Skill Match Distribution by Model", hole=0.4)
    st.plotly_chart(pie_fig, use_container_width=True)

    # === Top Missing Skills ===
    st.subheader("🚨 Top Missing Skills")
    skill_series = df["missing_skills"].dropna().str.split(", ").explode()
    top_missing_skills = skill_series.value_counts().head(10).reset_index()
    top_missing_skills.columns = ["Skill", "Count"]
    st.dataframe(top_missing_skills, use_container_width=True)

    # === Download Option ===
    st.markdown("---")
    st.download_button("⬇️ Download Full History as CSV", data=df.to_csv(index=False),
                       file_name="prediction_history.csv", mime="text/csv")
