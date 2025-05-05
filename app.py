import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# SQLite database path
sqlite_db_path = "user_data.db"
TABLE_NAME = "user_table"

# Create table in SQLite from DataFrame
def create_table_from_df(df, table_name):
    with sqlite3.connect(sqlite_db_path) as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)

# Display current data from SQLite
def display_table_data(table_name):
    with sqlite3.connect(sqlite_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=[col[0] for col in cursor.description])

# Retrieve schema and sample data for Gemini prompt
def retrieve_relevant_info(table_name):
    with sqlite3.connect(sqlite_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        schema = cursor.fetchall()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        sample_data = cursor.fetchall()
        return schema, sample_data

# Generate SQL query using Gemini
def generate_sql_query_rag(question, table_name):
    schema, sample_data = retrieve_relevant_info(table_name)
    schema_text = "\n".join([f"{col[1]} (Type: {col[2]})" for col in schema])
    sample_data_text = "\n".join([str(row) for row in sample_data])

    prompt = f"""
Convert the following natural language question into a SQL query using the table schema and sample data provided:

Table Schema:
{schema_text}

Sample Data (first 5 rows):
{sample_data_text}

Natural Language Question: '{question}'

The SQL query should fetch data from the table '{table_name}'.
"""

    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        return sql_query
    except Exception as e:
        return str(e)

# Execute SQL query
def execute_sql_query(query):
    with sqlite3.connect(sqlite_db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            if query.strip().lower().startswith(("insert", "update", "delete", "alter", "drop")):
                conn.commit()
            if not query.strip().lower().startswith(("insert", "update", "delete", "alter", "drop")):
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            st.error(f"Query execution error: {str(e)}")
            return None

# Save DataFrame to Excel
def update_excel_file(df, file_path):
    df.to_excel(file_path, index=False, sheet_name='Sheet1')

# UI starts here
st.title("Ask Your Data: SQL Generator with Gemini")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None and "data_loaded" not in st.session_state:
    df = pd.read_excel(uploaded_file)
    st.write("Preview of Uploaded Data:")
    st.write(df)

    create_table_from_df(df, TABLE_NAME)
    st.session_state["data_loaded"] = True
    st.success("Data has been loaded into the database.")

if "data_loaded" in st.session_state:
    current_data = display_table_data(TABLE_NAME)
    st.write("Current Data in SQLite:")
    st.dataframe(current_data)

    user_question = st.text_input("Ask a question about the data:")

    if st.button("Submit"):
        if user_question:
            sql_query = generate_sql_query_rag(user_question, TABLE_NAME)
            st.write("Generated SQL Query:")
            st.code(sql_query)

            if any(keyword in sql_query.lower() for keyword in ["update", "insert", "delete", "remove", "alter", "drop"]):
                execute_sql_query(sql_query)
                st.success("Database updated successfully.")

                current_data = display_table_data(TABLE_NAME)
                updated_excel_path = f"updated_{uploaded_file.name}"
                update_excel_file(current_data, updated_excel_path)
                st.write("Updated Data:")
                st.dataframe(current_data)

                st.session_state["updated_excel_path"] = updated_excel_path
            else:
                result = execute_sql_query(sql_query)
                if result:
                    st.subheader("Query Result:")
                    st.write(result)
                else:
                    st.warning("No results found.")

    if "updated_excel_path" in st.session_state:
        with open(st.session_state["updated_excel_path"], "rb") as f:
            st.download_button("Download Updated Excel", f, "updated_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
