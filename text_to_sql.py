import os
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genAI

# Load environment variables from the .env file
load_dotenv()

# Fetch API key from .env file
API_KEY = os.getenv("api_key")

# Configure Google Gemini API with the provided key
genAI.configure(api_key=API_KEY)

# Define your PostgreSQL schema
schema = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    manager_id INTEGER,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(50) NOT NULL, -- employee, manager, hr
    country VARCHAR(50) NOT NULL, -- pakistan, uae, uk
    fcm_token VARCHAR(255),
    image VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leaves_balances (
    id SERIAL PRIMARY KEY,
    sick_available FLOAT NOT NULL,
    casual_available FLOAT NOT NULL,
    wfh_available FLOAT NOT NULL,
    sick_taken FLOAT NOT NULL,
    casual_taken FLOAT NOT NULL,
    wfh_taken FLOAT NOT NULL,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leaves (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    manager_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- sick, casual, wfh
    from_date TIMESTAMP NOT NULL,
    to_date TIMESTAMP NOT NULL,
    comments TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_otps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    otp INTEGER NOT NULL,
    otp_expiry TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


# Function to generate SQL using Gemini AI
def get_gemini_response(question):
    prompt = f"""
    ### Task

    Generate a SQL query to answer the following question: {question}

    ### PostgreSQL Database Schema
    The query will run on a database with the following schema:
    {schema}

    ### Answer
    Here is the SQL query that answers the question: {question}
    sql
    """

    # Use the Google Gemini model to generate the SQL query
    model = genAI.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    return response.text.strip()

response = get_gemini_response("delete all users")
print(response)