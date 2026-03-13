from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import os

app = FastAPI(title="FastAPI CRUD Application - Containerized")

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '34.57.33.97'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Lucifetarian666!'),
    'database': os.getenv('DB_NAME', 'fastapi_crud')
}

class User(BaseModel):
    name: str
    email: str
    age: int

def get_db_connection():
    try:
        db_host = os.getenv('DB_HOST', '34.57.33.97')
        
        # Check if using Cloud SQL Unix socket
        if db_host.startswith('/cloudsql/'):
            connection = mysql.connector.connect(
                unix_socket=db_host,
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'Lucifetarian666!'),
                database=os.getenv('DB_NAME', 'fastapi_crud')
            )
        else:
            # Regular TCP connection
            connection = mysql.connector.connect(
                host=db_host,
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'Lucifetarian666!'),
                database=os.getenv('DB_NAME', 'fastapi_crud')
            )
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

@app.get("/")
def read_root():
    return {
        "message": "FastAPI CRUD Application",
        "status": "running",
        "version": "2.0-container",
        "environment": "docker"
    }

@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.post("/users")
def create_user(user: User):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)"
        cursor.execute(query, (user.name, user.email, user.age))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {"id": user_id, "message": "User created successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def read_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"users": users, "count": len(users)}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}")
def read_user(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE users SET name = %s, email = %s, age = %s WHERE id = %s"
        cursor.execute(query, (user.name, user.email, user.age, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        cursor.close()
        conn.close()
        return {"message": "User updated successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        cursor.close()
        conn.close()
        return {"message": "User deleted successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
