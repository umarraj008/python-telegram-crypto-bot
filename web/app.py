import os
import json
import docker
import redis
import psycopg2
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

# Flask setup
app = Flask(__name__)

# Docker client
docker_client = docker.from_env()

# PostgreSQL connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "telegram_db")
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port="5432")

# Hardcoded login credentials
USERNAME = "admin"
PASSWORD = "password123"

### ROUTES ###

# Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

# Dashboard: View running containers & status
@app.route('/dashboard')
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    containers = docker_client.containers.list(all=True)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT session_name, telegram_channel, bot_chat FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('dashboard.html', containers=containers, users=users)

# View container logs
@app.route('/logs/<container_id>')
def logs(container_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    container = docker_client.containers.get(container_id)
    logs = container.logs(tail=20).decode()
    return f"<pre>{logs}</pre>"

# Add new user & start a container
@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    data = request.form
    session_name = data["session_name"]
    api_id = data["telegram_api_id"]
    api_hash = data["telegram_api_hash"]
    session_data = data["telegram_session"]
    channel = data["telegram_channel"]
    bot_chat = data["bot_chat"]

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (session_name, telegram_api_id, telegram_api_hash, telegram_session, telegram_channel, bot_chat) VALUES (%s, %s, %s, %s, %s, %s)",
            (session_name, api_id, api_hash, session_data, channel, bot_chat)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Start the new container
        os.system(f"docker run -d --name {session_name} your-client-image")
        return redirect(url_for("dashboard"))

    except Exception as e:
        return str(e), 500

# View stored CAs
@app.route('/coin_addresses')
def get_coin_addresses():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ca, status, created_at FROM coin_addresses ORDER BY created_at DESC")
    records = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("coin_addresses.html", records=records)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# View running containers
# view coins in database
# view users and userchannels in database
# view channels in database
# view last logs in controller (can select num of lines)

# create new container
# delete container
# Stop/start container
# restart container

# add new user to database
# add new coin to database
# add new channel
# add user to channel

# remove user from database 
# remove coin from database
# remove channel
# remove user from channel