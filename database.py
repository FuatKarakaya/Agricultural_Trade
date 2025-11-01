import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

connection = psycopg2.connect(DATABASE_URL, sslmode="require")

cur = connection.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())

cur.close()
connection.close()

