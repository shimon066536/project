from flask import Flask, g, render_template, request, redirect, url_for, session
import socket
import chatlib

# הגדרת אפליקציית Flask
app = Flask(__name__)
print("app = ", app)
app.secret_key = 'your_secret_key'

SERVER_IP = "localhost"
SERVER_PORT = 8856

@app.before_request
def before_request():
    """לפני כל בקשה ניצור חיבור לשרת"""
    print("Executing before_request")
    g.conn = connect()
    print(f"g.conn = {g.conn}")

def connect():
    """יצירת חיבור לשרת"""
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect((SERVER_IP, SERVER_PORT))
        print('Connected to server:', my_socket.getsockname())
        return my_socket
    except ConnectionRefusedError:
        print(f"Error: Unable to connect to the server at {SERVER_IP}:{SERVER_PORT}")
        exit(1)

@app.route("/", methods=["GET", "POST"])
def login():
    """נתיב דף התחברות"""
    print("Accessing login route")
    conn = g.conn
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        if not user or not password:
            return "Missing username or password", 400
        username_password = "#".join((user, password))
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], username_password)
        msg_code, data = recv_message_and_parse(conn)
        if msg_code == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            session["username"] = user
            return redirect(url_for("dashboard"))  # נתיב עתידי לדף משחק
        else:
            return "Login failed: " + data
    return render_template("login.html")

# דוגמה לנתיב נוסף
@app.route("/dashboard")
def dashboard():
    # return "Welcome to the dashboard!"
    return redirect(url_for("play"))

# פונקציות עזר
def build_and_send_message(conn, code, data=''):
    msg = chatlib.build_message(code, data)
    conn.send(msg.encode())

def recv_message_and_parse(conn):
    message = conn.recv(1024).decode()
    return chatlib.parse_message(message)

# כניסה דרך 'main' רק בהרצה ישירה
if __name__ == "__main__":
    print("Running directly")
    app.run(debug=True)
