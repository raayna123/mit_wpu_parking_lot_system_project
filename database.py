'''import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",           # Your MySQL username
        password="your_password", # Your MySQL password
        database="my_project_db"
    )
    return connection'''

import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "parking_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )
    return connection