from flask import Flask, request, redirect, url_for, session, render_template_string, flash
import sqlite3
import bcrypt
import secrets
import re

app = Flask(__name__)

# Change this in a real deployment
app.secret_key = secrets.token_hex(32)

DATABASE = "users.db"


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            two_fa INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


create_database()


# =========================================================
# INPUT VALIDATION
# =========================================================

def valid_email(email):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(pattern, email) is not None


def valid_password(password):

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    return True


# =========================================================
# MAIN HTML
# =========================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<title>SecureVault</title>

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    min-height: 100vh;

    font-family:
    Arial, Helvetica, sans-serif;

    background:
    radial-gradient(
        circle at top left,
        #12345b,
        transparent 40%
    ),
    radial-gradient(
        circle at bottom right,
        #25104a,
        transparent 40%
    ),
    #060b14;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 20px;
}


.container {

    width: 420px;

    max-width: 100%;

    background:
    rgba(12,20,34,0.95);

    border:
    1px solid #263952;

    border-radius: 22px;

    padding: 30px;

    box-shadow:
    0 25px 80px #000b;

    backdrop-filter:
    blur(15px);

}


.logo {

    text-align: center;

    font-size: 48px;

    margin-bottom: 5px;

}


h1 {

    text-align: center;

    margin: 0;

    font-size: 30px;

    background:
    linear-gradient(
        90deg,
        #00e5ff,
        #7c5cff,
        #00ffa3
    );

    -webkit-background-clip: text;

    color: transparent;

}


.subtitle {

    text-align: center;

    color: #8291a8;

    font-size: 13px;

    margin-top: 8px;

}


.security-status {

    text-align: center;

    margin: 18px 0;

    padding: 8px;

    border-radius: 20px;

    background: #063c31;

    color: #4dffca;

    font-size: 12px;

    border: 1px solid #126651;

}


.tabs {

    display: flex;

    margin-bottom: 22px;

    background: #0a1322;

    padding: 4px;

    border-radius: 10px;

}


.tabs button {

    flex: 1;

    background: transparent;

    border: none;

    color: #7f8da2;

    padding: 10px;

    cursor: pointer;

    border-radius: 7px;

}


.tabs button.active {

    background: #16243a;

    color: white;

}


.form {

    display: none;

}


.form.active {

    display: block;

}


label {

    display: block;

    color: #9eacc0;

    font-size: 13px;

    margin-bottom: 7px;

    margin-top: 14px;

}


input {

    width: 100%;

    padding: 13px;

    border-radius: 9px;

    border: 1px solid #304158;

    background: #08111e;

    color: white;

    font-size: 15px;

    outline: none;

}


input:focus {

    border-color: #00d9ff;

    box-shadow:
    0 0 0 3px #00d9ff18;

}


.password-box {

    position: relative;

}


.show-password {

    position: absolute;

    right: 12px;

    top: 12px;

    cursor: pointer;

    color: #718198;

}


.checkbox {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-top: 15px;

    color: #9aa8ba;

    font-size: 13px;

}


.checkbox input {

    width: auto;

}


.main-button {

    width: 100%;

    margin-top: 22px;

    padding: 14px;

    border: none;

    border-radius: 9px;

    cursor: pointer;

    color: white;

    font-size: 15px;

    font-weight: bold;

    background:
    linear-gradient(
        90deg,
        #007cf0,
        #6a5cff
    );

    transition: .2s;

}


.main-button:hover {

    transform:
    translateY(-2px);

    box-shadow:
    0 10px 30px #007cf044;

}


.message {

    padding: 10px;

    margin-bottom: 15px;

    border-radius: 8px;

    background: #331b1b;

    border: 1px solid #703434;

    color: #ff9d9d;

    text-align: center;

    font-size: 13px;

}


.password-info {

    color: #65748a;

    font-size: 11px;

    line-height: 1.6;

    margin-top: 7px;

}


.features {

    display: grid;

    grid-template-columns: 1fr 1fr;

    gap: 10px;

    margin-top: 22px;

}


.feature {

    padding: 12px;

    border-radius: 10px;

    background: #0a1423;

    border: 1px solid #1c2a3d;

    text-align: center;

    color: #8492a7;

    font-size: 11px;

}


.feature strong {

    display: block;

    color: #4deac4;

    margin-bottom: 4px;

}


.dashboard {

    text-align: center;

}


.dashboard-icon {

    font-size: 65px;

}


.dashboard h2 {

    font-size: 27px;

    margin: 10px;

}


.user-card {

    margin-top: 20px;

    padding: 20px;

    border-radius: 14px;

    background: #0a1423;

    border: 1px solid #263952;

}


.user-card p {

    color: #8795a9;

}


.logout {

    display: block;

    text-decoration: none;

    color: white;

    background:
    linear-gradient(
        90deg,
        #e53935,
        #b71c1c
    );

    padding: 13px;

    border-radius: 9px;

    margin-top: 20px;

}


.footer {

    text-align: center;

    margin-top: 20px;

    color: #4d5b70;

    font-size: 10px;

}


@media(max-width:450px) {

    .container {

        padding: 22px;

    }

}

</style>

</head>


<body>


<div class="container">

{% if page == "dashboard" %}

    <div class="dashboard">

        <div class="dashboard-icon">
            🛡️
        </div>

        <h2>
            Access Granted
        </h2>

        <div class="security-status">
            ● AUTHENTICATED SESSION
        </div>

        <div class="user-card">

            <h3>
                Welcome, {{ username }}
            </h3>

            <p>
                You have successfully authenticated
                with SecureVault.
            </p>

            <p>
                🔐 Password: BCrypt Protected
            </p>

            <p>
                🛡️ Session: Active
            </p>

            <p>
                🔒 Database: SQLite
            </p>

        </div>

        <a href="/logout"
           class="logout">
            🔓 Logout Securely
        </a>

    </div>


{% else %}


    <div class="logo">
        🔐
    </div>

    <h1>
        SecureVault
    </h1>

    <div class="subtitle">
        Secure Authentication Gateway
    </div>

    <div class="security-status">
        ● SECURITY SYSTEM ONLINE
    </div>


    {% with messages =
        get_flashed_messages() %}

        {% if messages %}

            {% for message in messages %}

                <div class="message">
                    {{ message }}
                </div>

            {% endfor %}

        {% endif %}

    {% endwith %}


    <div class="tabs">

        <button
        id="loginTab"
        class="active"
        onclick="showForm('login')">

            Login

        </button>

        <button
        id="registerTab"
        onclick="showForm('register')">

            Register

        </button>

    </div>


    <!-- LOGIN -->

    <div
    id="login"
    class="form active">

        <form method="POST"
              action="/login">

            <label>
                Username
            </label>

            <input
            type="text"
            name="username"
            placeholder="Enter username"
            required>


            <label>
                Password
            </label>

            <div class="password-box">

                <input
                type="password"
                id="loginPassword"
                name="password"
                placeholder="Enter password"
                required>

                <span
                class="show-password"
                onclick="togglePassword(
                'loginPassword')">

                    👁

                </span>

            </div>


            <button
            class="main-button"
            type="submit">

                🔓 Secure Login

            </button>

        </form>

    </div>


    <!-- REGISTER -->

    <div
    id="register"
    class="form">

        <form method="POST"
              action="/register">

            <label>
                Username
            </label>

            <input
            type="text"
            name="username"
            placeholder="Create username"
            minlength="3"
            maxlength="30"
            required>


            <label>
                Email
            </label>

            <input
            type="email"
            name="email"
            placeholder="example@email.com"
            required>


            <label>
                Password
            </label>

            <div class="password-box">

                <input
                type="password"
                id="registerPassword"
                name="password"
                placeholder="Create strong password"
                required>

                <span
                class="show-password"
                onclick="togglePassword(
                'registerPassword')">

                    👁

                </span>

            </div>


            <div class="password-info">

                Minimum 8 characters,
                one uppercase,
                one lowercase
                and one number.

            </div>


            <div class="checkbox">

                <input
                type="checkbox"
                name="two_fa"
                value="1">

                Enable demo Two-Factor Authentication

            </div>


            <button
            class="main-button"
            type="submit">

                🛡️ Create Secure Account

            </button>

        </form>

    </div>


    <div class="features">

        <div class="feature">

            <strong>🔐 BCrypt</strong>

            Password Hashing

        </div>

        <div class="feature">

            <strong>🛡️ SQL Safe</strong>

            Parameterized Queries

        </div>

        <div class="feature">

            <strong>🍪 Session</strong>

            Secure Login State

        </div>

        <div class="feature">

            <strong>🔑 2FA</strong>

            OTP Protection

        </div>

    </div>


    <div class="footer">

        SecureVault • Cybersecurity Demo

    </div>


{% endif %}

</div>


<script>

function showForm(form) {

    document
    .querySelectorAll(".form")
    .forEach(
        item => item.classList.remove("active")
    );


    document
    .querySelectorAll(".tabs button")
    .forEach(
        item => item.classList.remove("active")
    );


    document
    .getElementById(form)
    .classList.add("active");


    document
    .getElementById(form + "Tab")
    .classList.add("active");

}


function togglePassword(id) {

    let input =
    document.getElementById(id);

    if (input.type === "password") {

        input.type = "text";

    } else {

        input.type = "password";

    }

}

</script>


</body>

</html>

"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:

        return render_template_string(
            HTML,
            page="dashboard",
            username=session["username"]
        )

    return render_template_string(
        HTML,
        page="login"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get(
        "username", ""
    ).strip()

    email = request.form.get(
        "email", ""
    ).strip().lower()

    password = request.form.get(
        "password", ""
    )

    two_fa = 1 if request.form.get(
        "two_fa"
    ) else 0


    # Basic validation

    if len(username) < 3:

        flash(
            "Username must contain at least 3 characters."
        )

        return redirect(url_for("home"))


    if not valid_email(email):

        flash(
            "Please enter a valid email address."
        )

        return redirect(url_for("home"))


    if not valid_password(password):

        flash(
            "Password must contain 8+ characters, uppercase, lowercase and a number."
        )

        return redirect(url_for("home"))


    # BCrypt password hashing

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )


    try:

        conn = get_db()

        # Parameterized SQL query
        # Prevents SQL injection

        conn.execute(
            """
            INSERT INTO users
            (username, email, password, two_fa)
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                email,
                hashed_password.decode("utf-8"),
                two_fa
            )
        )

        conn.commit()

        conn.close()

        flash(
            "Account created successfully. You can now login."
        )

    except sqlite3.IntegrityError:

        flash(
            "Username or email already exists."
        )


    return redirect(url_for("home"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get(
        "username", ""
    ).strip()

    password = request.form.get(
        "password", ""
    )


    conn = get_db()

    # Parameterized query
    # User input is NOT directly inserted into SQL

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()


    if user is None:

        flash(
            "Invalid username or password."
        )

        return redirect(url_for("home"))


    stored_password = user["password"]


    # Verify BCrypt hash

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password.encode("utf-8")
    ):

        flash(
            "Invalid username or password."
        )

        return redirect(url_for("home"))


    # =====================================================
    # OPTIONAL DEMO 2FA
    # =====================================================

    if user["two_fa"]:

        otp = str(
            secrets.randbelow(900000) + 100000
        )

        session["pending_2fa"] = True
        session["pending_user"] = user["id"]
        session["otp"] = otp
        session["username_temp"] = user["username"]

        print("\n==============================")
        print("DEMO 2FA OTP:", otp)
        print("==============================\n")

        return redirect(
            url_for("verify_2fa")
        )


    # =====================================================
    # SESSION CREATION
    # =====================================================

    session.clear()

    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return redirect(
        url_for("home")
    )


# =========================================================
# 2FA PAGE
# =========================================================

@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():

    if not session.get("pending_2fa"):

        return redirect(url_for("home"))


    if request.method == "POST":

        entered_otp = request.form.get(
            "otp", ""
        ).strip()


        if entered_otp == session.get("otp"):

            user_id = session["pending_user"]
            username = session["username_temp"]

            session.clear()

            session["user_id"] = user_id
            session["username"] = username

            return redirect(
                url_for("home")
            )

        flash(
            "Invalid OTP. Check the terminal."
        )


    return render_template_string(
        """

        <!DOCTYPE html>

        <html>

        <head>

        <title>2FA Verification</title>

        <style>

        body {

            margin:0;

            min-height:100vh;

            display:flex;

            align-items:center;

            justify-content:center;

            background:
            linear-gradient(
                135deg,
                #060b14,
                #17254a
            );

            font-family:Arial;

            color:white;

        }

        .box {

            width:380px;

            max-width:90%;

            padding:35px;

            border-radius:20px;

            background:#0d1727;

            border:1px solid #2b3d58;

            text-align:center;

        }

        .icon {

            font-size:55px;

        }

        h1 {

            color:#00d9ff;

        }

        p {

            color:#8998ad;

        }

        input {

            width:100%;

            box-sizing:border-box;

            padding:15px;

            margin-top:15px;

            background:#07101d;

            color:white;

            border:1px solid #33445e;

            border-radius:8px;

            text-align:center;

            font-size:20px;

            letter-spacing:5px;

        }

        button {

            width:100%;

            margin-top:18px;

            padding:14px;

            border:0;

            border-radius:8px;

            background:
            linear-gradient(
                90deg,
                #007cf0,
                #7657ff
            );

            color:white;

            font-weight:bold;

            cursor:pointer;

        }

        .error {

            color:#ff7777;

        }

        </style>

        </head>

        <body>

        <div class="box">

            <div class="icon">
                🔑
            </div>

            <h1>
                2FA Verification
            </h1>

            <p>
                Enter the 6-digit OTP shown
                in the Flask terminal.
            </p>

            {% with messages =
                get_flashed_messages() %}

                {% for message in messages %}

                    <div class="error">
                        {{ message }}
                    </div>

                {% endfor %}

            {% endwith %}

            <form method="POST">

                <input
                name="otp"
                maxlength="6"
                placeholder="000000"
                required>

                <button>
                    Verify Identity
                </button>

            </form>

        </div>

        </body>

        </html>

        """
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been securely logged out."
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
