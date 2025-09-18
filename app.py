from flask import Flask, render_template, redirect, request, session
from flask_bcrypt import Bcrypt
import mysql.connector

app = Flask(__name__)
app.secret_key = "123"
bcrypt = Bcrypt(app)

conn = mysql.connector.connect(
    host = "172.31.128.1",
    port=3306,
    user = "root",
    password = "pass",
    database = "db1",
    autocommit = True
)

def register_session(username, id):
    session["username"] = username
    session["id"] = id

@app.route("/")
def home() :
    if "username" not in session :
        return redirect("/login")
    
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY creation_date ASC", (session["id"],))
    res = cur.fetchall()
    
    return render_template("home.html", name=session["username"], tasks=res)

@app.route("/login", methods=["GET", "POST"])
def login() :
    if request.method == "GET" :
        return render_template("login.html")
    
    cur = conn.cursor(dictionary=True)
    
    username = request.form.get("username")
    passwd = request.form.get("password")
    
    cur.execute("SELECT id, passwd, username FROM users WHERE LOWER(username) = LOWER(%s) OR LOWER(email) = LOWER(%s)", (username, username))
    res = cur.fetchone()
    
    if res and bcrypt.check_password_hash(res["passwd"], passwd):
            register_session(res["username"], res["id"])
            return redirect("/")
        
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup() :
    if request.method == "GET" :
        return render_template("signup.html")
    
    cur = conn.cursor(dictionary=True)
    
    username = request.form.get("username")
    passwd = request.form.get("password")
    email = request.form.get("email")
    
    cur.execute("SELECT passwd FROM users WHERE LOWER(username) = LOWER(%s) OR LOWER(email) = LOWER(%s)", (username, email))
    res = cur.fetchone()
    
    if res:
        return redirect("/login")
    
    passwd_bcrypt = bcrypt.generate_password_hash(passwd).decode("utf-8")
    cur.execute("INSERT INTO users(username, passwd, email) VALUES(%s, %s, %s)", (username, passwd_bcrypt, email))
    return redirect("/login")

@app.route("/logout")
def logout() :
    session.clear()
    return redirect("/login")

@app.route("/delete-acc")
def delete_acc() :
    if "id" not in session or "username" not in session :
        return redirect("/login")
    
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id = %s", (session["id"],))
    res = cur.fetchone()
    
    if not res :
        return redirect("/login")
    
    cur.execute("DELETE FROM users WHERE id = %s", (session["id"],))
    return redirect("/login")

@app.route("/task-add", methods=["GET", "POST"])
def task_add() :
    if "username" not in session :
        return redirect("/login")
    
    if request.method == "GET" :
        return render_template("task_add.html")
    
    title = request.form.get("title")
    due_date = request.form.get("due_date")
    
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tasks WHERE title = %s AND user_id = %s", (title, session["id"]))
    res = cur.fetchone()
    
    if res :
        return render_template("task_add.html")
    
    if not due_date :
        cur.execute("INSERT INTO tasks(user_id, title) VALUES(%s, %s)", (session["id"], title))
    else :
        cur.execute("INSERT INTO tasks(user_id, title, due_date) VALUES(%s, %s, %s)", (session["id"], title, due_date))
        
    return redirect("/")

@app.route("/complete-task/<int:task_id>", methods=["POST"])
def complete_task(task_id) :
    if "id" not in session :
        return redirect("/login")
    
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, session["id"]))
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
