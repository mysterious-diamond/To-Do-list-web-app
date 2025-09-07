from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)
conn = mysql.connector.connect(
    host = "172.29.208.1",
    user = "root",
    password = "pass",
    database = "db1"
)

@app.route("/")
def home() :
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'Aaron'")
    results = cursor.fetchone()
    return render_template("login.html", res=results)

if __name__ == "__main__":
    app.run(debug=True)

