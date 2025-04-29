import streamlit as st
import psycopg2
import pandas as pd

# --- Configuration ---
st.set_page_config(page_title="Job Market Analytics Dashboard", page_icon="📈", layout="wide")

# --- Database Connection ---
@st.cache_resource
def connect_db():
    conn = psycopg2.connect(
        host=st.secrets["dpg-d081bq7gi27c73822eeg-a"],
        database=st.secrets["job_market_db"],
        user=st.secrets["job_market_db_user"],
        password=st.secrets["8jHGD1A4aQrpmd2G8RFbWiOl2AVVqLsg"],
        port="5432"
    )
    return conn

# Connect
conn = connect_db()

# --- Title and Intro ---
st.title("📊 Job Market Analytics Dashboard")
st.markdown("Welcome! Explore live job market data. See top insights or run your own custom queries!")

# --- Tabs for Navigation ---
tab1, tab2 = st.tabs(["📈 Top Insights", "🛠 Run Your Query"])

# --- Tab 1: Top Insights ---
with tab1:
    st.header("Top Insights from the Job Market Database")

    # Top 5 Highest Paying Jobs
    st.subheader("💰 Top 5 Highest Paying Jobs")
    query_salary = """
    SELECT job_title, salary_range, company_id
    FROM Job_Postings
    ORDER BY CAST(REPLACE(REPLACE(salary_range, 'K', ''), '$', '')::int * 1000) DESC
    LIMIT 5;
    """
    df_salary = pd.read_sql_query(query_salary, conn)
    st.dataframe(df_salary)

    st.divider()

    # Most In-Demand Skills
    st.subheader("🔥 Top 10 Most In-Demand Skills")
    query_skills = """
    SELECT s.skill_name, COUNT(*) AS demand
    FROM Job_Skills js
    JOIN Skills s ON js.skill_id = s.skill_id
    GROUP BY s.skill_name
    ORDER BY demand DESC
    LIMIT 10;
    """
    df_skills = pd.read_sql_query(query_skills, conn)
    st.bar_chart(df_skills.set_index('skill_name'))

    st.divider()

    # Companies with Most Jobs
    st.subheader("🏢 Companies with Most Job Postings")
    query_companies = """
    SELECT c.company_name, COUNT(j.job_id) AS job_post_count
    FROM Companies c
    JOIN Job_Postings j ON c.company_id = j.company_id
    GROUP BY c.company_name
    ORDER BY job_post_count DESC
    LIMIT 10;
    """
    df_companies = pd.read_sql_query(query_companies, conn)
    st.dataframe(df_companies)

# --- Tab 2: Custom Query ---
with tab2:
    st.header("🛠 Run Your Own SELECT Query!")

    user_query = st.text_area("Write your SQL SELECT query below:", height=150)

    if user_query:
        if user_query.strip().lower().startswith("select"):
            try:
                df_user_query = pd.read_sql_query(user_query, conn)
                st.success("✅ Query executed successfully!")
                st.dataframe(df_user_query)
            except Exception as e:
                st.error(f"❌ Error executing query: {e}")
        else:
            st.warning("⚠️ Only SELECT queries are allowed for security.")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + PostgreSQL + Python")

# --- Close Connection ---
conn.close()
