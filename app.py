import streamlit as st
import psycopg2
import pandas as pd

# --- Configuration ---
st.set_page_config(page_title="Job Market Analytics Dashboard", page_icon="📈", layout="wide")

# --- Database Connection Management ---

@st.cache_resource
def connect_db():
    return psycopg2.connect(
        host=st.secrets["db_host"],
        database=st.secrets["db_name"],
        user=st.secrets["db_user"],
        password=st.secrets["db_password"],
        port="5432"
    )

def get_connection():
    """Always get a fresh live connection."""
    try:
        conn = connect_db()
    except Exception:
        conn = connect_db()
    return conn

# --- Title and Introduction ---
st.title("📊 Job Market Analytics Dashboard")
st.markdown("Explore real-time insights into the job market. View analytics or run your own SQL queries!")

# --- Tabs for Navigation ---
tab1, tab2 = st.tabs(["📈 Top Insights", "🛠 Run Your Query"])

# --- Tab 1: Top Insights ---
with tab1:
    st.header("Top Insights from the Job Market Database")

    # Top 5 Highest Paying Jobs
    st.subheader("💰 Top 5 Highest Paying Jobs")
    conn = get_connection()
    query_salary = """
    SELECT job_title, salary_range, company_id
    FROM Job_Postings
    WHERE salary_range LIKE '$%' AND salary_range LIKE '%K'
    ORDER BY CAST(REPLACE(REPLACE(salary_range, 'K', ''), '$', '') AS INTEGER) DESC
    LIMIT 5;
    """
    df_salary = pd.read_sql_query(query_salary, conn)
    st.dataframe(df_salary)

    st.divider()

    # Most In-Demand Skills
    st.subheader("🔥 Top 10 Most In-Demand Skills")
    conn = get_connection()
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
    conn = get_connection()
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
                conn = get_connection()
                df_user_query = pd.read_sql_query(user_query, conn)
                st.success("✅ Query executed successfully!")
                st.dataframe(df_user_query)
            except Exception as e:
                st.error(f"❌ Error executing query: {e}")
        else:
            st.warning("⚠️ Only SELECT queries are allowed for security reasons.")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + PostgreSQL + Python")

