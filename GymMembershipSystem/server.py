import http.server
import socketserver
import urllib.parse
import os
import sqlite3
import datetime
import http.cookies
import uuid
import re

PORT = 8080
WEB_DIR = os.path.join(os.path.dirname(__file__), "WebContent")

# Initialize local database for live demo server (mirrors MySQL gym_db schema)
DB_FILE = os.path.join(os.path.dirname(__file__), "gym_live.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            membership TEXT NOT NULL,
            join_date DATE NOT NULL,
            status TEXT DEFAULT 'Active'
        )
    ''')
    # Insert sample test data if table empty
    cursor.execute('SELECT COUNT(*) FROM members')
    if cursor.fetchone()[0] == 0:
        today = datetime.date.today().strftime('%Y-%m-%d')
        cursor.executemany('''
            INSERT INTO members (name, email, phone, password, membership, join_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('Alex Johnson', 'alex@fitnesshub.com', '9876543210', 'password123', 'Yearly', today, 'Active'),
            ('Sarah Connor', 'sarah@fitnesshub.com', '9123456789', 'sarah2026', 'Quarterly', today, 'Active'),
            ('Mike Tyson', 'mike@fitnesshub.com', '9988776655', 'ironmike', 'Monthly', today, 'Active')
        ])
    conn.commit()
    conn.close()

init_db()

# In-memory Session Storage
SESSIONS = {}

class GymAppHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve static files from WebContent folder
        url_path = urllib.parse.urlparse(path).path
        if url_path == "/" or url_path == "":
            url_path = "/index.html"
        full_path = os.path.join(WEB_DIR, url_path.lstrip("/"))
        return full_path

    def get_session(self):
        cookie_header = self.headers.get("Cookie")
        if cookie_header:
            cookie = http.cookies.SimpleCookie(cookie_header)
            if "SESSIONID" in cookie:
                sid = cookie["SESSIONID"].value
                return SESSIONS.get(sid)
        return None

    def create_session(self, user_email):
        sid = str(uuid.uuid4())
        SESSIONS[sid] = {"email": user_email}
        return sid

    def clear_session(self):
        cookie_header = self.headers.get("Cookie")
        if cookie_header:
            cookie = http.cookies.SimpleCookie(cookie_header)
            if "SESSIONID" in cookie:
                sid = cookie["SESSIONID"].value
                if sid in SESSIONS:
                    del SESSIONS[sid]

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/DashboardServlet" or path == "/dashboard.jsp":
            session = self.get_session()
            if not session or "email" not in session:
                self.send_response(302)
                self.send_header("Location", "login.html?error=" + urllib.parse.quote("Please login to access your dashboard"))
                self.end_headers()
                return

            # Fetch user details from DB
            user_email = session["email"]
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, phone, membership, join_date, status FROM members WHERE email = ?", (user_email,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                self.clear_session()
                self.send_response(302)
                self.send_header("Location", "login.html?error=" + urllib.parse.quote("Member record not found"))
                self.end_headers()
                return

            name, email, phone, plan, join_date, status = row

            # Render dashboard JSP template dynamically
            jsp_path = os.path.join(WEB_DIR, "dashboard.jsp")
            with open(jsp_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace JSP scriptlets with dynamic values
            content = re.sub(r'<%[\s\S]*?%>', '', content) # Strip top scriptlet
            content = content.replace('<%= (name != null) ? name.toUpperCase() : "MEMBER" %>', name.upper())
            content = content.replace('<%= (name != null) ? name : "N/A" %>', name)
            content = content.replace('<%= (email != null) ? email : "N/A" %>', email)
            content = content.replace('<%= (phone != null) ? phone : "N/A" %>', phone)
            content = content.replace('<%= joinDate %>', str(join_date))
            content = content.replace('<%= status %>', status)
            content = content.replace('<%= (plan != null) ? plan : "Monthly" %>', plan)

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        elif path == "/LogoutServlet":
            self.clear_session()
            self.send_response(302)
            cookie = http.cookies.SimpleCookie()
            cookie["SESSIONID"] = ""
            cookie["SESSIONID"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
            cookie["SESSIONID"]["path"] = "/"
            self.send_header("Set-Cookie", cookie.output(header=""))
            self.send_header("Location", "login.html?loggedout=true")
            self.end_headers()
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        form_data = urllib.parse.parse_qs(body)

        if path == "/RegisterServlet":
            name = form_data.get('name', [''])[0].strip()
            email = form_data.get('email', [''])[0].strip().lower()
            phone = form_data.get('phone', [''])[0].strip()
            password = form_data.get('password', [''])[0]
            membership = form_data.get('membership', [''])[0].strip()

            if not name or not email or not phone or not password or not membership:
                self.send_redirect("register.html?error=" + urllib.parse.quote("All fields are required"))
                return

            if len(phone) != 10:
                self.send_redirect("register.html?error=" + urllib.parse.quote("Phone number must be exactly 10 digits"))
                return

            if len(password) < 6:
                self.send_redirect("register.html?error=" + urllib.parse.quote("Password must be at least 6 characters"))
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            today = datetime.date.today().strftime('%Y-%m-%d')

            try:
                cursor.execute('''
                    INSERT INTO members (name, email, phone, password, membership, join_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, email, phone, password, membership, today, 'Active'))
                conn.commit()
                conn.close()
                self.send_redirect("login.html?registered=true")
            except sqlite3.IntegrityError:
                conn.close()
                self.send_redirect("register.html?error=" + urllib.parse.quote("Email address is already registered!"))

        elif path == "/LoginServlet":
            email = form_data.get('email', [''])[0].strip().lower()
            password = form_data.get('password', [''])[0]

            if not email or not password:
                self.send_redirect("login.html?error=" + urllib.parse.quote("Please enter both email and password"))
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                sid = self.create_session(email)
                cookie = http.cookies.SimpleCookie()
                cookie["SESSIONID"] = sid
                cookie["SESSIONID"]["path"] = "/"
                self.send_response(302)
                self.send_header("Set-Cookie", cookie.output(header=""))
                self.send_header("Location", "DashboardServlet")
                self.end_headers()
            else:
                self.send_redirect("login.html?error=" + urllib.parse.quote("Invalid email or password"))

        else:
            self.send_error(404, "Endpoint not found")

    def send_redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(WEB_DIR)
    handler = GymAppHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        httpd.serve_forever()
