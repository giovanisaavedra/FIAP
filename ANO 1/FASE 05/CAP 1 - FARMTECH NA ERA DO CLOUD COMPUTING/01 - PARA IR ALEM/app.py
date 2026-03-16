import base64
import os
import csv
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory
import pymysql

APP_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(APP_DIR, "uploads")
CSV_PATH = os.path.join(APP_DIR, "readings.csv")

os.makedirs(UPLOADS, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(APP_DIR, "templates"))
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

# =========================
# CONFIG MYSQL (XAMPP)
# =========================
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASS = ""
MYSQL_DB = "farmdb"

# =========================
# CSV
# =========================
def append_csv(ts, humidity, temperature, filename):
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["timestamp", "humidity", "temperature", "filename"])
        w.writerow([ts, humidity, temperature, filename])

def read_last_rows_csv(limit=30):
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-limit:][::-1]

# =========================
# MYSQL
# =========================
def save_mysql(ts, humidity, temperature, filename, img_path, client_ip):
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        connect_timeout=5
    )

    cur = conn.cursor()

    query = """
    INSERT INTO readings (ts, device_id, humidity, temperature, image_filename, image_size, client_ip)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cur.execute(query, (
        ts,
        "esp32cam",
        humidity,
        temperature,
        filename,
        os.path.getsize(img_path),
        client_ip
    ))

    conn.commit()
    cur.close()
    conn.close()

def read_last_rows_mysql(limit=30):
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        connect_timeout=5,
        cursorclass=pymysql.cursors.DictCursor
    )

    cur = conn.cursor()
    cur.execute("""
        SELECT ts, humidity, temperature, image_filename
        FROM readings
        ORDER BY id DESC
        LIMIT %s
    """, (limit,))
    db_rows = cur.fetchall()

    cur.close()
    conn.close()

    rows = []
    for r in db_rows:
        rows.append({
            "timestamp": str(r["ts"]),
            "humidity": r["humidity"],
            "temperature": r["temperature"],
            "filename": r["image_filename"]
        })
    return rows

# =========================
# API RECEBE DO ESP32
# =========================
@app.route("/api/upload_json", methods=["POST"])
def upload_json():
    try:
        data = request.get_json(force=True)

        humidity = float(data.get("humidity", 0))
        temperature = float(data.get("temperature", 0))
        img_b64 = data.get("image_b64", "")

        print("JSON recebido:", data)
        print("humidity =", humidity)
        print("temperature =", temperature)

        if not img_b64:
            return {"ok": False, "error": "missing image_b64"}, 400

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        img_path = os.path.join(UPLOADS, filename)

        # Salva imagem
        img_bytes = base64.b64decode(img_b64)
        with open(img_path, "wb") as f:
            f.write(img_bytes)

        # Salva em CSV
        append_csv(ts, humidity, temperature, filename)

        # Salva em MySQL
        try:
            save_mysql(ts, humidity, temperature, filename, img_path, request.remote_addr)
            print("MySQL OK")
        except Exception as e:
            print("Erro ao salvar no MySQL:", repr(e))

        return {"ok": True}

    except Exception as e:
        print("ERRO upload_json:", repr(e))
        return {"ok": False, "error": str(e)}, 500

# =========================
# DASHBOARD
# =========================
@app.route("/")
def dashboard():
    try:
        rows = read_last_rows_mysql(30)
        if not rows:
            rows = read_last_rows_csv(30)
    except Exception as e:
        print("Erro ao ler MySQL, usando CSV:", repr(e))
        rows = read_last_rows_csv(30)

    latest = rows[0] if rows else None
    return render_template("index.html", latest=latest, rows=rows)

# =========================
# SERVIR IMAGENS
# =========================
@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOADS, filename)

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)