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


# Function to generate SQL using Gemini AI with detailed schema understanding and restrictions
def get_gemini_response(query):
    if not isinstance(query, str) or len(query.strip()) == 0:
        return "I cannot understand your request. Please provide a valid query."

    # Detailed schema explanation
    schema_explanation = """
    The database contains the following tables and relationships:

    1. **users**: This table stores information about each user in the system.
        - Columns:
            - id: Primary key (user ID)
            - manager_id: Foreign key referencing another user who is the manager of this user.
            - first_name, last_name: Name of the user.
            - designation: Job title of the user (e.g., Developer, Manager, etc.).
            - email, phone: Unique contact information for the user.
            - password: User's password (hashed).
            - role: Role of the user (e.g., employee, manager, HR).
            - country: User's country (e.g., Pakistan, UAE, UK).
            - fcm_token: Token for push notifications (optional).
            - image: URL to the user's profile image (optional).
            - created_at, updated_at: Timestamps for record creation and update.

    2. **leaves_balances**: Tracks the leave balance for each user.
        - Columns:
            - id: Primary key.
            - sick_available, casual_available, wfh_available: Available balance for sick, casual, and work-from-home leaves.
            - sick_taken, casual_taken, wfh_taken: Leaves already taken for each category.
            - user_id: Foreign key linking to the user who owns the leave balance.
            - created_at, updated_at: Timestamps for record creation and update.

    3. **leaves**: Records each leave request submitted by users.
        - Columns:
            - id: Primary key.
            - user_id: Foreign key linking to the user who submitted the leave.
            - manager_id: Foreign key linking to the manager who approves the leave.
            - username: The username of the employee.
            - type: The type of leave (sick, casual, work-from-home).
            - from_date, to_date: The start and end dates of the leave.
            - comments: Any comments related to the leave.
            - status: The status of the leave request (pending, approved, or rejected).
            - created_at, updated_at: Timestamps for record creation and update.

    4. **user_otps**: Stores one-time passwords (OTPs) for users, used for authentication purposes.
        - Columns:
            - id: Primary key.
            - user_id: Foreign key linking to the user for whom the OTP was generated.
            - otp: The OTP code.
            - otp_expiry: Expiration time for the OTP.
            - created_at: Timestamp for OTP creation.

    **Relationships**:
    - The `users` table has a self-referential relationship via the `manager_id`, where a manager is also a user.
    - The `leaves` table links both users and managers through `user_id` and `manager_id`.
    - The `leaves_balances` table links each leave balance record to a user via `user_id`.
    - The `user_otps` table links OTPs to users via `user_id`.
    """

    # Prompt with detailed schema explanation
    prompt = f"""
    ### Task
    You are a SQL expert. Given the following PostgreSQL database schema and its detailed explanation, your task is to generate an accurate SQL query based on the user's question. 
    If the query is irrelevant to the schema, respond with "Sorry, your question is not related to this database."

    ### PostgreSQL Database Schema:
    {schema}

    ### Schema Explanation:
    {schema_explanation}

    ### User Query:
    {query}

    ### Answer
    Based on the schema and the explanation provided, here is the SQL query for the user's request. If the query is irrelevant, respond with: "Sorry, your question is not related to this database."
    """

    try:
        # Use the Google Gemini model to generate the SQL query
        model = genAI.GenerativeModel('gemini-1.5-flash-8b')
        response = model.generate_content([prompt])

        # Clean up the response by removing extra formatting
        result = response.text.strip()
        result = result.replace("```sql", "").replace("```", "").strip()
        
        # Check if the model indicates the question is irrelevant
        if "Sorry, your question is not related to this database." in result:
            return "Sorry your question is not related to any use case"
        
        return result
    except Exception as e:
        return f"An error occurred: {str(e)}"