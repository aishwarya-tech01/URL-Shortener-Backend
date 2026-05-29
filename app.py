import os
import random
import string
import sqlite3
from datetime import datetime
import qrcode
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'my_secret_session_key_123'
DATABASE = 'url_shortener.db'
QR_STORAGE_PATH = 'static/qrcodes'

os.makedirs(QR_STORAGE_PATH, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        with open('schema.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("[DATABASE] Successfully initialized backend tables.")

def generate_random_slug(length=6):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for _ in range(length))

# --- UI LAYER ---
MAIN_DASHBOARD_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>URL Shortener & Analytics Panel</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f1f5f9; color: #1e293b; margin: 0; padding: 40px 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 30px; }
        .card { background: #ffffff; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .form-row { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; color: #475569; }
        input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
        .btn { background-color: #2563eb; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: 600; width: 100%; font-size: 15px; }
        .btn:hover { background-color: #1d4ed8; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
        th { background-color: #f8fafc; padding: 12px; color: #64748b; border-bottom: 2px solid #e2e8f0; text-align: left; }
        td { padding: 12px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
        .qr-frame { width: 70px; height: 70px; border: 1px solid #e2e8f0; border-radius: 4px; }
        .flash { padding: 12px; background-color: #fef08a; border-left: 4px solid #eab308; margin-bottom: 20px; border-radius: 4px; color: #713f12; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔗 Advanced URL Shortener Dashboard</h1>
            <p style="color: #64748b;">Python Backend Project with Analytics</p>
        </header>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="flash">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="card">
            <h2>Shorten a Long Link</h2>
            <form action="/shorten" method="POST">
                <div class="form-row">
                    <label for="long_url">Paste Long URL *</label>
                    <input type="url" id="long_url" name="long_url" placeholder="https://example.com/some/long/link" required>
                </div>
                <div class="form-row">
                    <label for="custom_alias">Custom Alias (Optional Vanity Brand String)</label>
                    <input type="text" id="custom_alias" name="custom_alias" placeholder="e.g., myfest">
                </div>
                <div class="form-row">
                    <label for="expires_at">Link Expiration Date & Time (Optional)</label>
                    <input type="datetime-local" id="expires_at" name="expires_at">
                </div>
                <button type="submit" class="btn">Shorten Link & Build QR Asset</button>
            </form>
        </div>

        <div class="card">
            <h2>Active Links Tracker</h2>
            <table>
                <thead>
                    <tr>
                        <th>Original Destination</th>
                        <th>Short Clean URL</th>
                        <th>Clicks Tracker</th>
                        <th>Expiration Target</th>
                        <th>QR Code Asset</th>
                        <th>Detailed Analytics</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in links %}
                    <tr>
                        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.long_url }}</td>
                        <td><a href="/{{ item.short_code }}" target="_blank" style="color: #2563eb; font-weight: 600;">{{ host_domain }}{{ item.short_code }}</a></td>
                        <td><strong>{{ item.clicks }} clicks</strong></td>
                        <td>{{ item.expires_at if item.expires_at else 'Permanent' }}</td>
                        <td><img class="qr-frame" src="/static/qrcodes/{{ item.short_code }}.png"></td>
                        <td><a href="/analytics/{{ item.id }}" style="color: #0284c7; text-decoration: none; font-weight: 600;">View Stats 📊</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

ANALYTICS_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Telemetry History Reports</title>
    <style>
        body { font-family: sans-serif; background-color: #f8fafc; padding: 40px 20px; }
        .card { max-width: 700px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { color: #64748b; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📊 Device Visitor Stats for: /{{ link.short_code }}</h1>
        <p><strong>Destination:</strong> {{ link.long_url }}</p>
        <p><strong>Total Hits logged:</strong> {{ link.clicks }}</p>
        <hr>
        <h3>Click Activity Logs</h3>
        {% if logs %}
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Browser</th>
                    <th>Platform OS</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr>
                    <td>{{ log.clicked_at }}</td>
                    <td>{{ log.browser }}</td>
                    <td>{{ log.platform }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color: #94a3b8;">No link entries tracked yet.</p>
        {% endif %}
        <br>
        <a href="/" style="color: #2563eb;">⬅️ Back to Control Center</a>
    </div>
</body>
</html>
"""

# --- WORK ROUTES ---

@app.route('/')
def home():
    conn = get_db_connection()
    links = conn.execute('SELECT * FROM urls ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string(MAIN_DASHBOARD_UI, links=links, host_domain=request.host_url)

@app.route('/shorten', methods=['POST'])
def shorten_link():
    long_url = request.form['long_url'].strip()
    custom_alias = request.form['custom_alias'].strip()
    expires_at = request.form['expires_at'].strip()
    
    if not expires_at:
        expires_at = None
    else:
        expires_at = expires_at.replace('T', ' ')

    conn = get_db_connection()

    if custom_alias:
        check = conn.execute('SELECT * FROM urls WHERE short_code = ?', (custom_alias,)).fetchone()
        if check:
            flash(f"Error: Slug '{custom_alias}' is already in use!")
            conn.close()
            return redirect(url_for('home'))
        short_code = custom_alias
    else:
        short_code = generate_random_slug()

    try:
        conn.execute('INSERT INTO urls (long_url, short_code, expires_at) VALUES (?, ?, ?)', (long_url, short_code, expires_at))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("System error, please try generating again.")
        conn.close()
        return redirect(url_for('home'))
    finally:
        conn.close()

    # Generate QR asset
    qr_url = request.host_url + short_code
    qr_image = qrcode.make(qr_url)
    qr_image.save(os.path.join(QR_STORAGE_PATH, f"{short_code}.png"))

    flash("Success! Clean route created and QR code updated.")
    return redirect(url_for('home'))

@app.route('/<short_code>')
def send_redirect(short_code):
    conn = get_db_connection()
    link = conn.execute('SELECT * FROM urls WHERE short_code = ?', (short_code,)).fetchone()

    if not link:
        conn.close()
        return "<h1>404 Link Error</h1>", 404

    if link['expires_at']:
        expiration = datetime.strptime(link['expires_at'], '%Y-%m-%d %H:%M')
        if datetime.now() > expiration:
            conn.close()
            return f"<h1>⚠️ Link Expired!</h1>", 410

    conn.execute('UPDATE urls SET clicks = clicks + 1 WHERE id = ?', (link['id'],))
    
    # Advanced Telemetry Tracking
    ua = request.user_agent
    browser = ua.browser if ua.browser else "Unknown Browser"
    platform = ua.platform if ua.platform else "Unknown OS"
    
    conn.execute('INSERT INTO clicks_analytics (url_id, browser, platform) VALUES (?, ?, ?)', (link['id'], browser, platform))
    conn.commit()
    conn.close()
    
    return redirect(link['long_url'])

@app.route('/analytics/<int:url_id>')
def stats(url_id):
    conn = get_db_connection()
    link = conn.execute('SELECT * FROM urls WHERE id = ?', (url_id,)).fetchone()
    logs = conn.execute('SELECT * FROM clicks_analytics WHERE url_id = ? ORDER BY clicked_at DESC', (url_id,)).fetchall()
    conn.close()
    return render_template_string(ANALYTICS_UI, link=link, logs=logs)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)