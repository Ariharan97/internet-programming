import json
from datetime import datetime, timedelta, date
from database import query_db, execute_db

class GamificationEngine:
    """
    Central Gamification & AI Motivation Engine.
    Handles Server-Validated XP transactions, Level progression, Streaks, Shields,
    Badges, Achievements, AI-Driven Challenges, Virtual Learning Coins, and Leaderboards.
    """

    LEVEL_CONFIG = [
        {"level": 1, "name": "Beginner", "min_xp": 0, "max_xp": 99, "icon": "seedling"},
        {"level": 2, "name": "Explorer", "min_xp": 100, "max_xp": 249, "icon": "compass"},
        {"level": 3, "name": "Learner", "min_xp": 250, "max_xp": 499, "icon": "book"},
        {"level": 4, "name": "Practitioner", "min_xp": 500, "max_xp": 999, "icon": "laptop-code"},
        {"level": 5, "name": "Skilled Learner", "min_xp": 1000, "max_xp": 1499, "icon": "certificate"},
        {"level": 6, "name": "Advanced Learner", "min_xp": 1500, "max_xp": 2499, "icon": "graduation-cap"},
        {"level": 7, "name": "Expert Learner", "min_xp": 2500, "max_xp": 3999, "icon": "brain"},
        {"level": 8, "name": "Master Learner", "min_xp": 4000, "max_xp": 5999, "icon": "crown"},
        {"level": 9, "name": "Learning Champion", "min_xp": 6000, "max_xp": 9999, "icon": "trophy"},
        {"level": 10, "name": "Career Ready", "min_xp": 10000, "max_xp": 999999, "icon": "rocket"}
    ]

    STREAK_MILESTONES = {
        3: 30,
        7: 100,
        14: 200,
        30: 500,
        60: 1000,
        90: 2000
    }

    @staticmethod
    def get_user_xp(user_id):
        row = query_db("SELECT SUM(amount) as total_xp FROM xp_transactions WHERE user_id = ?", (user_id,), one=True)
        return int(row['total_xp'] or 0) if row else 0

    @staticmethod
    def get_level_info(xp):
        for lvl in GamificationEngine.LEVEL_CONFIG:
            if lvl['min_xp'] <= xp <= lvl['max_xp']:
                return lvl
        return GamificationEngine.LEVEL_CONFIG[-1]

    @staticmethod
    def get_active_multiplier(user_id):
        row = query_db("""
            SELECT multiplier_value FROM active_multipliers
            WHERE user_id = ? AND expires_at > CURRENT_TIMESTAMP
            ORDER BY expires_at DESC LIMIT 1
        """, (user_id,), one=True)
        return float(row['multiplier_value']) if row else 1.0

    @staticmethod
    def award_xp(user_id, base_amount, source_type, description, source_id=None):
        """
        Awards XP to a student, checks active 2X boosters, calculates Level-ups,
        records notifications, and triggers badge evaluation.
        """
        if source_id and source_type in ['badge', 'milestone', 'career_completion']:
            existing = query_db("SELECT id FROM xp_transactions WHERE user_id = ? AND source_type = ? AND source_id = ?",
                                (user_id, source_type, str(source_id)), one=True)
            if existing:
                return {'earned_xp': 0, 'leveled_up': False}

        multiplier = GamificationEngine.get_active_multiplier(user_id)
        final_xp = int(base_amount * multiplier)

        if final_xp <= 0:
            return {'earned_xp': 0, 'leveled_up': False}

        xp_before = GamificationEngine.get_user_xp(user_id)
        lvl_before = GamificationEngine.get_level_info(xp_before)

        execute_db("""
            INSERT INTO xp_transactions (user_id, amount, source_type, source_id, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, final_xp, source_type, str(source_id) if source_id else None, description))

        coins_earned = max(1, final_xp // 5)
        GamificationEngine.award_coins(user_id, coins_earned, f"XP Award Bonus for {source_type}")

        xp_after = xp_before + final_xp
        lvl_after = GamificationEngine.get_level_info(xp_after)

        leveled_up = False
        new_level_info = None

        if lvl_after['level'] > lvl_before['level']:
            leveled_up = True
            new_level_info = lvl_after
            execute_db("""
                INSERT INTO notifications (user_id, type, title, message)
                VALUES (?, 'level_up', ?, ?)
            """, (user_id, f"🎉 LEVEL UP! Level {lvl_after['level']}",
                  f"Congratulations! You reached Level {lvl_after['level']} - '{lvl_after['name']}'! Keep up the brilliant learning!"))

        unlocked_badges = []
        if source_type != 'badge':
            unlocked_badges = GamificationEngine.check_and_unlock_badges(user_id)

        return {
            'earned_xp': final_xp,
            'multiplier': multiplier,
            'total_xp': xp_after,
            'leveled_up': leveled_up,
            'new_level': new_level_info,
            'unlocked_badges': unlocked_badges
        }

    @staticmethod
    def get_user_coins(user_id):
        row = query_db("SELECT balance FROM learning_coins WHERE user_id = ?", (user_id,), one=True)
        return int(row['balance']) if row else 0

    @staticmethod
    def award_coins(user_id, amount, description):
        existing = query_db("SELECT balance FROM learning_coins WHERE user_id = ?", (user_id,), one=True)
        if existing:
            execute_db("UPDATE learning_coins SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        else:
            execute_db("INSERT INTO learning_coins (user_id, balance) VALUES (?, ?)", (user_id, amount))

        execute_db("""
            INSERT INTO coin_transactions (user_id, amount, type, description)
            VALUES (?, ?, 'earn', ?)
        """, (user_id, amount, description))

    @staticmethod
    def update_streak(user_id):
        today = date.today()
        streak_row = query_db("SELECT * FROM learning_streaks WHERE user_id = ?", (user_id,), one=True)

        if not streak_row:
            execute_db("""
                INSERT INTO learning_streaks (user_id, current_streak, longest_streak, last_activity_date, streak_shields)
                VALUES (?, 1, 1, ?, 0)
            """, (user_id, today.strftime('%Y-%m-%d')))
            GamificationEngine.award_xp(user_id, 30, 'daily_goal', "Completed First Day Learning Goal!")
            return {'streak': 1, 'longest_streak': 1, 'shield_used': False, 'bonus_xp': 30}

        last_date_str = streak_row['last_activity_date']
        curr_streak = streak_row['current_streak'] or 1
        longest_streak = streak_row['longest_streak'] or 1
        shields = streak_row['streak_shields'] or 0

        if not last_date_str:
            last_date = today - timedelta(days=2)
        else:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()

        days_diff = (today - last_date).days

        if days_diff == 0:
            return {'streak': curr_streak, 'longest_streak': longest_streak, 'shield_used': False, 'bonus_xp': 0}

        shield_used = False
        bonus_xp = 0

        if days_diff == 1:
            curr_streak += 1
        elif days_diff == 2 and shields > 0:
            shields -= 1
            curr_streak += 1
            shield_used = True
            execute_db("""
                INSERT INTO notifications (user_id, type, title, message)
                VALUES (?, 'streak', '🛡️ Streak Shield Activated!', 'You missed yesterday, but your Streak Shield saved your 15+ day learning streak!')
            """, (user_id,))
        else:
            curr_streak = 1

        if curr_streak > longest_streak:
            longest_streak = curr_streak

        execute_db("""
            UPDATE learning_streaks
            SET current_streak = ?, longest_streak = ?, last_activity_date = ?, streak_shields = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (curr_streak, longest_streak, today.strftime('%Y-%m-%d'), shields, user_id))

        if curr_streak in GamificationEngine.STREAK_MILESTONES:
            bonus_xp = GamificationEngine.STREAK_MILESTONES[curr_streak]
            GamificationEngine.award_xp(user_id, bonus_xp, 'streak', f"🔥 Reached {curr_streak}-Day Streak Milestone!")

        return {
            'streak': curr_streak,
            'longest_streak': longest_streak,
            'shield_used': shield_used,
            'bonus_xp': bonus_xp
        }

    @staticmethod
    def check_and_unlock_badges(user_id):
        all_badges = query_db("SELECT * FROM badges")
        unlocked_rows = query_db("SELECT badge_id FROM student_badges WHERE user_id = ?", (user_id,))
        already_unlocked_ids = set(r['badge_id'] for r in unlocked_rows)

        act_count = query_db("SELECT COUNT(*) as cnt FROM learning_history WHERE user_id = ?", (user_id,), one=True)['cnt']
        quiz_count = query_db("SELECT COUNT(*) as cnt FROM assessment_results WHERE user_id = ?", (user_id,), one=True)['cnt']
        perfect_count = query_db("SELECT COUNT(*) as cnt FROM assessment_results WHERE user_id = ? AND score_percentage >= 100", (user_id,), one=True)['cnt']
        
        streak_row = query_db("SELECT current_streak FROM learning_streaks WHERE user_id = ?", (user_id,), one=True)
        streak = streak_row['current_streak'] if streak_row else 0

        mastered_count = query_db("SELECT COUNT(*) as cnt FROM student_progress WHERE user_id = ? AND status = 'Mastered'", (user_id,), one=True)['cnt']

        newly_unlocked = []

        for b in all_badges:
            if b['id'] in already_unlocked_ids:
                continue

            should_unlock = False
            code = b['code']

            if code == 'FIRST_STEP' and act_count >= 1:
                should_unlock = True
            elif code == 'FIRST_LESSON' and act_count >= 1:
                should_unlock = True
            elif code == 'QUIZ_MASTER' and quiz_count >= 10:
                should_unlock = True
            elif code == 'PERFECT_SCORE' and perfect_count >= 1:
                should_unlock = True
            elif code == 'STREAK_7' and streak >= 7:
                should_unlock = True
            elif code == 'STREAK_30' and streak >= 30:
                should_unlock = True
            elif code == 'KNOWLEDGE_SEEKER' and act_count >= 25:
                should_unlock = True
            elif code == 'ROADMAP_HERO' and mastered_count >= 1:
                should_unlock = True
            elif code == 'CAREER_READY' and mastered_count >= 10:
                should_unlock = True

            if should_unlock:
                execute_db("INSERT OR IGNORE INTO student_badges (user_id, badge_id) VALUES (?, ?)", (user_id, b['id']))
                GamificationEngine.award_xp(user_id, b['bonus_xp'], 'badge', f"🏆 Badge Unlocked: {b['title']}", source_id=b['id'])
                GamificationEngine.award_coins(user_id, b['bonus_coins'], f"Badge Bonus: {b['title']}")

                execute_db("""
                    INSERT INTO notifications (user_id, type, title, message)
                    VALUES (?, 'badge', ?, ?)
                """, (user_id, f"🏆 NEW BADGE: {b['title']}", f"{b['description']} (+{b['bonus_xp']} XP, +{b['bonus_coins']} Coins)"))

                newly_unlocked.append(dict(b))

        return newly_unlocked

    @staticmethod
    def generate_personalized_ai_challenges(user_id):
        profile = query_db("SELECT career_goal_id FROM student_profiles WHERE user_id = ?", (user_id,), one=True)
        cid = profile['career_goal_id'] if profile and profile['career_goal_id'] else 1

        from ai_engine import AdaptiveAIEngine
        gap = AdaptiveAIEngine.analyze_skill_gap(user_id, cid)
        
        weak_skills = gap.get('weak_skills', []) + gap.get('missing_skills', [])
        today_str = date.today().strftime('%Y-%m-%d')

        existing = query_db("SELECT id FROM daily_challenges WHERE for_date = ? AND (user_id IS NULL OR user_id = ?)", (today_str, user_id))
        if existing:
            return

        execute_db("""
            INSERT INTO daily_challenges (title, description, target_type, target_value, reward_xp, reward_coins, is_personalized, user_id, for_date)
            VALUES ('Daily Lesson Explorer', 'Complete at least 1 learning activity today', 'lesson', 1, 30, 15, 0, ?, ?)
        """, (user_id, today_str))

        execute_db("""
            INSERT INTO daily_challenges (title, description, target_type, target_value, reward_xp, reward_coins, is_personalized, user_id, for_date)
            VALUES ('Quiz Crusher', 'Complete 1 topic diagnostic assessment with 70%+ score', 'quiz', 1, 40, 20, 0, ?, ?)
        """, (user_id, today_str))

        if weak_skills:
            target_skill = weak_skills[0]['skill_name']
            execute_db("""
                INSERT INTO daily_challenges (title, description, target_type, target_value, reward_xp, reward_coins, is_personalized, user_id, for_date)
                VALUES (?, ?, 'weak_topic', 1, 150, 50, 1, ?, ?)
            """, (f"AI Special Bounty: Master {target_skill}", f"Complete remedial activities and raise score in {target_skill} above 70%", user_id, today_str))
        else:
            execute_db("""
                INSERT INTO daily_challenges (title, description, target_type, target_value, reward_xp, reward_coins, is_personalized, user_id, for_date)
                VALUES ('System Mastery', 'Review 1 advanced roadmap topic', 'study_time', 1, 60, 30, 0, ?, ?)
            """, (user_id, today_str))

    @staticmethod
    def get_gamification_profile(user_id):
        xp = GamificationEngine.get_user_xp(user_id)
        level_info = GamificationEngine.get_level_info(xp)
        coins = GamificationEngine.get_user_coins(user_id)
        streak = GamificationEngine.update_streak(user_id)

        xp_in_level = xp - level_info['min_xp']
        xp_needed = level_info['max_xp'] - level_info['min_xp'] + 1
        level_pct = min(100, max(0, int((xp_in_level / max(1, xp_needed)) * 100)))

        unlocked_badges = query_db("SELECT COUNT(*) as cnt FROM student_badges WHERE user_id = ?", (user_id,), one=True)['cnt']
        total_badges = query_db("SELECT COUNT(*) as cnt FROM badges", one=True)['cnt']

        active_mult = GamificationEngine.get_active_multiplier(user_id)
        ls_row = query_db("SELECT streak_shields FROM learning_streaks WHERE user_id = ?", (user_id,), one=True)

        return {
            'user_id': user_id,
            'total_xp': xp,
            'coins': coins,
            'level': level_info['level'],
            'level_name': level_info['name'],
            'level_icon': level_info['icon'],
            'min_xp': level_info['min_xp'],
            'max_xp': level_info['max_xp'],
            'xp_to_next_level': max(0, level_info['max_xp'] + 1 - xp),
            'level_progress_percentage': level_pct,
            'current_streak': streak['streak'],
            'longest_streak': streak['longest_streak'],
            'streak_shields': ls_row['streak_shields'] if ls_row else 0,
            'badges_unlocked_count': unlocked_badges,
            'total_badges_count': total_badges,
            'active_multiplier': active_mult
        }

    @staticmethod
    def redeem_reward(user_id, reward_id):
        reward = query_db("SELECT * FROM rewards WHERE id = ?", (reward_id,), one=True)
        if not reward:
            return {'success': False, 'message': 'Reward item not found.'}

        cost = reward['cost_coins']
        user_coins = GamificationEngine.get_user_coins(user_id)

        if user_coins < cost:
            return {'success': False, 'message': f"Insufficient Learning Coins. Required: {cost} coins, You have: {user_coins} coins."}

        execute_db("UPDATE learning_coins SET balance = balance - ? WHERE user_id = ?", (cost, user_id))
        execute_db("""
            INSERT INTO coin_transactions (user_id, amount, type, description)
            VALUES (?, ?, 'spend', ?)
        """, (user_id, cost, f"Redeemed Shop Item: {reward['title']}"))

        rtype = reward['type']
        if rtype == 'shield':
            execute_db("UPDATE learning_streaks SET streak_shields = streak_shields + 1 WHERE user_id = ?", (user_id,))
        elif rtype == 'xp_booster':
            expires_at = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            execute_db("INSERT INTO active_multipliers (user_id, multiplier_value, expires_at) VALUES (?, 2.0, ?)", (user_id, expires_at))

        execute_db("INSERT INTO student_rewards (user_id, reward_id) VALUES (?, ?)", (user_id, reward_id))

        return {
            'success': True,
            'message': f"Successfully purchased '{reward['title']}'! Coins remaining: {user_coins - cost}.",
            'new_balance': user_coins - cost
        }

    @staticmethod
    def get_leaderboard(timeframe='all_time', limit=20):
        query = """
            SELECT u.id, u.name, ls.current_streak,
                   COALESCE(SUM(xp.amount), 0) as total_xp,
                   (SELECT COUNT(*) FROM student_badges sb WHERE sb.user_id = u.id) as badge_count
            FROM users u
            LEFT JOIN xp_transactions xp ON u.id = xp.user_id
            LEFT JOIN learning_streaks ls ON u.id = ls.user_id
            WHERE u.is_leaderboard_hidden = 0 AND u.role = 'student'
            GROUP BY u.id
            ORDER BY total_xp DESC
            LIMIT ?
        """
        rows = query_db(query, (limit,))
        result = []
        for rank, r in enumerate(rows, start=1):
            xp = int(r['total_xp'] or 0)
            lvl = GamificationEngine.get_level_info(xp)
            result.append({
                'rank': rank,
                'user_id': r['id'],
                'name': r['name'],
                'total_xp': xp,
                'level': lvl['level'],
                'level_name': lvl['name'],
                'streak': r['current_streak'] or 0,
                'badge_count': r['badge_count'] or 0
            })
        return result
