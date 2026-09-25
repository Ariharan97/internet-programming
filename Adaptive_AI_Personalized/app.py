import os
import json
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file
from database import (
    init_db, query_db, execute_db, create_user,
    get_user_by_email, get_user_by_id, verify_password
)
from ai_engine import AdaptiveAIEngine
from gamification import GamificationEngine
from chatbot import LearnMateAI, StudentContextExtractor

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'super_secret_antigravity_key_learning_path'

# Ensure database is initialized on startup
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'database.db')):
    from seed_data import seed
    seed()

def get_current_user_id():
    return session.get('user_id', 2)

# Page Routing
@app.route('/')
def index():
    return render_template('index.html')

# Direct Code Download Endpoint
@app.route('/download')
def download_code_zip():
    zip_path = r'C:\Users\dell\OneDrive\Desktop\Adaptive_AI_Personalized_Learning_System.zip'
    if not os.path.exists(zip_path):
        zip_path = os.path.join(os.path.dirname(__file__), 'Adaptive_AI_Personalized_Learning_System.zip')
    
    if not os.path.exists(zip_path):
        return jsonify({'error': 'ZIP file not found on server.'}), 404

    return send_file(
        zip_path,
        as_attachment=True,
        download_name='Adaptive_AI_Personalized_Learning_System.zip',
        mimetype='application/zip'
    )

# 1. Auth Endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400

    existing = get_user_by_email(email)
    if existing:
        return jsonify({'error': 'An account with this email already exists.'}), 400

    user_id = create_user(name, email, password, role)
    session['user_id'] = user_id

    if role == 'student':
        execute_db("""
            INSERT INTO student_profiles (
                user_id, academic_year, department, cgpa, prior_experience, career_goal_id, target_role,
                current_skills, programming_languages, technical_subjects, academic_background,
                learning_interests, available_hours_per_day, preferred_learning_style, target_completion_date
            ) VALUES (?, ?, ?, ?, ?, 1, 'Java Backend Developer', 'Programming Fundamentals', 'Java', 'CS Basics', 'Engineering', 'Backend APIs', 2.0, 'Practical', DATE('now', '+90 days'))
        """, (user_id, data.get('academic_year', '1st Year'), data.get('department', 'Computer Science'), float(data.get('cgpa', 3.5)), data.get('prior_experience', 'Beginner')))

        GamificationEngine.award_xp(user_id, 100, 'milestone', 'Welcome to Adaptive AI Platform!')
        GamificationEngine.award_coins(user_id, 100, 'Welcome Coin Bonus')
        GamificationEngine.update_streak(user_id)
        AdaptiveAIEngine.generate_personalized_roadmap(user_id, 1)

    return jsonify({'message': 'Registration successful', 'user_id': user_id, 'role': role})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')

    user = get_user_by_email(email)
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    session['user_id'] = user['id']
    if user['role'] == 'student':
        GamificationEngine.update_streak(user['id'])

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    uid = get_current_user_id()
    user = get_user_by_id(uid)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    profile = query_db("SELECT * FROM student_profiles WHERE user_id = ?", (uid,), one=True)
    g_profile = GamificationEngine.get_gamification_profile(uid)

    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'is_leaderboard_hidden': user['is_leaderboard_hidden'] if 'is_leaderboard_hidden' in user.keys() else 0
        },
        'profile': dict(profile) if profile else None,
        'gamification': g_profile
    })

# 2. Student Profile & Goal Settings
@app.route('/api/career-goals', methods=['GET'])
def get_career_goals():
    goals = query_db("SELECT * FROM career_goals")
    return jsonify([dict(g) for g in goals])

@app.route('/api/student/profile', methods=['GET', 'POST'])
def student_profile():
    uid = get_current_user_id()
    if request.method == 'POST':
        data = request.json or {}
        career_goal_id = int(data.get('career_goal_id', 1))
        target_role = data.get('target_role', 'Software Engineer')
        academic_year = data.get('academic_year', '4th Year')
        department = data.get('department', 'Computer Science')
        cgpa = float(data.get('cgpa', 3.5))
        prior_experience = data.get('prior_experience', '')
        current_skills = data.get('current_skills', '')
        programming_languages = data.get('programming_languages', '')
        technical_subjects = data.get('technical_subjects', '')
        academic_background = data.get('academic_background', '')
        learning_interests = data.get('learning_interests', '')
        available_hours = float(data.get('available_hours_per_day', 2.0))
        learning_style = data.get('preferred_learning_style', 'Practical')
        target_date = data.get('target_completion_date', None)

        existing = query_db("SELECT user_id FROM student_profiles WHERE user_id = ?", (uid,), one=True)
        if existing:
            execute_db("""
                UPDATE student_profiles SET
                    career_goal_id = ?, target_role = ?, academic_year = ?, department = ?,
                    cgpa = ?, prior_experience = ?, current_skills = ?, programming_languages = ?,
                    technical_subjects = ?, academic_background = ?, learning_interests = ?,
                    available_hours_per_day = ?, preferred_learning_style = ?, target_completion_date = ?
                WHERE user_id = ?
            """, (career_goal_id, target_role, academic_year, department, cgpa, prior_experience,
                  current_skills, programming_languages, technical_subjects, academic_background,
                  learning_interests, available_hours, learning_style, target_date, uid))
        else:
            execute_db("""
                INSERT INTO student_profiles (
                    user_id, career_goal_id, target_role, academic_year, department, cgpa, prior_experience,
                    current_skills, programming_languages, technical_subjects, academic_background,
                    learning_interests, available_hours_per_day, preferred_learning_style, target_completion_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, career_goal_id, target_role, academic_year, department, cgpa, prior_experience,
                  current_skills, programming_languages, technical_subjects, academic_background,
                  learning_interests, available_hours, learning_style, target_date))

        AdaptiveAIEngine.generate_personalized_roadmap(uid, career_goal_id)
        GamificationEngine.generate_personalized_ai_challenges(uid)

        return jsonify({'message': 'Profile updated successfully'})

    profile = query_db("SELECT * FROM student_profiles WHERE user_id = ?", (uid,), one=True)
    return jsonify(dict(profile) if profile else {})

# 3. AI Skill Gap Analysis
@app.route('/api/skill-gap-analysis', methods=['GET'])
def get_skill_gap_analysis():
    uid = get_current_user_id()
    profile = query_db("SELECT career_goal_id FROM student_profiles WHERE user_id = ?", (uid,), one=True)
    career_goal_id = profile['career_goal_id'] if profile and profile['career_goal_id'] else 1

    gap_data = AdaptiveAIEngine.analyze_skill_gap(uid, career_goal_id)
    return jsonify(gap_data or {})

# 4. Roadmap Endpoint
@app.route('/api/roadmap', methods=['GET'])
def get_roadmap():
    uid = get_current_user_id()
    profile = query_db("SELECT career_goal_id FROM student_profiles WHERE user_id = ?", (uid,), one=True)
    career_goal_id = profile['career_goal_id'] if profile and profile['career_goal_id'] else 1

    roadmap = AdaptiveAIEngine.generate_personalized_roadmap(uid, career_goal_id)
    return jsonify(roadmap)

# 5. Assessment Endpoint & Gamified Submit
@app.route('/api/assessment/<int:topic_id>', methods=['GET'])
def get_assessment(topic_id):
    assessment = query_db("SELECT * FROM assessments WHERE topic_id = ?", (topic_id,), one=True)
    if not assessment:
        topic = query_db("SELECT name FROM topics WHERE id = ?", (topic_id,), one=True)
        tname = topic['name'] if topic else "Topic"
        aid = execute_db("INSERT INTO assessments (topic_id, title, time_limit_mins, passing_score) VALUES (?, ?, 15, 70)", (topic_id, f"{tname} Skill Verification Assessment"))
        execute_db("INSERT INTO questions (assessment_id, type, question_text, options_json, correct_answer, explanation, difficulty) VALUES (?, 'mcq', ?, ?, ?, ?, 'Beginner')",
                   (aid, f"What is the foundational concept of {tname}?", json.dumps(["Core Mechanics", "Syntax Sugar", "Compiler Flag", "Deprecation Warning"]), "Core Mechanics", "Core mechanics form the backbone of this topic."))
        assessment = query_db("SELECT * FROM assessments WHERE id = ?", (aid,), one=True)

    questions = query_db("SELECT id, type, question_text, options_json, difficulty, points FROM questions WHERE assessment_id = ?", (assessment['id'],))
    q_list = []
    for q in questions:
        q_dict = dict(q)
        if q_dict['options_json']:
            q_dict['options'] = json.loads(q_dict['options_json'])
        q_list.append(q_dict)

    return jsonify({
        'assessment': dict(assessment),
        'questions': q_list
    })

@app.route('/api/assessment/submit', methods=['POST'])
def submit_assessment():
    uid = get_current_user_id()
    data = request.json or {}
    assessment_id = data.get('assessment_id')
    answers = data.get('answers', {})
    time_taken = data.get('time_taken_seconds', 120)

    assessment = query_db("SELECT * FROM assessments WHERE id = ?", (assessment_id,), one=True)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404

    questions = query_db("SELECT * FROM questions WHERE assessment_id = ?", (assessment_id,))
    total_points = sum(q['points'] for q in questions)
    user_points = 0
    correct_count = 0

    evaluations = []
    for q in questions:
        qid = str(q['id'])
        user_ans = str(answers.get(qid, '')).strip().lower()
        correct_ans = str(q['correct_answer']).strip().lower()

        is_correct = (user_ans == correct_ans)
        if is_correct:
            user_points += q['points']
            correct_count += 1

        evaluations.append({
            'question_id': q['id'],
            'question_text': q['question_text'],
            'user_answer': answers.get(qid, ''),
            'correct_answer': q['correct_answer'],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })

    score_pct = round((user_points / max(1, total_points)) * 100, 1)
    accuracy = round((correct_count / max(1, len(questions))) * 100, 1)

    prev_result = query_db("SELECT score_percentage FROM assessment_results WHERE user_id = ? AND assessment_id = ? ORDER BY evaluated_at DESC LIMIT 1", (uid, assessment_id), one=True)
    improved_bonus_earned = False
    if prev_result and (score_pct - float(prev_result['score_percentage'])) >= 20.0:
        improved_bonus_earned = True

    execute_db("""
        INSERT INTO assessment_results (user_id, assessment_id, score_percentage, accuracy, time_taken_seconds, topic_performance_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (uid, assessment_id, score_pct, accuracy, time_taken, json.dumps(evaluations)))

    xp_reward = GamificationEngine.award_xp(uid, 30, 'quiz', f"Completed Assessment '{assessment['title']}'", source_id=assessment_id)
    
    bonus_xp = 0
    if score_pct >= 90.0:
        bonus_res = GamificationEngine.award_xp(uid, 50, 'quiz_bonus', "Scored 90%+ in Assessment!")
        bonus_xp += bonus_res['earned_xp']
    elif score_pct >= 70.0:
        bonus_res = GamificationEngine.award_xp(uid, 20, 'quiz_bonus', "Scored 70%+ in Assessment!")
        bonus_xp += bonus_res['earned_xp']

    if improved_bonus_earned:
        imp_res = GamificationEngine.award_xp(uid, 30, 'improvement', "Improved assessment score by 20%+")
        bonus_xp += imp_res['earned_xp']

    streak_info = GamificationEngine.update_streak(uid)
    adaptation_res = AdaptiveAIEngine.adapt_roadmap_after_assessment(uid, assessment['topic_id'], score_pct, accuracy, time_taken)

    if score_pct >= 85.0:
        GamificationEngine.award_xp(uid, 100, 'milestone', f"Mastered Topic Node #{assessment['topic_id']}", source_id=assessment['topic_id'])

    g_profile = GamificationEngine.get_gamification_profile(uid)

    return jsonify({
        'score_percentage': score_pct,
        'accuracy': accuracy,
        'time_taken_seconds': time_taken,
        'evaluations': evaluations,
        'adaptation': adaptation_res,
        'gamification_rewards': {
            'earned_xp': xp_reward['earned_xp'] + bonus_xp,
            'total_xp': g_profile['total_xp'],
            'level': g_profile['level'],
            'level_name': g_profile['level_name'],
            'leveled_up': xp_reward['leveled_up'],
            'streak': streak_info['streak'],
            'unlocked_badges': xp_reward.get('unlocked_badges', [])
        }
    })

# 6. Dashboard Endpoint
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    uid = get_current_user_id()

    user = get_user_by_id(uid)
    profile = query_db("SELECT * FROM student_profiles WHERE user_id = ?", (uid,), one=True)
    career_goal_id = profile['career_goal_id'] if profile and profile['career_goal_id'] else 1
    career = query_db("SELECT title, target_role FROM career_goals WHERE id = ?", (career_goal_id,), one=True)

    gap = AdaptiveAIEngine.analyze_skill_gap(uid, career_goal_id)
    roadmap = AdaptiveAIEngine.generate_personalized_roadmap(uid, career_goal_id)
    g_profile = GamificationEngine.get_gamification_profile(uid)

    recommendations = query_db("SELECT * FROM recommendations WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (uid,))
    recent_history = query_db("SELECT * FROM learning_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (uid,))

    nodes = roadmap.get('nodes', [])
    current_node = next((n for n in nodes if n['status'] not in ['Mastered', 'Completed']), nodes[0] if nodes else None)
    todays_tasks = current_node['recommended_activities'][:3] if current_node else []

    return jsonify({
        'user': {
            'name': user['name'] if user else "Student",
            'email': user['email'] if user else ""
        },
        'career_goal': career['title'] if career else "Java Developer",
        'target_role': career['target_role'] if career else "Developer",
        'overall_progress_percentage': gap.get('overall_readiness_percentage', 0),
        'skill_counts': gap.get('counts', {}),
        'current_topic': current_node,
        'todays_tasks': todays_tasks,
        'available_hours_per_day': profile['available_hours_per_day'] if profile else 2.0,
        'gamification': g_profile,
        'recommendations': [dict(r) for r in recommendations],
        'recent_history': [dict(h) for h in recent_history],
        'roadmap_summary': {
            'total_topics': roadmap.get('total_topics', 0),
            'completed_topics': roadmap.get('completed_topics', 0),
            'estimated_completion_date': roadmap.get('estimated_completion_date', '')
        }
    })

# 7. Gamified Activity Completion
@app.route('/api/activity/complete', methods=['POST'])
def complete_activity():
    uid = get_current_user_id()
    data = request.json or {}
    activity_id = data.get('activity_id')

    act = query_db("SELECT * FROM learning_activities WHERE id = ?", (activity_id,), one=True)
    if not act:
        return jsonify({'error': 'Activity not found'}), 404

    execute_db("""
        INSERT INTO learning_history (user_id, activity_type, description, score_or_metric)
        VALUES (?, 'Activity Completed', ?, ?)
    """, (uid, f"Completed {act['type'].title()}: {act['title']}", f"{act['estimated_mins']} mins"))

    xp_res = GamificationEngine.award_xp(uid, 20, 'lesson', f"Completed Activity '{act['title']}'", source_id=activity_id)
    GamificationEngine.award_coins(uid, 5, f"Completed Lesson '{act['title']}'")
    GamificationEngine.update_streak(uid)

    g_profile = GamificationEngine.get_gamification_profile(uid)

    return jsonify({
        'message': 'Activity marked complete!',
        'earned_xp': xp_res['earned_xp'],
        'coins_earned': 5,
        'total_xp': g_profile['total_xp'],
        'leveled_up': xp_res['leveled_up']
    })

# 8. Learning History Endpoint
@app.route('/api/learning-history', methods=['GET'])
def get_learning_history():
    uid = get_current_user_id()
    history = query_db("SELECT * FROM learning_history WHERE user_id = ? ORDER BY timestamp DESC", (uid,))
    return jsonify([dict(h) for h in history])

# GAMIFICATION API ENDPOINTS
@app.route('/api/gamification/dashboard', methods=['GET'])
def get_gamification_dashboard():
    uid = get_current_user_id()
    g_profile = GamificationEngine.get_gamification_profile(uid)
    return jsonify(g_profile)

@app.route('/api/gamification/badges', methods=['GET'])
def get_gamification_badges():
    uid = get_current_user_id()
    all_badges = query_db("SELECT * FROM badges")
    unlocked = query_db("SELECT badge_id, unlocked_at FROM student_badges WHERE user_id = ?", (uid,))
    unlocked_map = {r['badge_id']: r['unlocked_at'] for r in unlocked}

    result = []
    for b in all_badges:
        bd = dict(b)
        bd['is_unlocked'] = b['id'] in unlocked_map
        bd['unlocked_at'] = unlocked_map.get(b['id'], None)
        result.append(bd)

    return jsonify(result)

@app.route('/api/gamification/challenges', methods=['GET'])
def get_gamification_challenges():
    uid = get_current_user_id()
    GamificationEngine.generate_personalized_ai_challenges(uid)

    today_str = date.today().strftime('%Y-%m-%d')
    challenges = query_db("SELECT * FROM daily_challenges WHERE for_date = ? AND (user_id IS NULL OR user_id = ?)", (today_str, uid))

    user_prog = query_db("SELECT challenge_id, current_value, is_completed FROM challenge_progress WHERE user_id = ? AND challenge_type = 'daily'", (uid,))
    prog_map = {p['challenge_id']: p for p in user_prog}

    res = []
    for c in challenges:
        cd = dict(c)
        prog = prog_map.get(c['id'], None)
        cd['current_value'] = prog['current_value'] if prog else 0
        cd['is_completed'] = prog['is_completed'] if prog else 0
        res.append(cd)

    return jsonify(res)

@app.route('/api/gamification/complete-challenge', methods=['POST'])
def complete_challenge():
    uid = get_current_user_id()
    data = request.json or {}
    cid = data.get('challenge_id')

    c = query_db("SELECT * FROM daily_challenges WHERE id = ?", (cid,), one=True)
    if not c:
        return jsonify({'error': 'Challenge not found'}), 404

    existing = query_db("SELECT id FROM challenge_progress WHERE user_id = ? AND challenge_type = 'daily' AND challenge_id = ?", (uid, cid), one=True)
    if existing:
        execute_db("UPDATE challenge_progress SET current_value = target_value, is_completed = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?", (existing['id'],))
    else:
        execute_db("INSERT INTO challenge_progress (user_id, challenge_type, challenge_id, current_value, is_completed, completed_at) VALUES (?, 'daily', ?, ?, 1, CURRENT_TIMESTAMP)", (uid, cid, c['target_value']))

    xp_res = GamificationEngine.award_xp(uid, c['reward_xp'], 'challenge', f"Completed Daily Challenge '{c['title']}'", source_id=cid)
    GamificationEngine.award_coins(uid, c['reward_coins'], f"Challenge Bonus '{c['title']}'")

    return jsonify({
        'message': 'Challenge completed!',
        'earned_xp': xp_res['earned_xp'],
        'earned_coins': c['reward_coins']
    })

@app.route('/api/gamification/leaderboard', methods=['GET'])
def get_leaderboard_endpoint():
    tf = request.args.get('timeframe', 'all_time')
    board = GamificationEngine.get_leaderboard(timeframe=tf, limit=20)
    return jsonify(board)

@app.route('/api/gamification/toggle-leaderboard', methods=['POST'])
def toggle_leaderboard_privacy():
    uid = get_current_user_id()
    data = request.json or {}
    hide = 1 if data.get('hide') else 0
    execute_db("UPDATE users SET is_leaderboard_hidden = ? WHERE id = ?", (hide, uid))
    return jsonify({'message': 'Leaderboard privacy settings updated', 'is_hidden': hide})

@app.route('/api/gamification/rewards', methods=['GET'])
def get_rewards():
    uid = get_current_user_id()
    all_rewards = query_db("SELECT * FROM rewards")
    purchased = query_db("SELECT reward_id FROM student_rewards WHERE user_id = ?", (uid,))
    purchased_ids = set(p['reward_id'] for p in purchased)

    res = []
    for r in all_rewards:
        rd = dict(r)
        rd['is_owned'] = r['id'] in purchased_ids
        res.append(rd)

    coins = GamificationEngine.get_user_coins(uid)
    return jsonify({'rewards': res, 'user_coins': coins})

@app.route('/api/gamification/redeem-reward', methods=['POST'])
def redeem_reward_endpoint():
    uid = get_current_user_id()
    data = request.json or {}
    reward_id = data.get('reward_id')

    res = GamificationEngine.redeem_reward(uid, reward_id)
    if not res['success']:
        return jsonify(res), 400
    return jsonify(res)

@app.route('/api/gamification/notifications', methods=['GET'])
def get_notifications():
    uid = get_current_user_id()
    notifs = query_db("SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC", (uid,))
    return jsonify([dict(n) for n in notifs])

@app.route('/api/gamification/notifications/read', methods=['POST'])
def mark_notifications_read():
    uid = get_current_user_id()
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (uid,))
    return jsonify({'message': 'Notifications marked read'})

# ==========================================================================
# LEARNMATE AI CHATBOT REST ENDPOINTS
# ==========================================================================

@app.route('/api/chat', methods=['POST'])
def chat_prompt():
    uid = get_current_user_id()
    data = request.json or {}
    prompt = data.get('prompt', '').strip()
    session_id = data.get('session_id', None)
    page_ctx = data.get('page_context', 'dashboard')

    if not prompt:
        return jsonify({'error': 'Prompt cannot be empty.'}), 400

    res = LearnMateAI.process_message(uid, prompt, session_id=session_id, page_context=page_ctx)
    return jsonify(res)

@app.route('/api/chat/greeting', methods=['GET'])
def chat_greeting():
    uid = get_current_user_id()
    greeting = LearnMateAI.generate_contextual_greeting(uid)
    return jsonify({'greeting': greeting})

@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    uid = get_current_user_id()
    session_id = request.args.get('session_id')

    if not session_id:
        latest = query_db("SELECT id FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (uid,), one=True)
        session_id = latest['id'] if latest else None

    if not session_id:
        return jsonify({'messages': []})

    msgs = query_db("SELECT id, sender, agent_type, message, metadata_json, created_at FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
    res = []
    for m in msgs:
        md = dict(m)
        md['metadata'] = json.loads(md['metadata_json']) if md['metadata_json'] else None
        res.append(md)

    return jsonify({'session_id': session_id, 'messages': res})

@app.route('/api/chat/sessions', methods=['GET'])
def chat_sessions():
    uid = get_current_user_id()
    sessions = query_db("SELECT id, title, created_at, updated_at FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC", (uid,))
    return jsonify([dict(s) for s in sessions])

@app.route('/api/chat/new', methods=['POST'])
def chat_new_session():
    uid = get_current_user_id()
    sid = execute_db("INSERT INTO chat_sessions (user_id, title) VALUES (?, 'New Mentor Chat')", (uid,))
    greeting = LearnMateAI.generate_contextual_greeting(uid)
    execute_db("INSERT INTO chat_messages (session_id, user_id, sender, agent_type, message) VALUES (?, ?, 'bot', 'MentorAgent', ?)", (sid, uid, greeting))

    return jsonify({'session_id': sid, 'greeting': greeting})

@app.route('/api/chat/context', methods=['GET'])
def chat_student_context():
    uid = get_current_user_id()
    ctx = StudentContextExtractor.get_full_context(uid)
    return jsonify(ctx or {})

@app.route('/api/chat/feedback', methods=['POST'])
def chat_feedback():
    uid = get_current_user_id()
    data = request.json or {}
    message_id = data.get('message_id')
    feedback = data.get('feedback', 'like')

    execute_db("INSERT INTO mentor_interactions (user_id, interaction_type, summary) VALUES (?, ?, ?)",
               (uid, f"feedback_{feedback}", f"Feedback on message {message_id}: {feedback}"))
    return jsonify({'message': 'Thank you for your feedback!'})

# Admin Analytics Endpoint
@app.route('/api/admin/analytics', methods=['GET'])
def admin_analytics():
    total_students = query_db("SELECT COUNT(*) as count FROM users WHERE role = 'student'", one=True)['count']
    total_courses = query_db("SELECT COUNT(*) as count FROM career_goals", one=True)['count']
    total_topics = query_db("SELECT COUNT(*) as count FROM topics", one=True)['count']
    total_questions = query_db("SELECT COUNT(*) as count FROM questions", one=True)['count']

    topic_stats = query_db("""
        SELECT t.name, AVG(sp.mastery_score) as avg_mastery, COUNT(sp.user_id) as student_count
        FROM topics t
        LEFT JOIN student_progress sp ON t.id = sp.topic_id
        GROUP BY t.id
        ORDER BY avg_mastery ASC
        LIMIT 10
    """)

    students_list = query_db("""
        SELECT u.id, u.name, u.email, sp.academic_year, sp.department, sp.cgpa, cg.title as career_goal
        FROM users u
        LEFT JOIN student_profiles sp ON u.id = sp.user_id
        LEFT JOIN career_goals cg ON sp.career_goal_id = cg.id
        WHERE u.role = 'student'
    """)

    return jsonify({
        'total_students': total_students,
        'total_courses': total_courses,
        'total_topics': total_topics,
        'total_questions': total_questions,
        'weakest_topics': [dict(s) for s in topic_stats],
        'students': [dict(st) for st in students_list]
    })

if __name__ == '__main__':
    print("Starting Adaptive AI Personalized Learning Server with LearnMate AI on http://127.0.0.1:5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
