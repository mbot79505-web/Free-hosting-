from flask import Flask, request, redirect, session, jsonify
import subprocess, os, json, hashlib

app = Flask(__name__)
app.secret_key = "supersecretkey123"

USERS_FILE = "/data/users.json"
os.makedirs("/data", exist_ok=True)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ✅ Register endpoint
@app.route("/new")
def register():
    username = request.args.get("acc")
    password = request.args.get("password")

    if not username or not password:
        return jsonify({"error": "acc aur password dono do"}), 400

    users = load_users()
    if username in users:
        return jsonify({"error": "User already exists"}), 400

    # User ka alag folder banao
    user_home = f"/home/{username}"
    os.makedirs(user_home, exist_ok=True)

    users[username] = {
        "password": hash_pass(password),
        "home": user_home,
        "port": 8100 + len(users)  # har user ka alag port
    }
    save_users(users)

    return jsonify({"success": f"User {username} registered!", "home": user_home})

# ✅ Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()

        if username in users and users[username]["password"] == hash_pass(password):
            session["user"] = username
            return redirect(f"/lab/{username}")
        return "Wrong username or password", 401

    return '''
    <html>
    <body style="background:#1a1a2e; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; font-family:sans-serif;">
    <div style="background:#16213e; padding:40px; border-radius:12px; color:white; min-width:300px;">
        <h2 style="text-align:center; margin-bottom:24px;">🔐 JupyterLab Login</h2>
        <form method="POST">
            <input name="username" placeholder="Username" required
                style="width:100%; padding:10px; margin-bottom:12px; border-radius:6px; border:none; box-sizing:border-box;"><br>
            <input name="password" type="password" placeholder="Password" required
                style="width:100%; padding:10px; margin-bottom:16px; border-radius:6px; border:none; box-sizing:border-box;"><br>
            <button type="submit"
                style="width:100%; padding:10px; background:#0f3460; color:white; border:none; border-radius:6px; cursor:pointer; font-size:16px;">
                Login
            </button>
        </form>
    </div>
    </body>
    </html>
    '''

# ✅ User ka Jupyter launch karo
@app.route("/lab/<username>")
def launch_lab(username):
    if session.get("user") != username:
        return redirect("/")

    users = load_users()
    if username not in users:
        return "User not found", 404

    user_home = users[username]["home"]
    port = users[username]["port"]

    # Jupyter already chal raha hai?
    check = subprocess.run(["pgrep", "-f", f"port={port}"], capture_output=True)
    if check.returncode != 0:
        subprocess.Popen([
            "jupyter", "lab",
            "--ip=0.0.0.0",
            f"--port={port}",
            "--no-browser",
            "--allow-root",
            "--NotebookApp.token=",
            "--NotebookApp.password=",
            f"--notebook-dir={user_home}"
        ])

    return redirect(f"http://your-app.up.railway.app:{port}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
