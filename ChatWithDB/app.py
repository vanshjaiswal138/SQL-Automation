import streamlit as st
import os
from dotenv import load_dotenv
from main import Database, SQLTranslator
import pandas as pd
import io

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="MySQL Automation Tool",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>div>div>input {
        border-radius: 4px;
    }
    .stSelectbox>div>div>select {
        border-radius: 4px;
    }
    .download-button {
        background-color: #2196F3 !important;
    }
    .download-button:hover {
        background-color: #1976D2 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()
if 'translator' not in st.session_state:
    st.session_state.translator = SQLTranslator()
if 'current_db' not in st.session_state:
    st.session_state.current_db = st.session_state.db.get_current_database()
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# Helper function to create download button
def create_download_button(df, filename):
    if df is not None and not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=filename,
            mime="text/csv",
            key=f"download_{filename}",
            help="Click to download the results as a CSV file"
        )

# Sidebar
with st.sidebar:
    st.title("🗄️ MySQL Automation")
    st.markdown("---")
    
    # Database selection
    st.subheader("Database Selection")
    databases = st.session_state.db.list_databases()
    if databases:
        selected_db = st.selectbox(
            "Select Database",
            databases,
            index=databases.index(st.session_state.current_db) if st.session_state.current_db in databases else 0
        )
        
        if selected_db != st.session_state.current_db:
            if st.session_state.db.switch_database(selected_db):
                st.session_state.current_db = selected_db
                # Update schema for the new database
                schema = st.session_state.db.get_schema()
                if schema:
                    st.session_state.translator = SQLTranslator()  # Reset translator
                    for table, columns in schema.items():
                        st.session_state.translator.update_schema(table, columns)
                    st.success(f"Switched to database: {selected_db}")
                    st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                else:
                    st.error("No tables found in the selected database. Please create some tables first.")
            else:
                st.error("Failed to switch to the selected database. Please check if the database exists and you have proper permissions.")
    else:
        st.warning("No databases available")
    
    st.markdown("---")
    
    # Schema information
    st.subheader("Current Schema")
    schema = st.session_state.db.get_schema()
    if schema:
        for table, columns in schema.items():
            with st.expander(f"📊 {table}"):
                for column in columns:
                    st.write(f"• {column}")
    else:
        st.info("No tables in the current database")

# Main content
st.title("MySQL Automation Tool")
st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["SQL Query", "Natural Language", "Test Data"])

# SQL Query Tab
with tab1:
    st.subheader("Execute SQL Query")
    query = st.text_area("Enter your SQL query:", height=100)
    if st.button("Execute Query"):
        if query:
            result = st.session_state.db.execute_query(query)
            if isinstance(result, list):
                df = pd.DataFrame(result)
                st.session_state.last_result = df
                st.dataframe(df, use_container_width=True)
                create_download_button(df, f"query_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv")
            else:
                st.write(result)
        else:
            st.warning("Please enter a SQL query")

# Natural Language Tab
with tab2:
    st.subheader("Convert Natural Language to SQL")
    nl_query = st.text_area("Enter your request in natural language:", height=100)
    if st.button("Convert to SQL"):
        if nl_query:
            sql_query = st.session_state.translator.translate(nl_query)
            st.code(sql_query, language="sql")
            
            if not sql_query.startswith("Error:"):
                if st.button("Execute Generated SQL"):
                    result = st.session_state.db.execute_query(sql_query)
                    if isinstance(result, list):
                        df = pd.DataFrame(result)
                        st.session_state.last_result = df
                        st.dataframe(df, use_container_width=True)
                        create_download_button(df, f"nl_query_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv")
                    else:
                        st.write(result)
        else:
            st.warning("Please enter a natural language query")

# Test Data Tab
with tab3:
    st.subheader("Add Test Data")
    if st.button("Add Sample Users"):
        st.session_state.db.execute_query("INSERT INTO USERS (name) VALUES ('Vansh')")
        st.session_state.db.execute_query("INSERT INTO USERS (name) VALUES ('Anuj')")
        st.session_state.db.execute_query("INSERT INTO USERS (name) VALUES ('Arihant')")
        st.success("Test data added successfully!")
        
        # Show current users
        result = st.session_state.db.execute_query("SELECT * FROM USERS")
        if isinstance(result, list):
            df = pd.DataFrame(result)
            st.session_state.last_result = df
            st.dataframe(df, use_container_width=True)
            create_download_button(df, "users_data.csv")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Vansh Jaiswal") 