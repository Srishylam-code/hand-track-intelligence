"""
auth_app.py - Standalone Flask Auth Server (Port 5001)
Handles Signup with OTP email verification, Login, and Excel user storage.

SETUP:
  1. Create a .env file in this directory:
       MAIL_USER=yourgmail@gmail.com
       MAIL_PASSWORD=your_gmail_app_password   (NOT your normal password)
       SECRET_KEY=any_random_long_string
  2. To get a Gmail App Password:
       - Enable 2FA on your Google Account
       - Go to: Google Account → Security → 2-Step Verification → App passwords
       - Generate one for "Mail" and paste it here
  3. Run: python auth_app.py
  4. Open: http://localhost:5001
"""

import os
import smtplib
import ssl
import random
import string
import bcrypt
import openpyxl
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, session, jsonify
from dotenv import load_dotenv
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-secret-key-2026")

MAIL_USER     = os.environ.get("MAIL_USER", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 465

USERS_FILE    = Path(__file__).parent / "users.xlsx"
OTP_EXPIRY_MINUTES = 5
MAX_RESENDS   = 3

# In-memory OTP store: { email: { otp, expiry, resend_count } }
otp_store: dict = {}

# ---------------------------------------------------------------------------
# Excel helpers
# ---------------------------------------------------------------------------
def _load_workbook():
    """Load or create the users Excel workbook."""
    if USERS_FILE.exists():
        return openpyxl.load_workbook(USERS_FILE)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append(["Email", "PasswordHash", "CreatedAt"])
    wb.save(USERS_FILE)
    return wb


def email_exists(email: str) -> bool:
    """Return True if email is already registered."""
    wb = _load_workbook()
    ws = wb["Users"]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[0].lower() == email.lower():
            return True
    return False


def get_user_hash(email: str):
    """Return stored password hash for email, or None."""
    wb = _load_workbook()
    ws = wb["Users"]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[0].lower() == email.lower():
            return row[1]
    return None


def save_user(email: str, password_plain: str):
    """Hash password and append new user row to Excel."""
    hashed = bcrypt.hashpw(password_plain.encode(), bcrypt.gensalt()).decode()
    wb = _load_workbook()
    ws = wb["Users"]
    ws.append([email.lower(), hashed, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    wb.save(USERS_FILE)


# ---------------------------------------------------------------------------
# OTP helpers
# ---------------------------------------------------------------------------
# In-memory OTP store: { email: { otp, expiry, last_sent } }
otp_store = {}

def send_otp(email):
    """
    1. Generates 6-digit OTP
    2. Checks 60s resend protection
    3. Stores with 5m expiry
    4. Sends SSL email (Port 465)
    5. Returns (success, message)
    """
    email = email.lower().strip()
    now = datetime.now()

    # 1. Resend Protection (60 seconds)
    if email in otp_store:
        last_sent = otp_store[email].get("last_sent")
        if last_sent and (now - last_sent).total_seconds() < 60:
            print(f"[DEBUG] Resend blocked for {email} (too soon)")
            return False, "Please wait 60 seconds before requesting another OTP."

    # 2. Generate OTP
    otp = "".join(random.choices(string.digits, k=6))
    print(f"[DEBUG] Generated OTP for {email}: {otp}")

    # 3. Store OTP with 5m expiry
    otp_store[email] = {
        "otp": otp,
        "expiry": now + timedelta(minutes=5),
        "last_sent": now
    }

    # 4. Prepare Email
    mail_user = os.getenv("MAIL_USER")
    mail_pass = os.getenv("MAIL_PASSWORD")

    if not mail_user or not mail_pass:
        print("[ERROR] MAIL_USER or MAIL_PASSWORD environment variables not set.")
        return False, "Server configuration error: missing email credentials."

    subject = f"Your Verification Code: {otp}"
    message_text = f"Your verification code is: {otp}\n\nThis code expires in 5 minutes.\n\n— Virtual Life with AI"
    
    msg = MIMEText(message_text)
    msg["Subject"] = subject
    msg["From"] = f"Virtual Life with AI <{mail_user}>"
    msg["To"] = email

    # 5. Send Email via SSL (Port 465)
    try:
        print(f"[DEBUG] Attempting to send email to {email}")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(mail_user, mail_pass)
            server.send_message(msg)
        print(f"[SUCCESS] Email sent to {email}")
        return True, "OTP sent successfully! Please check your inbox."
    except Exception as e:
        print(f"[ERROR] Exception occurred while sending email: {str(e)}")
        return False, f"Email delivery failed: {str(e)}"


# (verify_otp logic moved directly into the verify-otp route)


# (HTML template removed for a cleaner production-ready plain text implementation)

# ---------------------------------------------------------------------------
# Email sender
# ---------------------------------------------------------------------------
# (send_otp_email deleted - logic moved to send_otp)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------
def is_valid_email(email: str) -> bool:
    import re
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def is_valid_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    return True, ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("auth.html")


@app.route("/status")
def status():
    """Return current login status for the homepage to consume."""
    return jsonify({
        "logged_in": "user_email" in session,
        "email": session.get("user_email", ""),
    })


@app.route("/signup", methods=["POST"])
def signup():
    print("[DEBUG] Signup route triggered")
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email:
        print("[DEBUG] Signup failed: missing email")
        return jsonify(success=False, message="Email is required.")
    
    if len(password) < 8:
        print("[DEBUG] Signup failed: password too short")
        return jsonify(success=False, message="Password must be at least 8 characters.")

    if email_exists(email):
        print(f"[DEBUG] Signup failed: {email} already exists")
        return jsonify(success=False, message="This email is already registered.")

    # Store pending password in session securely
    session["pending_email"] = email
    session["pending_password"] = password

    # Call send_otp
    print(f"[DEBUG] Calling send_otp for {email}")
    success, msg = send_otp(email)
    
    if not success:
        return jsonify(success=False, message=msg)

    return jsonify(success=True, message=msg)


@app.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    print("[DEBUG] Verify OTP route triggered")
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower() or session.get("pending_email")
    otp_entered = data.get("otp", "").strip()

    if not email or not otp_entered:
        print("[DEBUG] Verification failed: missing email or OTP")
        return jsonify(success=False, message="Email and OTP are required.")

    # Retrieve OTP from store
    record = otp_store.get(email)
    if not record:
        print(f"[DEBUG] Verification failed: no record for {email}")
        return jsonify(success=False, message="No OTP record found. Please sign up again.")

    # Check OTP and Expiry
    if record["otp"] != otp_entered:
        print(f"[DEBUG] Verification failed: invalid OTP for {email}")
        return jsonify(success=False, message="Invalid verification code.")

    if datetime.now() > record["expiry"]:
        print(f"[DEBUG] Verification failed: OTP expired for {email}")
        otp_store.pop(email, None) # Clean up
        return jsonify(success=False, message="Verification code has expired.")

    # Success!
    print(f"[SUCCESS] OTP verified for {email}")
    
    # Save user data
    pending_pass = session.get("pending_password")
    if not pending_pass:
        return jsonify(success=False, message="Session expired. Please sign up again.")

    save_user(email, pending_pass)
    
    # Cleanup OTP and Session
    otp_store.pop(email, None)
    session.pop("pending_password", None)
    session["user_email"] = email
    
    return jsonify(success=True, message="Account verified and created successfully!")


@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    print("[DEBUG] Resend OTP route triggered")
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower() or session.get("pending_email")

    if not email:
        return jsonify(success=False, message="No email found. Please start signup again.")

    # Call the new send_otp which already handles 60s protection
    success, msg = send_otp(email)
    
    if not success:
        return jsonify(success=False, message=msg)

    return jsonify(success=True, message="A new verification code has been sent.")


@app.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    email    = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify(success=False, message="Email and password are required.")
    if not is_valid_email(email):
        return jsonify(success=False, message="Please enter a valid email address.")

    stored_hash = get_user_hash(email)
    if not stored_hash:
        return jsonify(success=False, message="No account found with this email. Please sign up.")

    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return jsonify(success=False, message="Incorrect password. Please try again.")

    session["user_email"] = email.lower()
    return jsonify(success=True, message=f"Login successful! Welcome back, {email}.")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(success=True, message="Logged out successfully.")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Virtual Life Auth Server running at http://localhost:5001")
    m_user = os.getenv("MAIL_USER")
    if not m_user:
        print("  ⚠  WARNING: MAIL_USER not found in environment!")
    else:
        print(f"  ✉  SMTP configured for: {m_user}")
    print("="*55 + "\n")
    # Setting debug=False for a "production-ready" feel, or True if they prefer
    app.run(host="0.0.0.0", port=5001, debug=True)
