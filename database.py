import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()



def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database
    using the DATABASE_URL environment variable.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set!")
    conn = psycopg2.connect(db_url)
    return conn


def fetch_query(query, params=()):
    """
    Executes a SELECT query and returns the results as a list of dictionaries.
    """
    conn = None
    try:
        conn = get_db_connection()
        # Use RealDictCursor to get results as dictionaries
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        # It's good practice to log the error
        print(f"Database fetch error: {e}")
        return None # Or raise the exception
    finally:
        if conn:
            conn.close()




def execute_query(query, params=()):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(query, params)

        # Commit the changes to make them permanent
        conn.commit()

        # Log all SQL execution to the file /log.sql
        with open("log.sql", "a") as f:
            f.write("\n")
            f.write(f"{query}")


        # Get the number of rows affected
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount

    except Exception as e:
        if conn:
            conn.rollback()  # Roll back the transaction on error

    finally:
        if conn:
            conn.close()

def test_connection():

    try:
        conn = get_db_connection()
        conn.close()
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed! {e}")
