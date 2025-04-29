import streamlit as st
import psycopg2
import pandas as pd

# --- Streamlit Config ---
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
    """Get a fresh DB connection."""
    try:
        conn = connect_db()
    except Exception:
        conn = connect_db()
    return conn

# --- Predefined Queries ---
queries = {
    "Top 5 Highest Paying Jobs": """
        SELECT job_title, salary_range, company_id
        FROM Job_Postings
        WHERE salary_range LIKE '$%' AND salary_range LIKE '%K'
        ORDER BY CAST(REPLACE(REPLACE(salary_range, 'K', ''), '$', '') AS INTEGER) DESC
        LIMIT 5;
    """,
    "Top 10 Most In-Demand Skills": """
        SELECT s.skill_name, COUNT(*) AS demand
        FROM Job_Skills js
        JOIN Skills s ON js.skill_id = s.skill_id
        GROUP BY s.skill_name
        ORDER BY demand DESC
        LIMIT 10;
    """,
    "Companies with Most Job Postings": """
        SELECT c.company_name, COUNT(j.job_id) AS job_post_count
        FROM Companies c
        JOIN Job_Postings j ON c.company_id = j.company_id
        GROUP BY c.company_name
        ORDER BY job_post_count DESC
        LIMIT 10;
    """,
    "Locations with Most Applicants": """
        SELECT l.city, COUNT(a.applicant_id) AS applicant_count
        FROM Applicants a
        JOIN Locations l ON a.location_id = l.location_id
        GROUP BY l.city
        ORDER BY applicant_count DESC
        LIMIT 10;
    """,
    "Skills Required by Most Jobs": """
        SELECT s.skill_name, COUNT(js.job_id) AS job_count
        FROM Skills s
        JOIN Job_Skills js ON s.skill_id = js.skill_id
        GROUP BY s.skill_name
        ORDER BY job_count DESC
        LIMIT 10;
    """,
    "Jobs Requiring >5 Years Experience": """
        SELECT job_title, experience_required
        FROM Job_Postings
        WHERE experience_required > 5;
    """,
    "Applicants with >5 Years Experience": """
        SELECT name, experience_years
        FROM Applicants
        WHERE experience_years > 5;
    """,
    "Applications Pending Status": """
        SELECT applicant_id, job_id, application_date
        FROM Applications
        WHERE status = 'Pending';
    """,
    "Job Count by Employment Type": """
        SELECT employment_type, COUNT(*) AS count
        FROM Job_Postings
        GROUP BY employment_type
        ORDER BY count DESC;
    """,
    "Application Count per Job": """
        SELECT job_id, COUNT(application_id) AS total_applications
        FROM Applications
        GROUP BY job_id
        ORDER BY total_applications DESC
        LIMIT 10;
    """
}

# --- Title and Intro ---
st.title("📊 Job Market Analytics Dashboard")
st.markdown("Explore predefined insights or run your own custom SQL queries!")

# --- Tabs for Navigation ---
tab1, tab2 = st.tabs(["📈 Predefined Queries", "🛠 Custom Query"])

# --- Tab 1: Predefined Insights ---
with tab1:
    st.header("📚 Explore Ready Insights")

    selected_query = st.selectbox("Choose an analysis to view:", list(queries.keys()))

    if selected_query:
        st.subheader(f"🔎 Result: {selected_query}")
        sql_query = queries[selected_query]

        try:
            conn = get_connection()
            df_result = pd.read_sql_query(sql_query, conn)
            st.dataframe(df_result)
        except Exception as e:
            st.error(f"❌ Query failed: {e}")

# --- Tab 2: Custom Query ---
with tab2:
    st.header("🛠 Run Your Own SELECT Query!")

    user_query = st.text_area("Write your SQL SELECT query here:", height=150)

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