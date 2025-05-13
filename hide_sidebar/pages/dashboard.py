import streamlit as st
import pandas as pd
import plotly.express as px
import os 
from datetime import datetime, time
from config.supabase_config import supabase_client, PREDICTION_HISTORY_TABLE_NAME 
# from config.constants import PREDICTION_HISTORY_CSV

def load_prediction_history_from_supabase() -> pd.DataFrame:
    """Loads prediction history from the Supabase table."""
    if not supabase_client:
        st.error("Supabase client not initialized. Cannot load prediction history.")
        print("Supabase client not initialized in load_prediction_history_from_supabase.")
        return pd.DataFrame()
    try:
        response = supabase_client.table(PREDICTION_HISTORY_TABLE_NAME).select("*").order("timestamp", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Convert timestamp from ISO string to datetime objects
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            # Ensure numeric columns are numeric, handling potential errors
            numeric_cols = ['match_score', 'skill_match_score', 'experience_match_score', 'missing_skills_count']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) # Coerce errors, fill NaN with 0
            return df
        else:
            # print(f"No data in prediction history table or error in response: {response}") 
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading prediction history from Supabase: {e}")
        print(f"Error loading prediction history from Supabase: {e}")
        return pd.DataFrame()

def run():
    st.title("📊 Dashboard: Prediction Insights & Model Comparison")
    st.markdown("Explore how resumes match jobs, compare model performance, and analyze trends over time.")
    st.markdown("---")

    # # === Load Data ===
    # if not os.path.exists(PREDICTION_HISTORY_CSV):
    #     st.warning(f"⚠️ No prediction history found yet. Please analyze some resumes in the Applicant Portal.")
    #     st.caption(f"Expected history file at: {PREDICTION_HISTORY_CSV}")
    #     return

    # try:
    #     df = pd.read_csv(PREDICTION_HISTORY_CSV)
    #     if df.empty:
    #         st.info("Prediction history is currently empty.")
    #         return
    #     df["timestamp"] = pd.to_datetime(df["timestamp"])
    # except Exception as e:
    #     st.error(f"Error loading prediction history: {e}")
    #     return

     # === Load Data from Supabase ===
    df = load_prediction_history_from_supabase()

    if df.empty:
        st.info("Prediction history is currently empty. Analyze some resumes in the Applicant Portal to see data here.")
        return

    # === Sidebar Filters ===
    st.sidebar.header("📂 Filter Data")
    
    # Date Range Filter
    min_date = df["timestamp"].min().date() if not df.empty else datetime.now().date()
    max_date = df["timestamp"].max().date() if not df.empty else datetime.now().date()
    
    
    selected_date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        # format="YYYY-MM-DD" # For Streamlit versions that support it
    )
    
    start_date, end_date = selected_date_range
    # Convert to datetime for comparison, ensuring end_date covers the whole day
    start_datetime = datetime.combine(start_date, time.min) 
    end_datetime = datetime.combine(end_date, time.max) 
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)  # Make timestamp naive

    # Job Title Filter
    job_titles = ["All"] + sorted(df["job_title"].astype(str).unique().tolist())
    selected_job = st.sidebar.selectbox("Select Job Title", job_titles, key="dashboard_job_filter")


    # Model Filter
    model_names = ["All"] + sorted(df["model_used"].astype(str).unique().tolist())
    selected_model_filter = st.sidebar.selectbox("Select Model to Analyze", model_names, key="dashboard_model_filter")


    # Apply filters
    filtered_df = df[
        (df["timestamp"] >= start_datetime) & (df["timestamp"] <= end_datetime)
    ]
    if selected_job != "All":
        filtered_df = filtered_df[filtered_df["job_title"] == selected_job]
    if selected_model_filter != "All":
        filtered_df = filtered_df[filtered_df["model_used"] == selected_model_filter]

    if filtered_df.empty:
        st.warning("No data matches the current filter criteria.")
        return
  
    st.subheader("📈 Overall Performance Metrics")

    # === Key Summary Metrics (Overall for filtered data) ===
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions (Filtered)", len(filtered_df))
    with col2:
        avg_match_score = filtered_df['match_score'].mean()
        st.metric("Avg. Match Score (Filtered)", f"{avg_match_score:.2f}%" if not pd.isna(avg_match_score) else "N/A")
    with col3:
        if not filtered_df.empty and 'model_used' in filtered_df.columns and 'match_score' in filtered_df.columns:
            top_model_series = filtered_df.groupby("model_used")["match_score"].mean()
            if not top_model_series.empty:
                top_model_name = top_model_series.idxmax()
                top_model_score = top_model_series.max()
                st.metric("Top Performing Model (Avg.)", f"{top_model_name} ({top_model_score:.1f}%)")
            else:
                st.metric("Top Performing Model", "N/A")
        else:
            st.metric("Top Performing Model", "N/A")
            
    st.markdown("---")
    st.subheader("🤖 Model Specific Comparison")

    # === Model Performance Summary Table ===
    if 'model_used' in filtered_df.columns and 'match_score' in filtered_df.columns:
        model_summary = filtered_df.groupby("model_used")["match_score"].agg(
            count='count',
            mean_score='mean',
            median_score='median',
            min_score='min',
            max_score='max',
            std_dev='std'
        ).reset_index()
        model_summary = model_summary.sort_values(by="mean_score", ascending=False)
        model_summary['mean_score'] = model_summary['mean_score'].round(2)
        model_summary['median_score'] = model_summary['median_score'].round(2)
        model_summary['std_dev'] = model_summary['std_dev'].round(2)
        
        st.dataframe(
            model_summary,
            column_config={
                "model_used": st.column_config.TextColumn("Model"),
                "count": st.column_config.NumberColumn("Predictions", format="%d"),
                "mean_score": st.column_config.NumberColumn("Avg. Match Score (%)"),
                "median_score": st.column_config.NumberColumn("Median Score (%)"),
                "min_score": st.column_config.NumberColumn("Min Score (%)"),
                "max_score": st.column_config.NumberColumn("Max Score (%)"),
                "std_dev": st.column_config.NumberColumn("Std. Dev (Score)"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Not enough data to generate model performance summary table.")

    # === Average Match Score by Model (Bar Chart) ===
    if not filtered_df.empty and 'model_used' in filtered_df.columns and 'match_score' in filtered_df.columns:
        model_avg_scores = filtered_df.groupby("model_used")["match_score"].mean().reset_index()
        if not model_avg_scores.empty:
            bar_fig_model_avg = px.bar(
                model_avg_scores.sort_values(by="match_score", ascending=False),
                x="model_used",
                y="match_score",
                color="model_used",
                title="Average Match Score by Model",
                labels={"model_used": "Model", "match_score": "Average Match Score (%)"},
                text='match_score' # Display score on bars
            )
            bar_fig_model_avg.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            bar_fig_model_avg.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', showlegend=False)
            st.plotly_chart(bar_fig_model_avg, use_container_width=True)
        else:
            st.info("Not enough data to plot average match scores by model.")
            
    # === Match Score Distribution by Model (Box Plot) ===
    if not filtered_df.empty and 'model_used' in filtered_df.columns and 'match_score' in filtered_df.columns:
        if len(filtered_df["model_used"].unique()) > 0: # Ensure there's at least one model group
            box_fig_score_dist = px.box(
                filtered_df.sort_values(by="model_used"),
                x="model_used",
                y="match_score",
                color="model_used",
                title="Match Score Distribution by Model",
                labels={"model_used": "Model", "match_score": "Match Score (%)"},
                points="outliers" # Show outliers
            )
            box_fig_score_dist.update_layout(showlegend=False)
            st.plotly_chart(box_fig_score_dist, use_container_width=True)
        else:
            st.info("Not enough distinct models in filtered data to plot score distribution.")

    st.markdown("---")
    st.subheader("🕰️ Trends Over Time")
    
    # === Match Score Over Time (Line Chart) ===
    if not filtered_df.empty and 'timestamp' in filtered_df.columns and 'match_score' in filtered_df.columns and 'model_used' in filtered_df.columns:
        # Ensure there's data to plot after filtering
        if len(filtered_df) > 1: # Line chart needs at least 2 points ideally
            trend_fig = px.line(
                filtered_df.sort_values("timestamp"),
                x="timestamp",
                y="match_score",
                color="model_used", # Color lines by model
                title="Match Score Trend Over Time (Filtered)",
                markers=True,
                labels={"timestamp": "Date", "match_score": "Match Score (%)", "model_used": "Model"}
            )
            st.plotly_chart(trend_fig, use_container_width=True)
        elif len(filtered_df) == 1:
            st.info("Only one data point matches filters; line chart for trends requires more data.")
        else:
            st.info("No data to plot match score trend over time for the current filters.")


    st.markdown("---")
    st.subheader("🎯 Skill Analysis (from Rule-Based Component)")

    # === Top Missing Skills (Overall for filtered data) ===
    if 'missing_skills_list' in filtered_df.columns:
        # Explode the comma-separated skills into individual rows
        # Ensure missing_skills_list is treated as string and handle potential NaN/float values
        skills_series = filtered_df["missing_skills_list"].astype(str).str.split(", ").explode().str.strip()
        # Filter out empty strings that might result from empty lists or splitting "nan"
        skills_series = skills_series[skills_series != "" ]
        
        if not skills_series.empty:
            top_missing_skills = skills_series.value_counts().head(10).reset_index()
            top_missing_skills.columns = ["Skill", "Frequency"]
            
            st.write("Top 10 Most Frequently Missing Skills (across all models in filtered data):")
            st.dataframe(top_missing_skills, use_container_width=True, hide_index=True)
        else:
            st.info("No missing skills data to display for the current filters.")
    else:
        st.info("'missing_skills_list' column not found in history.")

    # === Download Option ===
    st.markdown("---")
    if not df.empty: # Offer download of the original, unfiltered dataframe
        csv_export = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Full Prediction History (CSV)",
            data=csv_export,
            file_name="full_prediction_history.csv",
            mime="text/csv",
        )
