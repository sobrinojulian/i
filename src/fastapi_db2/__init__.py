# This file is the entire application.
# When you run the app, FastAPI reads this file to know what endpoints (URLs) exist.

# Import the FastAPI class — this is what creates our web server.
from fastapi import FastAPI

# Import pyodbc — this is the library that lets Python talk to a DB2 database via ODBC.
# ODBC is a standard way for programs to connect to databases, kind of like a universal adapter.
import pyodbc

# Import os so we can read environment variables (like passwords stored outside the code).
import os

from dotenv import load_dotenv

load_dotenv()

# Create the FastAPI "app" object. Think of it as the main container for your web application.
app = FastAPI()


# --------------------------------------------------
# A helper function to connect to the DB2 database.
# We put this in a function so we can reuse it for every request.
# --------------------------------------------------
def get_db_connection():
    """
    Opens a connection to the DB2 database using environment variables.

    Why environment variables?
    - You don't want to hard-code passwords in your source code.
    - Instead, you set them in your shell or a .env file before running the app.

    The connection string tells DB2 where to find the database and how to log in.
    We use the IBM i Access ODBC driver (or any DB2 ODBC driver you have installed).
    """

    # Read each piece of connection info from the environment.
    # If a variable is missing, os.getenv returns None, and the connection will fail with a clear error.
    hostname = os.getenv("DB2_HOSTNAME", "pub400.com")       # e.g. "pub400.com"
    port = os.getenv("DB2_PORT", "446")        # default DB2 port is 446
    user = os.getenv("DB2_USER")               # e.g. "JULI"
    password = os.getenv("DB2_PASSWORD")       # e.g. "mypassword"

    missing = [
        name
        for name, value in (("DB2_USER", user), ("DB2_PASSWORD", password))
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required DB2 settings: {', '.join(missing)}")

    # Build the ODBC connection string — this is one long string that the ODBC driver understands.
    # The driver name "IBM i Access ODBC Driver" is the standard name on Linux for IBM i (AS400).
    # If you get a driver error, check that the IBM i Access ODBC driver is installed.
    # Note: On IBM i, you don't need a database name — you connect directly to the system
    # and access libraries (schemas) in your SQL queries.
    conn_str = (
        f"DRIVER={{IBM i Access ODBC Driver}};"
        f"SYSTEM={hostname};"
        f"UID={user};"
        f"PWD={password};"
        f"PORT={port};"
        f"PROTOCOL=TCPIP"
    )

    # Open the actual connection to the database.
    # pyodbc.connect returns a connection object we use to run queries.
    conn = pyodbc.connect(conn_str)
    return conn


# --------------------------------------------------
# The API endpoint.
# When someone visits http://localhost:8000/data, this function runs.
# --------------------------------------------------
@app.get("/data")
def fetch_data():
    """
    GET /data — fetches rows from a table in DB2 and returns them as JSON.

    Change "YOURSCHEMA.YOURTABLE" below to the real table you want to query.
    The FETCH FIRST 100 ROWS ONLY just means "give me at most 100 rows" so we don't overload the response.
    """

    conn = None  # We'll store the database connection here so we can close it later.

    try:
        # Step 1: Connect to the database.
        conn = get_db_connection()

        # Step 2: Create a cursor.
        # A cursor is like a pointer that lets you run SQL and read the results.
        cursor = conn.cursor()

        # Step 3: Write a SQL query.
        # Replace "JULI1.FCUSTOMER" with your actual library (schema) and table name.
        # On IBM i, libraries are like schemas. Example: "MYSCH.MYTABLE"
        query = "SELECT * FROM JULI1.FCUSTOMER FETCH FIRST 100 ROWS ONLY"

        # Step 4: Execute the query.
        cursor.execute(query)

        # Step 5: Find out what columns the query returned.
        # cursor.description contains info about each column, including the name.
        # This is like asking "what are the column names?" so we can build proper JSON.
        column_names = [desc[0] for desc in cursor.description]

        # Step 6: Fetch all the rows and turn them into a list of dictionaries.
        # Each row becomes a dict like {"COL1": value1, "COL2": value2, ...}
        rows = []
        for row in cursor.fetchall():
            # zip pairs each column name with its value, then dict() turns it into a dictionary.
            rows.append(dict(zip(column_names, row)))

        # Close the cursor when we're done with it.
        cursor.close()

        # Step 7: Return the data. FastAPI automatically converts the Python list to JSON.
        return {
            "table": "JULI1.FCUSTOMER",  # tells the caller which table this came from
            "count": len(rows),           # how many rows were returned
            "columns": column_names,      # the column names
            "rows": rows                  # the actual data
        }

    except Exception as e:
        # If anything goes wrong (bad connection, bad table name, etc.), return a clear error.
        return {
            "error": str(e),
            "hint": "Check that your DB2_* environment variables are set correctly and the ODBC driver is installed."
        }

    finally:
        # Step 8: Always close the connection, even if an error occurred.
        # This prevents "too many connections" errors.
        if conn:
            conn.close()


# --------------------------------------------------
# The main() function is kept for compatibility with the project setup,
# but the real entry point is running: uvicorn src.fastapi_db2:app --reload
# --------------------------------------------------
def main() -> None:
    print("Run this app with: uvicorn src.fastapi_db2:app --reload")
