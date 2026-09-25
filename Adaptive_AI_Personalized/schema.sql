-- Database Schema for Adaptive AI-Based Personalized Learning Path System with Gamification & LearnMate AI Chatbot

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student', -- 'student' or 'admin'
    is_leaderboard_hidden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_profiles (
    user_id INTEGER PRIMARY KEY,
    academic_year TEXT,
    department TEXT,
    cgpa REAL,
    prior_experience TEXT,
    career_goal_id INTEGER,
    target_role TEXT,
    current_skills TEXT,
    programming_languages TEXT,
    technical_subjects TEXT,
    academic_background TEXT,
    learning_interests TEXT,
    available_hours_per_day REAL DEFAULT 2.0,
    preferred_learning_style TEXT DEFAULT 'Practical',
    target_completion_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (career_goal_id) REFERENCES career_goals(id)
);

CREATE TABLE IF NOT EXISTS career_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    target_role TEXT
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS career_required_skills (
    career_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    required_level TEXT DEFAULT 'Intermediate',
    PRIMARY KEY (career_id, skill_id),
    FOREIGN KEY (career_id) REFERENCES career_goals(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    difficulty TEXT DEFAULT 'Beginner',
    estimated_hours REAL DEFAULT 4.0,
    order_index INTEGER DEFAULT 1,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prerequisites (
    topic_id INTEGER NOT NULL,
    prerequisite_topic_id INTEGER NOT NULL,
    dependency_type TEXT DEFAULT 'Strict',
    PRIMARY KEY (topic_id, prerequisite_topic_id),
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    time_limit_mins INTEGER DEFAULT 15,
    passing_score REAL DEFAULT 70.0,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    type TEXT DEFAULT 'mcq',
    question_text TEXT NOT NULL,
    options_json TEXT,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    difficulty TEXT DEFAULT 'Beginner',
    points INTEGER DEFAULT 10,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessment_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    assessment_id INTEGER NOT NULL,
    score_percentage REAL NOT NULL,
    accuracy REAL NOT NULL,
    time_taken_seconds INTEGER,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic_performance_json TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    url_or_content TEXT,
    estimated_mins INTEGER DEFAULT 30,
    difficulty TEXT DEFAULT 'Beginner',
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS student_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Not Started',
    mastery_score REAL DEFAULT 0.0,
    completed_at TIMESTAMP,
    UNIQUE(user_id, topic_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS personalized_roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    career_goal_id INTEGER NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_adapted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    roadmap_json TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (career_goal_id) REFERENCES career_goals(id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT DEFAULT 'remedial',
    message TEXT NOT NULL,
    action_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    description TEXT NOT NULL,
    score_or_metric TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- GAMIFICATION TABLES
CREATE TABLE IF NOT EXISTS xp_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS levels (
    level_number INTEGER PRIMARY KEY,
    level_name TEXT NOT NULL,
    min_xp INTEGER NOT NULL,
    max_xp INTEGER NOT NULL,
    icon TEXT
);

CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    bonus_xp INTEGER DEFAULT 100,
    bonus_coins INTEGER DEFAULT 50,
    category TEXT DEFAULT 'General'
);

CREATE TABLE IF NOT EXISTS student_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    target_count INTEGER DEFAULT 1,
    category TEXT DEFAULT 'General',
    reward_xp INTEGER DEFAULT 200,
    reward_coins INTEGER DEFAULT 50
);

CREATE TABLE IF NOT EXISTS student_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    current_count INTEGER DEFAULT 0,
    is_completed INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    UNIQUE(user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_value INTEGER DEFAULT 1,
    reward_xp INTEGER DEFAULT 30,
    reward_coins INTEGER DEFAULT 15,
    is_personalized INTEGER DEFAULT 0,
    user_id INTEGER,
    for_date DATE DEFAULT (DATE('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS weekly_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_value INTEGER DEFAULT 5,
    reward_xp INTEGER DEFAULT 250,
    reward_coins INTEGER DEFAULT 100,
    for_week TEXT DEFAULT (strftime('%Y-%W', 'now'))
);

CREATE TABLE IF NOT EXISTS challenge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    challenge_type TEXT NOT NULL,
    challenge_id INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    is_completed INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    UNIQUE(user_id, challenge_type, challenge_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_streaks (
    user_id INTEGER PRIMARY KEY,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    streak_shields INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_coins (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS coin_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL,
    cost_coins INTEGER NOT NULL,
    icon TEXT NOT NULL,
    effect_value INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS student_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reward_id INTEGER NOT NULL,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reward_id) REFERENCES rewards(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS active_multipliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    multiplier_value REAL DEFAULT 2.0,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================================================
-- LEARNMATE AI CHATBOT TABLES
-- ==========================================================================

CREATE TABLE IF NOT EXISTS chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT 'Learning Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    sender TEXT NOT NULL, -- 'user' or 'bot'
    agent_type TEXT DEFAULT 'MentorAgent', -- 'MentorAgent', 'SkillAnalyst', 'QuizAgent', 'RoadmapAgent', 'CareerAgent', 'CodeMentor'
    message TEXT NOT NULL,
    metadata_json TEXT, -- JSON for structured cards, quizzes, code review stats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mistake_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER,
    concept_name TEXT NOT NULL,
    mistake_count INTEGER DEFAULT 1,
    last_made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, concept_name),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quest_name TEXT NOT NULL,
    target_skill TEXT NOT NULL,
    missions_json TEXT NOT NULL, -- JSON array of missions
    reward_xp INTEGER DEFAULT 150,
    reward_coins INTEGER DEFAULT 30,
    is_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mentor_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interaction_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
