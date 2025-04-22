import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
from services.job_service import load_jobs


def run():

    # Load job dataset
    df = load_jobs()

    # Clean Job Descriptions
    df['Job Description'] = df['Job Description'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    st.title("📈 Data Visualization Dashboard")
    st.markdown("---")

    # -- Data Overview ---
    st.subheader("🔍 Dataset Overview")
    st.write("This dataset contains job postings from various companies. Below is a preview of the data:")
    st.dataframe(df)
    st.markdown("---")

    # --- Job Title Distribution Pie Chart ---
    st.subheader("🔹 Job Title Distribution (Pie Chart)")
    job_counts = df['Job Title'].value_counts()
    fig1 = px.pie(values=job_counts.values, names=job_counts.index, title='Job Title Distribution')
    st.plotly_chart(fig1)

    # --- Countplot for Job Title ---
    st.subheader("🔹 Job Title Frequency")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df, y='Job Title', order=df['Job Title'].value_counts().index, ax=ax2)
    ax2.set_title("Job Title Count")
    st.pyplot(fig2)

    # --- Location Normalization ---
    df = df.dropna(subset=['Job Title', 'Location'])
    df['Location'] = df['Location'].apply(lambda x: x.split(', ')[-1])

    # --- Job Title by Country ---
    st.subheader("🔹 Country vs Job Title Distribution")
    fig3 = px.histogram(df, x='Location', color='Job Title', barmode='group', title='Country - Job Title Distribution')
    st.plotly_chart(fig3)

    # --- Employment Mode Distribution ---
    st.subheader("🔹 Employment Mode Distribution")
    employment_counts = df['Employment Mode'].value_counts()
    fig4 = px.pie(values=employment_counts.values, names=employment_counts.index, title='Employment Mode Distribution')
    st.plotly_chart(fig4)

    # --- Job Title by Employment Mode ---
    st.subheader("🔹 Job Title vs Employment Mode")
    fig5 = px.histogram(df, x='Job Title', color='Employment Mode', barmode='group')
    fig5.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig5)

    # --- Location vs Employment Mode ---
    df_location_emp = df.dropna(subset=['Location', 'Employment Mode'])
    df_location_emp['Location'] = df_location_emp['Location'].apply(lambda x: x.split(', ')[-1])
    st.subheader("🔹 Country vs Employment Mode")
    fig6 = px.histogram(df_location_emp, x='Location', color='Employment Mode', barmode='group')
    fig6.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig6)

    # --- WordCloud of Skills ---
    st.subheader("🔹 WordCloud of Required Skills")
    skills = df['Skills Required'].dropna().str.split(', ').sum()
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(skills))
    fig7, ax7 = plt.subplots(figsize=(10, 5))
    ax7.imshow(wordcloud, interpolation='bilinear')
    ax7.axis('off')
    ax7.set_title("WordCloud of Required Skills")
    st.pyplot(fig7)

    # --- Salary Extraction for Scatter Plots ---
    df = df.dropna(subset=['Salary Range'])
    df['Salary Extracted'] = df['Salary Range'].apply(lambda x: float((str(x).split('k - $')[0]).split('$')[-1]) if isinstance(x, str) and '$' in x else None)

    # --- Scatter: Job Title vs Salary vs Experience Level ---
    df_exp = df.dropna(subset=['Experience Level'])
    st.subheader("🔹 Salary vs Experience Level per Job Title")
    fig8 = px.scatter(df_exp, x='Salary Extracted', y='Experience Level', color='Job Title', size_max=55)
    st.plotly_chart(fig8)

    # --- Scatter: Job Title vs Salary vs Employment Mode ---
    df_emp = df.dropna(subset=['Employment Mode'])
    st.subheader("🔹 Salary vs Employment Mode per Job Title")
    fig9 = px.scatter(df_emp, x='Salary Extracted', y='Employment Mode', color='Job Title', size_max=55)
    st.plotly_chart(fig9)

    # --- New: Experience Level Distribution ---
    st.subheader("🔹 Experience Level Distribution")
    fig10 = px.histogram(df, x='Experience Level', color='Job Title', barmode='group')
    st.plotly_chart(fig10)

    # --- Geospatial Visualization ---
    st.subheader("🔹 Geospatial Distribution of Jobs")
    geo_df = df[['Location']].dropna()
    country_counts = geo_df['Location'].value_counts().reset_index()
    country_counts.columns = ['country', 'job_count']

    # print(country_counts['country'].unique())


    try:
        fig13 = px.choropleth(country_counts,locations='country',locationmode='country names',
                              color='job_count', color_continuous_scale='Plasma',
                              title='Jobs per Country (Approximate)')
        fig13.update_geos(projection_type="natural earth")
        fig13.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig13.update_geos(showcoastlines=True, coastlinecolor="Black")

        st.plotly_chart(fig13)
    except Exception as e:
        st.warning(f"Could not plot map due to: {e}")

    st.markdown("---")
    st.caption("📊 All visualizations are based on the job dataset loaded dynamically.")
