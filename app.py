from flask import Flask, render_template, redirect, request, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "123"
conn = mysql.connector.connect(
    host = "172.29.208.1",
    user = "root",
    password = "pass",
    database = "db1",
    autocommit = True
)

@app.route("/")
def home() :
    if "username" not in session :
        return redirect("/login")
    
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login() :
    if request.method == "GET" :
        return render_template("login.html")
    
    cur = conn.cursor(dictionary=True)
    
    username = request.form.get("username")
    passwd = request.form.get("password")
    
    cur.execute("SELECT id, passwd FROM users WHERE username = %s", (username,))
    res = cur.fetchone()
    
    if res and passwd == res["passwd"]:
        session["username"] = username
        session["id"] = res["id"]
        return redirect("/")
        
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup() :
    if request.method == "GET" :
        return render_template("signup.html")
    
    cur = conn.cursor()
    
    username = request.form.get("username")
    passwd = request.form.get("password")
    email = request.form.get("email")
    
    cur.execute("SELECT passwd FROM users WHERE username = %s", (username,))
    res = cur.fetchone()
    
    if res:
        return redirect("/login")
    
    cur.execute("INSERT INTO users(username, passwd, email) VALUES(%s, %s, %s)", (username, passwd, email))
    return redirect("/login")

@app.route("/logout")
def logout() :
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)

