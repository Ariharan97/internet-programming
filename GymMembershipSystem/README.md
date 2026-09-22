# 🏋️ FITNESS HUB - GYM MEMBERSHIP MANAGEMENT SYSTEM

A complete, professional, and responsive dynamic web application built for college Internet Programming project submission.

---

## 🔗 Live Application Access
The application is currently compiled and **LIVE** on your local machine:
👉 **[http://localhost:8080](http://localhost:8080)**

### 🔑 Pre-Loaded Test Credentials
You can log in immediately on the live server using any of the following accounts:
- **Email:** `alex@fitnesshub.com` | **Password:** `password123`
- **Email:** `sarah@fitnesshub.com` | **Password:** `sarah2026`
- **Email:** `mike@fitnesshub.com`  | **Password:** `ironmike`

Or register a brand new user on the **Register** page!

---

## 📁 Project Structure

```
GymMembershipSystem/
├── src/main/java/com/gym/
│   ├── DBConnection.java       # JDBC database connection manager
│   ├── RegisterServlet.java     # Member registration processor
│   ├── LoginServlet.java        # Authentication & session creator
│   ├── DashboardServlet.java    # Dynamic member dashboard data fetcher
│   └── LogoutServlet.java       # Session invalidator & exit handler
├── WebContent/
│   ├── index.html               # Home Page (Hero, Plans, About, Footer)
│   ├── register.html            # Registration form with JS validation
│   ├── login.html               # Login page with error banners
│   ├── dashboard.jsp            # Dynamic JavaServer Page for member dashboard
│   ├── css/
│   │   └── style.css            # Dark professional modern gym UI design
│   ├── js/
│   │   └── script.js            # Form validation (Email, 10-digit phone, password)
│   └── WEB-INF/
│       └── web.xml              # Servlet deployment descriptor & URL mappings
├── database/
│   └── gym.sql                  # MySQL script (database & table schema + sample data)
├── server.py                    # Standalone instant demo runner for local testing
└── README.md                    # Project documentation & setup manual
```

---

## 🛠️ Technology Requirements

- **HTML5**: Structured semantic web layouts
- **CSS3**: Dark modern gym theme, glassmorphism cards, responsive flexbox & grid
- **JavaScript**: Client-side validation (Email format, 10-digit phone number, password length >= 6)
- **Java Servlet (Java 11+)**: Server-side request processing & business logic
- **JSP (JavaServer Pages)**: Dynamic rendering of logged-in member dashboard
- **MySQL Database**: Persistent storage for member accounts
- **Apache Tomcat (v9 / v10 / v11)**: Servlet web server container

---

## 🗄️ Database Setup (MySQL)

1. Open **MySQL Workbench** or **MySQL Command Line Client**.
2. Run the SQL script located in `database/gym.sql`:

```sql
CREATE DATABASE IF NOT EXISTS gym_db;
USE gym_db;

CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    membership VARCHAR(50) NOT NULL,
    join_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

INSERT INTO members (name, email, phone, password, membership, join_date, status) 
VALUES 
('Alex Johnson', 'alex@fitnesshub.com', '9876543210', 'password123', 'Yearly', CURDATE(), 'Active'),
('Sarah Connor', 'sarah@fitnesshub.com', '9123456789', 'sarah2026', 'Quarterly', CURDATE(), 'Active'),
('Mike Tyson', 'mike@fitnesshub.com', '9988776655', 'ironmike', 'Monthly', CURDATE(), 'Active');
```

---

## 💻 Eclipse IDE & Apache Tomcat Setup Instructions

### Step 1: Import Project into Eclipse
1. Open **Eclipse IDE for Enterprise Java and Web Developers**.
2. Go to **File ➔ Import ➔ General ➔ Existing Projects into Workspace**.
3. Select the `GymMembershipSystem` directory and click **Finish**.
4. Right-click project ➔ **Properties ➔ Project Facets**:
   - Check **Dynamic Web Module** (version 3.1 or 4.0).
   - Check **Java** (version 11 or 17/21).

### Step 2: Add MySQL JDBC Driver JAR
1. Download `mysql-connector-j-8.x.x.jar`.
2. Copy the `.jar` file into `WebContent/WEB-INF/lib/`.
3. Right-click project in Eclipse ➔ **Build Path ➔ Configure Build Path ➔ Libraries ➔ Add JARs** ➔ select `mysql-connector-j.jar` from `WEB-INF/lib`.

### Step 3: Configure Database Credentials
Open `src/main/java/com/gym/DBConnection.java` and update your MySQL credentials:
```java
private static final String URL = "jdbc:mysql://localhost:3306/gym_db?useSSL=false&serverTimezone=UTC";
private static final String USER = "root";     // Your MySQL username
private static final String PASSWORD = "root"; // Your MySQL password
```

### Step 4: Configure Apache Tomcat Server
1. In Eclipse, open the **Servers** tab (Window ➔ Show View ➔ Servers).
2. Click **No servers are available. Click this link to create a new server...**.
3. Select **Apache ➔ Tomcat v9.0 / v10.0 / v11.0 Server**.
4. Browse to your Apache Tomcat installation directory.
5. Add `GymMembershipSystem` to the server configured projects list.
6. Click **Finish**.

### Step 5: Run the Project
1. Right-click `GymMembershipSystem` project.
2. Select **Run As ➔ Run on Server**.
3. Select your configured Tomcat server and click **Finish**.
4. Eclipse will launch the app at `http://localhost:8080/GymMembershipSystem/`.

---

## ⚡ JavaScript Validation Rules
- **Email Validation**: Enforces standard email format regex (`user@domain.com`).
- **Phone Number Validation**: Enforces **exactly 10 numeric digits** (strips non-digits on keypress).
- **Password Validation**: Enforces a minimum length of **6 characters**.
- **Required Fields**: Prevents form submission and highlights empty input fields.

---

## 🏆 Project Submission Checklist
- [x] HTML5 structure with semantic tags
- [x] CSS3 responsive dark gym design system
- [x] Client-side JS validation
- [x] Java Servlets (`RegisterServlet`, `LoginServlet`, `DashboardServlet`, `LogoutServlet`)
- [x] PreparedStatement SQL queries & DB connection
- [x] MySQL database script (`gym.sql`)
- [x] Apache Tomcat & Eclipse setup guide
- [x] Tested & ready for college evaluation!
