#!/usr/bin/env python3
"""
SmartKrushi Real-World Production Backend Server (HTTP + REST API + Scikit-Learn ML + SQLite + SMTP)
Serves the frontend web application on http://localhost:8000 and exposes live API endpoints
that execute the real Python Scikit-Learn ML models in big/farmer/ML/ and persist records in SQLite.
"""

import json
import os
import smtplib
import sqlite3
import subprocess
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ML_DIR = os.path.join(BASE_DIR, "ml")
if not os.path.exists(ML_DIR):
    ML_DIR = os.path.join(BASE_DIR, "big", "farmer", "ML")
DB_PATH = os.path.join(BASE_DIR, "smart_krushi_production.db")

# Centralized Backend SMTP Configuration (Dynamically loaded from .env or Environment Variables)
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")
HOME_ENV_PATH = os.path.expanduser("~/.env")


def load_smtp_credentials():
    env_vars = {}
    for path in (HOME_ENV_PATH, ENV_FILE_PATH):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        env_vars[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
    smtp_email = (
        env_vars.get("SMARTKRUSHI_SMTP_EMAIL")
        or os.environ.get("SMARTKRUSHI_SMTP_EMAIL")
        or "kushora.otp@gmail.com"
    ).strip()
    smtp_pass = (
        env_vars.get("SMARTKRUSHI_SMTP_PASS")
        or os.environ.get("SMARTKRUSHI_SMTP_PASS")
        or ""
    ).replace(" ", "").strip()
    return smtp_email, smtp_pass


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            to_email TEXT,
            to_name TEXT,
            role TEXT,
            order_id TEXT,
            type TEXT,
            subject TEXT,
            body TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ml_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT,
            inputs_json TEXT,
            prediction_output TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def run_ml_script(script_rel_path, args):
    script_path = os.path.join(ML_DIR, *script_rel_path.split("/"))
    try:
        cmd = [sys.executable, script_path] + [str(a) for a in args]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        output = (proc.stdout or "").strip()
        if proc.returncode != 0 and not output:
            output = (proc.stderr or "ML execution error").strip()
    except subprocess.TimeoutExpired:
        output = "Prediction timed out during cold start. Please retry in a moment."
    except Exception as e:
        output = f"ML error: {str(e)}"

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO ml_audit_logs (module, inputs_json, prediction_output) VALUES (?, ?, ?)",
            (script_rel_path, json.dumps(args), output)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    return output


def send_real_smtp_or_log(payload):
    to_email = payload.get("to_email", "")
    to_name = payload.get("to_name", "User")
    role = payload.get("role", "customer")
    order_id = str(payload.get("order_id", ""))
    mail_type = payload.get("type", "Notification")
    subject = payload.get("subject", "SmartKrushi Notification")
    body = payload.get("body", "")
    html_body = payload.get("html_body", "")

    smtp_user, smtp_pass = load_smtp_credentials()
    delivery_status = "Pending SMTP App Password in .env"
    sent_live = False

    if smtp_user and smtp_pass and to_email and "@" in to_email:
        msg = MIMEMultipart("alternative")
        msg["From"] = "SmartKrushi No-Reply <no-reply@smartkrushi.in>"
        msg["Reply-To"] = "no-reply@smartkrushi.in"
        msg["Auto-Submitted"] = "auto-generated"
        msg["X-Auto-Response-Suppress"] = "All"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=12)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
            server.quit()
            delivery_status = "Sent via Gmail SMTP (250 OK)"
            sent_live = True
        except Exception:
            try:
                server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=12)
                server_ssl.login(smtp_user, smtp_pass)
                server_ssl.sendmail(smtp_user, [to_email], msg.as_string())
                server_ssl.quit()
                delivery_status = "Sent via Gmail SMTP SSL (250 OK)"
                sent_live = True
            except Exception as e2:
                delivery_status = f"SMTP Error: {str(e2)[:80]}"

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO email_logs (to_email, to_name, role, order_id, type, subject, body, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (to_email, to_name, role, order_id, mail_type, subject, body, delivery_status)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    return {"success": True, "sent_live": sent_live, "status": delivery_status}


class SmartKrushiRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def _send_json(self, data, status=200):
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self._send_json({
                "status": "online",
                "engine": "SmartKrushi Python + Scikit-Learn + SQLite Production Server",
                "database": DB_PATH
            })
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body_raw)
        except Exception:
            data = {}

        if parsed.path == "/api/ml/crop_prediction":
            out = run_ml_script(
                "crop_prediction/ZDecision_Tree_Model_Call.py",
                [data.get("state", "Maharashtra"), data.get("district", "PUNE"), data.get("season", "Kharif")]
            )
            return self._send_json({"success": True, "prediction": out})

        if parsed.path in ("/api/ml/crop_recommendation", "/api/ml/soil_analysis"):
            out = run_ml_script(
                "crop_recommendation/recommend.py",
                [
                    data.get("n", 90), data.get("p", 42), data.get("k", 43),
                    data.get("t", 25), data.get("h", 80), data.get("ph", 6.5), data.get("r", 200)
                ]
            )
            return self._send_json({"success": True, "prediction": out})

        if parsed.path == "/api/ml/fertilizer_recommendation":
            out = run_ml_script(
                "fertilizer_recommendation/fertilizer_recommendation.py",
                [
                    data.get("n", 37), data.get("p", 0), data.get("k", 0),
                    data.get("t", 26), data.get("h", 52), data.get("sm", 38),
                    data.get("soil", "Sandy"), data.get("crop", "Maize")
                ]
            )
            return self._send_json({"success": True, "prediction": out})

        if parsed.path == "/api/ml/yield_prediction":
            out = run_ml_script(
                "yield_prediction/yield_prediction.py",
                [
                    data.get("state", "Maharashtra"), data.get("district", "Pune"),
                    data.get("season", "Kharif"), data.get("crop", "Soyabean"), data.get("area", 10)
                ]
            )
            return self._send_json({"success": True, "prediction": out})

        if parsed.path == "/api/ml/rainfall_prediction":
            out = run_ml_script(
                "rainfall_prediction/rainfall_prediction.py",
                [data.get("region", "MADHYA MAHARASHTRA"), data.get("month", "JUL")]
            )
            return self._send_json({"success": True, "prediction": out})

        if parsed.path == "/api/send_email":
            res = send_real_smtp_or_log(data)
            return self._send_json(res)

        return self._send_json({"success": False, "error": "Unknown API endpoint"}, status=404)


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer(("0.0.0.0", port), SmartKrushiRequestHandler)
    print(f"============================================================")
    print(f" SmartKrushi Production Server Running at: http://localhost:{port}")
    print(f" SQLite Database: {DB_PATH}")
    print(f" Scikit-Learn ML Directory: {ML_DIR}")
    print(f"============================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down SmartKrushi server...")
        server.server_close()

