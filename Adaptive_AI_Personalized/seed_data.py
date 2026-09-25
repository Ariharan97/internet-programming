import sqlite3
import json
import os
from database import init_db, get_db_connection, create_user, get_user_by_email

def seed():
    print("Initializing Database Schema with Gamification Engine...")
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if data already seeded
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]

    if user_count == 0:
        print("Seeding Users...")
        admin_id = create_user("System Admin", "admin@example.com", "admin123", role="admin")
        student_id = create_user("Alex Mercer", "student@example.com", "student123", role="student")
        create_user("Sophia Chen", "sophia@example.com", "password123", role="student")
        create_user("Marcus Vance", "marcus@example.com", "password123", role="student")

        print("Seeding Career Goals...")
        career_goals = [
            ("Java Developer", "Master enterprise backend development using Java, Spring Boot, microservices, and database systems.", "code", "Java Backend Engineer"),
            ("Full Stack Developer", "Build end-to-end web applications with modern frontend frameworks, REST APIs, and modern databases.", "globe", "Full Stack Engineer"),
            ("Data Scientist", "Analyze data, construct predictive statistical models, and extract actionable business insights using Python and R.", "bar-chart", "Data Scientist / Data Analyst"),
            ("AI/ML Engineer", "Design and deploy deep learning models, natural language processing applications, and intelligent agent systems.", "cpu", "AI/ML Engineer"),
            ("Cybersecurity Engineer", "Protect networks, applications, and cloud systems against security vulnerabilities, malware, and cyber threats.", "shield", "Security Engineer"),
            ("Android Developer", "Build native mobile applications for Android platform using Java, Kotlin, and modern UI toolkits.", "smartphone", "Android Engineer")
        ]
        
        career_id_map = {}
        for title, desc, icon, role in career_goals:
            cur.execute("INSERT INTO career_goals (title, description, icon, target_role) VALUES (?, ?, ?, ?)", (title, desc, icon, role))
            career_id_map[title] = cur.lastrowid

        print("Seeding Skills...")
        skills = [
            ("Programming Fundamentals", "Foundational logic, variables, loops, conditionals, and algorithms", "Core"),
            ("Java Basics", "Core Java syntax, data types, control flow, and memory management", "Language"),
            ("OOP Concepts", "Encapsulation, Inheritance, Polymorphism, and Abstraction principles", "Core"),
            ("Collections & Data Structures", "Lists, Sets, Maps, Queues, Tree data structures, and Algorithmic Complexity", "Data Structures"),
            ("Exception Handling & File I/O", "Try-catch blocks, custom exceptions, file streams, and serialization", "Core"),
            ("SQL & Database Design", "Relational database concepts, normalization, queries, joins, and indexing", "Database"),
            ("JDBC Integration", "Java Database Connectivity API for relational databases", "Database"),
            ("Spring Boot Core", "Dependency Injection, Inversion of Control, and Spring Framework architecture", "Framework"),
            ("RESTful API Development", "Designing scalable REST endpoints, HTTP methods, JSON payloads, and authentication", "Web"),
            ("Full Stack Web Basics", "HTML5, CSS3, JavaScript ES6+, DOM manipulation, and responsive web design", "Web"),
            ("React & Frontend Frameworks", "Component architecture, hooks, state management, and SPA development", "Web"),
            ("Python Programming", "Syntax, data structures, list comprehensions, and standard libraries", "Language"),
            ("Data Analysis & Visualization", "Pandas, NumPy, Matplotlib, and Seaborn for data manipulation", "Data Science"),
            ("Machine Learning Algorithms", "Supervised, unsupervised, regression, classification, clustering, and Scikit-Learn", "AI/ML"),
            ("Deep Learning & Neural Networks", "TensorFlow, PyTorch, Convolutional & Recurrent Neural Networks", "AI/ML"),
            ("Android UI & Jetpack", "Activities, Fragments, Views, Layouts, ViewModel, and LiveData", "Mobile"),
            ("Network & System Security", "OSI model, cryptography, network protocols, firewalls, and penetration testing", "Security")
        ]

        skill_id_map = {}
        for name, desc, cat in skills:
            cur.execute("INSERT INTO skills (name, description, category) VALUES (?, ?, ?)", (name, desc, cat))
            skill_id_map[name] = cur.lastrowid

        print("Mapping Required Skills to Careers...")
        career_skills_data = {
            "Java Developer": [
                ("Programming Fundamentals", "Intermediate"),
                ("Java Basics", "Advanced"),
                ("OOP Concepts", "Advanced"),
                ("Collections & Data Structures", "Intermediate"),
                ("Exception Handling & File I/O", "Intermediate"),
                ("SQL & Database Design", "Intermediate"),
                ("JDBC Integration", "Intermediate"),
                ("Spring Boot Core", "Advanced"),
                ("RESTful API Development", "Advanced")
            ]
        }

        for career_title, skill_list in career_skills_data.items():
            cid = career_id_map[career_title]
            for skill_name, req_level in skill_list:
                sid = skill_id_map[skill_name]
                cur.execute("INSERT INTO career_required_skills (career_id, skill_id, required_level) VALUES (?, ?, ?)", (cid, sid, req_level))

        print("Seeding Topics...")
        topics_data = [
            ("Programming Fundamentals", "Variables, Operators, Control Flow, and Loops", "Beginner", 4.0, 1),
            ("Java Basics", "Java Syntax, JVM Architecture, and Data Types", "Beginner", 5.0, 2),
            ("OOP Concepts", "Encapsulation, Inheritance, Polymorphism, and Interfaces", "Intermediate", 8.0, 3),
            ("Collections Framework", "List, Set, Map interfaces, ArrayList, HashMap, and Iterators", "Intermediate", 6.0, 4),
            ("Exception Handling", "Checked vs Unchecked Exceptions, Try-Catch-Finally, Custom Exceptions", "Intermediate", 4.0, 5),
            ("File Handling & Streams", "Byte/Character Streams, File I/O, and Serialization", "Intermediate", 4.0, 6),
            ("SQL Fundamentals", "DML, DDL, SELECT, Joins, Aggregation, and Database Normalization", "Beginner", 6.0, 7),
            ("JDBC Integration", "Connecting Java to Relational DBs, PreparedStatements, Transaction Management", "Intermediate", 5.0, 8),
            ("Spring Boot Core", "Spring IoC Container, Dependency Injection, Annotations, and Beans", "Advanced", 10.0, 9),
            ("REST API Development", "Controllers, ResponseEntities, DTOs, Validation, and Postman Testing", "Advanced", 8.0, 10),
            ("Project Development", "Building a full enterprise Java Spring Boot backend service", "Advanced", 15.0, 11),
            ("Interview Preparation", "Mock technical interviews, Java coding patterns, and system design basics", "Advanced", 10.0, 12)
        ]

        topic_id_map = {}
        for name, desc, diff, hours, ord_idx in topics_data:
            sid = skill_id_map.get("Programming Fundamentals")
            if "Java" in name or "OOP" in name or "Collections" in name or "Exception" in name or "File" in name:
                sid = skill_id_map.get("Java Basics")
            if "OOP" in name:
                sid = skill_id_map.get("OOP Concepts")
            if "Collections" in name:
                sid = skill_id_map.get("Collections & Data Structures")
            if "SQL" in name:
                sid = skill_id_map.get("SQL & Database Design")
            if "JDBC" in name:
                sid = skill_id_map.get("JDBC Integration")
            if "Spring" in name:
                sid = skill_id_map.get("Spring Boot Core")
            if "REST" in name:
                sid = skill_id_map.get("RESTful API Development")

            cur.execute(
                "INSERT INTO topics (skill_id, name, description, difficulty, estimated_hours, order_index) VALUES (?, ?, ?, ?, ?, ?)",
                (sid, name, desc, diff, hours, ord_idx)
            )
            topic_id_map[name] = cur.lastrowid

        print("Seeding Prerequisites...")
        prereqs = [
            ("Java Basics", "Programming Fundamentals", "Strict"),
            ("OOP Concepts", "Java Basics", "Strict"),
            ("Collections Framework", "OOP Concepts", "Strict"),
            ("Exception Handling", "Java Basics", "Strict"),
            ("File Handling & Streams", "Exception Handling", "Recommended"),
            ("JDBC Integration", "Java Basics", "Strict"),
            ("JDBC Integration", "SQL Fundamentals", "Strict"),
            ("Spring Boot Core", "OOP Concepts", "Strict"),
            ("Spring Boot Core", "JDBC Integration", "Strict"),
            ("REST API Development", "Spring Boot Core", "Strict"),
            ("Project Development", "REST API Development", "Strict"),
            ("Interview Preparation", "Project Development", "Recommended")
        ]

        for topic_name, prereq_name, dep_type in prereqs:
            if topic_name in topic_id_map and prereq_name in topic_id_map:
                tid = topic_id_map[topic_name]
                pid = topic_id_map[prereq_name]
                cur.execute("INSERT INTO prerequisites (topic_id, prerequisite_topic_id, dependency_type) VALUES (?, ?, ?)", (tid, pid, dep_type))

        print("Seeding Assessments & Questions...")
        for tname, tid in topic_id_map.items():
            cur.execute("INSERT INTO assessments (topic_id, title, time_limit_mins, passing_score) VALUES (?, ?, 15, 70)", (tid, f"{tname} Skill Verification Assessment"))
            aid = cur.lastrowid

            q_list = [
                ("mcq", f"Which of the following is a primary principle of {tname}?", json.dumps(["Encapsulation & Abstraction", "Direct RAM deletion", "Static execution", "None of these"]), "Encapsulation & Abstraction", "Encapsulation hides internal details while exposing interfaces.", "Beginner", 10),
                ("mcq", f"What is the best practice when handling operations in {tname}?", json.dumps(["Handle exceptions gracefully and write modular code", "Ignore log outputs", "Use global variables", "Hardcode DB passwords"]), "Handle exceptions gracefully and write modular code", "Proper exception handling maintains software stability.", "Intermediate", 10),
                ("coding", f"Select the correct code structure for {tname}:", json.dumps(["public class Solution { public static void main(String[] args) {} }", "function solution() {}", "def run(): pass", "void main()"]), "public class Solution { public static void main(String[] args) {} }", "Standard Java main entry point.", "Advanced", 15)
            ]

            for qtype, qtext, options, correct, expl, diff, pts in q_list:
                cur.execute(
                    "INSERT INTO questions (assessment_id, type, question_text, options_json, correct_answer, explanation, difficulty, points) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (aid, qtype, qtext, options, correct, expl, diff, pts)
                )

        print("Seeding Learning Activities...")
        for tname, tid in topic_id_map.items():
            activities = [
                ("video", f"Mastering {tname}: Comprehensive Guide", "https://youtube.com", 35, "Beginner"),
                ("reading", f"{tname} Conceptual Documentation", "https://docs.oracle.com", 20, "Beginner"),
                ("practice_questions", f"{tname} Practice Quiz", "internal_quiz", 25, "Intermediate"),
                ("coding_exercise", f"{tname} Coding Lab", "internal_lab", 40, "Intermediate"),
                ("mini_project", f"Build a Mini Portfolio Project applying {tname}", "internal_project", 90, "Advanced")
            ]
            for atype, atitle, content, mins, diff in activities:
                cur.execute(
                    "INSERT INTO learning_activities (topic_id, type, title, url_or_content, estimated_mins, difficulty) VALUES (?, ?, ?, ?, ?, ?)",
                    (tid, atype, atitle, content, mins, diff)
                )

        print("Seeding Sample Student Profiles...")
        java_dev_id = career_id_map["Java Developer"]
        cur.execute("""
            INSERT INTO student_profiles (
                user_id, academic_year, department, cgpa, prior_experience, career_goal_id, target_role,
                current_skills, programming_languages, technical_subjects, academic_background,
                learning_interests, available_hours_per_day, preferred_learning_style, target_completion_date
            ) VALUES (?, '4th Year / Senior', 'Computer Science Engineering', 3.75,
                'Coursework in Java & Web Dev', ?, 'Java Backend Engineer',
                'Programming Fundamentals, Java Basics', 'Java, SQL', 'Data Structures', 'B.Tech CS',
                'Spring Boot, APIs', 3.0, 'Practical', DATE('now', '+90 days'))
        """, (student_id, java_dev_id))

    # Always ensure Gamification Catalogs exist (Levels, Badges, Rewards)
    print("Seeding Gamification Levels Catalog...")
    levels_data = [
        (1, "Beginner", 0, 99, "seedling"),
        (2, "Explorer", 100, 249, "compass"),
        (3, "Learner", 250, 499, "book"),
        (4, "Practitioner", 500, 999, "laptop-code"),
        (5, "Skilled Learner", 1000, 1499, "certificate"),
        (6, "Advanced Learner", 1500, 2499, "graduation-cap"),
        (7, "Expert Learner", 2500, 3999, "brain"),
        (8, "Master Learner", 4000, 5999, "crown"),
        (9, "Learning Champion", 6000, 9999, "trophy"),
        (10, "Career Ready", 10000, 999999, "rocket")
    ]
    for lvl, name, min_xp, max_xp, icon in levels_data:
        cur.execute("INSERT OR REPLACE INTO levels (level_number, level_name, min_xp, max_xp, icon) VALUES (?, ?, ?, ?, ?)",
                    (lvl, name, min_xp, max_xp, icon))

    print("Seeding Badges Catalog...")
    badges_data = [
        ("FIRST_STEP", "First Step", "Complete your first learning activity", "rocket", 50, 25, "General"),
        ("FIRST_LESSON", "First Lesson", "Complete your first lesson", "book-open", 50, 25, "General"),
        ("QUIZ_MASTER", "Quiz Master", "Complete 10 quizzes", "vial", 150, 50, "Quiz"),
        ("PERFECT_SCORE", "Perfect Score", "Get 100% in a quiz assessment", "star", 100, 50, "Quiz"),
        ("STREAK_7", "7 Day Streak", "Maintain a 7-day learning streak", "fire", 100, 50, "Streak"),
        ("STREAK_30", "30 Day Streak", "Maintain a 30-day learning streak", "fire-burner", 500, 200, "Streak"),
        ("CODER", "Coder", "Complete 10 coding challenges", "code", 150, 75, "Coding"),
        ("KNOWLEDGE_SEEKER", "Knowledge Seeker", "Complete 25 learning activities", "brain", 200, 100, "General"),
        ("FAST_LEARNER", "Fast Learner", "Complete 5 activities in one day", "bolt", 100, 50, "General"),
        ("ROADMAP_HERO", "Roadmap Hero", "Complete your first roadmap milestone", "diagram-project", 150, 75, "Roadmap"),
        ("CAREER_READY", "Career Ready", "Master all required skills for your selected career", "trophy", 500, 250, "Roadmap"),
        ("IMPROVEMENT_MASTER", "Improvement Master", "Improve an assessment score by 20% or more", "chart-line", 100, 50, "Quiz"),
        ("SKILL_HUNTER", "Skill Hunter", "Complete 5 weak-skill improvement activities", "bullseye", 150, 75, "AI"),
        ("CONSISTENT_LEARNER", "Consistent Learner", "Maintain a 60-day learning streak", "crown", 1000, 500, "Streak")
    ]
    for code, title, desc, icon, bxp, bcoins, cat in badges_data:
        cur.execute("""
            INSERT INTO badges (code, title, description, icon, bonus_xp, bonus_coins, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET title=excluded.title, description=excluded.description, bonus_xp=excluded.bonus_xp, bonus_coins=excluded.bonus_coins
        """, (code, title, desc, icon, bxp, bcoins, cat))

    print("Seeding Virtual Reward Shop Catalog...")
    rewards_data = [
        ("Streak Shield", "Protects your active daily learning streak if you miss 1 day", "shield", 500, "shield-halved", 1),
        ("2X XP Booster", "Doubles all earned XP for 1 hour of active learning", "xp_booster", 750, "bolt", 2),
        ("Cyberpunk Profile Theme", "Unlocks sleek neon cyberpunk accent styling", "theme", 200, "palette", 1),
        ("Special Master Profile Badge", "Displays a golden star badge on your profile and leaderboard", "badge", 300, "star", 1)
    ]
    for title, desc, rtype, cost, icon, eff in rewards_data:
        cur.execute("""
            INSERT INTO rewards (title, description, type, cost_coins, icon, effect_value)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING
        """, (title, desc, rtype, cost, icon, eff))

    # Give sample student initial XP, streak & coin ledger
    cur.execute("SELECT id FROM users WHERE email = 'student@example.com'")
    srow = cur.fetchone()
    if srow:
        sid = srow[0]
        # Seed initial XP transactions
        cur.execute("SELECT COUNT(*) FROM xp_transactions WHERE user_id = ?", (sid,))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO xp_transactions (user_id, amount, source_type, description) VALUES (?, 150, 'milestone', 'Initial Profile Setup')", (sid,))
            cur.execute("INSERT INTO xp_transactions (user_id, amount, source_type, description) VALUES (?, 100, 'quiz', 'Completed Java Basics Quiz')", (sid,))
            cur.execute("INSERT INTO learning_coins (user_id, balance) VALUES (?, 350) ON CONFLICT DO NOTHING", (sid,))
            cur.execute("INSERT INTO learning_streaks (user_id, current_streak, longest_streak, last_activity_date, streak_shields) VALUES (?, 5, 5, DATE('now'), 1) ON CONFLICT DO NOTHING", (sid,))

    conn.commit()
    conn.close()
    print("Database & Gamification Catalogs successfully seeded!")

if __name__ == "__main__":
    seed()
