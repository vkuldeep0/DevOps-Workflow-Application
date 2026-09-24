import psycopg
import os
from flask import Flask, request

app = Flask(__name__)
port = int(os.getenv('APP_PORT', default=5000))

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "devops_db"),
        user=os.getenv("DB_USER", "devops_app"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/users", methods=["POST"])
def create_user():
	data = request.get_json()

	conn=get_db_connection()

	with conn.cursor() as cursor:
		cursor.execute(
			"INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
			(data["name"], data["email"])
		)
		user_id = cursor.fetchone()[0]

	conn.commit()
	conn.close()

	return {"id": user_id, "name": data["name"], "email": data["email"]}, 201



@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email FROM users ORDER BY id")
        users = cursor.fetchall()

    conn.close()

    return {
        "users": [
            {"id": row[0], "name": row[1], "email": row[2]}
            for row in users
        ]
    }

@app.route("/health")
def health():
	return {"status" : "ok"}

@app.route("/")
def home():
	return "Hello From DevOPs!"

@app.route("/db-health")
def db_health():
	conn=get_db_connection()

	with conn.cursor() as cursor:
		cursor.execute("SELECT 1")
		result = cursor.fetchone()

	conn.close()
	return {"database": "ok", "return" : result[0]}

if __name__=="__main__":
	app.run(host="0.0.0.0",port=port)
