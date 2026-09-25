import json
import math
from datetime import datetime, timedelta
from database import query_db, execute_db
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AdaptiveAIEngine:
    """
    AI/ML Adaptive Personalized Learning Path & Recommendation Engine.
    Combines Scikit-Learn TF-IDF vector similarity with dynamic DAG topological sorting,
    weighted skill gap classification, and performance-driven dynamic roadmap adaptation.
    """

    @staticmethod
    def classify_skill_status(mastery_score, is_prereq_missing=False):
        """
        Classifies performance score into skill status.
        """
        if is_prereq_missing:
            return "Missing Prerequisite"
        if mastery_score >= 80.0:
            return "Strong"
        elif mastery_score >= 60.0:
            return "Average"
        elif mastery_score >= 40.0:
            return "Weak"
        else:
            return "Missing Prerequisite"

    @staticmethod
    def analyze_skill_gap(user_id, career_goal_id):
        """
        Analyzes student baseline skills and test performance against target career requirements.
        Returns detailed gap breakdown with chart-friendly vectors.
        """
        profile = query_db("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,), one=True)
        if not profile:
            return None

        # Fetch career required skills
        career_reqs = query_db("""
            SELECT s.id as skill_id, s.name as skill_name, s.category, crs.required_level
            FROM career_required_skills crs
            JOIN skills s ON crs.skill_id = s.id
            WHERE crs.career_id = ?
        """, (career_goal_id,))

        # Fetch student progress
        student_progs = query_db("""
            SELECT t.skill_id, sp.status, sp.mastery_score
            FROM student_progress sp
            JOIN topics t ON sp.topic_id = t.id
            WHERE sp.user_id = ?
        """, (user_id,))

        mastery_by_skill = {}
        for sp in student_progs:
            sid = sp['skill_id']
            score = sp['mastery_score'] or 0.0
            if sid not in mastery_by_skill or score > mastery_by_skill[sid]:
                mastery_by_skill[sid] = score

        # Student current skills text (e.g., "Java Basics, Programming Fundamentals")
        user_skills_str = (profile['current_skills'] or '') + ', ' + (profile['programming_languages'] or '')
        user_skills_list = [s.strip().lower() for s in user_skills_str.split(',') if s.strip()]

        existing_skills = []
        strong_skills = []
        average_skills = []
        weak_skills = []
        missing_skills = []
        prerequisite_gaps = []

        overall_required_count = len(career_reqs)
        total_mastery_accumulated = 0.0

        for req in career_reqs:
            sid = req['skill_id']
            sname = req['skill_name']

            score = mastery_by_skill.get(sid, 0.0)

            # Check if user stated they know this skill in baseline profile if no assessment yet
            if sid not in mastery_by_skill and any(sname.lower() in us for us in user_skills_list):
                score = 70.0 # Default baseline for self-declared skills before assessment

            total_mastery_accumulated += score
            status = AdaptiveAIEngine.classify_skill_status(score, is_prereq_missing=(score < 40.0 and sid not in mastery_by_skill))

            skill_info = {
                "skill_id": sid,
                "skill_name": sname,
                "category": req['category'],
                "required_level": req['required_level'],
                "mastery_score": round(score, 1),
                "status": status
            }

            if status == "Strong":
                strong_skills.append(skill_info)
                existing_skills.append(skill_info)
            elif status == "Average":
                average_skills.append(skill_info)
                existing_skills.append(skill_info)
            elif status == "Weak":
                weak_skills.append(skill_info)
            else:
                missing_skills.append(skill_info)
                prerequisite_gaps.append(skill_info)

        # Vector Similarity matching using Scikit-Learn TF-IDF
        match_percentage = 0.0
        if career_reqs:
            vectorizer = TfidfVectorizer()
            career_skills_text = " ".join([r['skill_name'] for r in career_reqs])
            student_skills_text = " ".join([s['skill_name'] for s in strong_skills + average_skills] + user_skills_list)

            if student_skills_text.strip() and career_skills_text.strip():
                tfidf = vectorizer.fit_transform([career_skills_text, student_skills_text])
                match_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
                match_percentage = round(min(1.0, max(0.1, float(match_sim))) * 100, 1)
            else:
                match_percentage = round((len(strong_skills) + len(average_skills) * 0.6) / max(1, overall_required_count) * 100, 1)

        overall_readiness = round(total_mastery_accumulated / max(1, overall_required_count), 1)

        return {
            "career_goal_id": career_goal_id,
            "overall_readiness_percentage": overall_readiness,
            "skill_match_percentage": match_percentage,
            "counts": {
                "total_required": overall_required_count,
                "strong": len(strong_skills),
                "average": len(average_skills),
                "weak": len(weak_skills),
                "missing": len(missing_skills)
            },
            "strong_skills": strong_skills,
            "average_skills": average_skills,
            "weak_skills": weak_skills,
            "missing_skills": missing_skills,
            "prerequisite_gaps": prerequisite_gaps
        }

    @staticmethod
    def generate_personalized_roadmap(user_id, career_goal_id):
        """
        Generates or recalculates the adaptive learning path.
        Applies Topological Sorting on Topic Prerequisites, prioritizes weak topics,
        adjusts duration based on available daily study hours, and builds topic node details.
        """
        profile = query_db("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,), one=True)
        available_hours_per_day = float(profile['available_hours_per_day'] or 2.0) if profile else 2.0

        # Fetch required skills for the career
        req_skill_rows = query_db("SELECT skill_id FROM career_required_skills WHERE career_id = ?", (career_goal_id,))
        req_skill_ids = [r['skill_id'] for r in req_skill_rows]

        if not req_skill_ids:
            # Fallback: get all topics
            topics = query_db("SELECT * FROM topics ORDER BY order_index ASC")
        else:
            placeholders = ','.join('?' * len(req_skill_ids))
            topics = query_db(f"SELECT * FROM topics WHERE skill_id IN ({placeholders}) ORDER BY order_index ASC", tuple(req_skill_ids))

        if not topics:
            topics = query_db("SELECT * FROM topics ORDER BY order_index ASC")

        topic_map = {t['id']: dict(t) for t in topics}

        # Fetch prerequisites
        prereqs = query_db("SELECT topic_id, prerequisite_topic_id, dependency_type FROM prerequisites")
        adj_list = {tid: [] for tid in topic_map}
        in_degree = {tid: 0 for tid in topic_map}
        prereq_ids_by_topic = {tid: [] for tid in topic_map}

        for p in prereqs:
            tid = p['topic_id']
            pid = p['prerequisite_topic_id']
            if tid in topic_map and pid in topic_map:
                adj_list[pid].append(tid)
                in_degree[tid] += 1
                prereq_ids_by_topic[tid].append(pid)

        # Topological Sort (Kahn's Algorithm) with priority queue logic
        queue = [tid for tid in topic_map if in_degree[tid] == 0]
        sorted_topic_ids = []

        while queue:
            # Sort queue by order_index
            queue.sort(key=lambda x: topic_map[x]['order_index'])
            curr = queue.pop(0)
            sorted_topic_ids.append(curr)

            for neighbor in adj_list.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If graph has remaining unvisited nodes due to external dependencies, append them
        for tid in topic_map:
            if tid not in sorted_topic_ids:
                sorted_topic_ids.append(tid)

        # Fetch user progress for topics
        user_progress_rows = query_db("SELECT topic_id, status, mastery_score FROM student_progress WHERE user_id = ?", (user_id,))
        progress_map = {p['topic_id']: p for p in user_progress_rows}

        roadmap_nodes = []
        cumulative_hours = 0.0

        for idx, tid in enumerate(sorted_topic_ids, start=1):
            topic = topic_map[tid]
            prog = progress_map.get(tid, None)

            status = prog['status'] if prog else 'Not Started'
            mastery = prog['mastery_score'] if prog else 0.0

            # Determine Priority based on performance & dependency depth
            prereq_names = [topic_map[pid]['name'] for pid in prereq_ids_by_topic.get(tid, []) if pid in topic_map]
            
            # Check if any prerequisite is weak or missing
            prereq_unmet = False
            for pid in prereq_ids_by_topic.get(tid, []):
                pprog = progress_map.get(pid, None)
                if not pprog or pprog['mastery_score'] < 60.0:
                    prereq_unmet = True
                    break

            if status == 'Weak' or prereq_unmet:
                priority = "High (Remedial)"
                if status != 'Completed' and status != 'Mastered':
                    status = 'Weak / Prerequisites Missing' if prereq_unmet else 'Weak'
            elif status == 'Mastered' or status == 'Completed':
                priority = "Low (Completed)"
            else:
                priority = "High" if idx <= 3 else "Medium"

            est_hours = float(topic['estimated_hours'] or 4.0)
            
            # If student is weak, add 50% extra estimated hours for revision
            if status in ['Weak', 'Weak / Prerequisites Missing']:
                est_hours = round(est_hours * 1.5, 1)
            elif status in ['Mastered']:
                est_hours = 0.0 # Skip hours for mastered

            cumulative_hours += est_hours

            # Fetch recommended activities for node
            activities = query_db("SELECT id, type, title, url_or_content, estimated_mins, difficulty FROM learning_activities WHERE topic_id = ?", (tid,))
            act_list = [dict(a) for a in activities]

            roadmap_nodes.append({
                "sequence_order": idx,
                "topic_id": tid,
                "topic_name": topic['name'],
                "description": topic['description'],
                "difficulty": topic['difficulty'],
                "estimated_hours": est_hours,
                "prerequisites": prereq_names,
                "priority": priority,
                "status": status,
                "mastery_score": round(mastery, 1),
                "recommended_activities": act_list
            })

        # Calculate timeline dates
        days_needed = math.ceil(cumulative_hours / max(0.5, available_hours_per_day))
        est_completion_date = (datetime.now() + timedelta(days=days_needed)).strftime('%Y-%m-%d')

        roadmap_data = {
            "user_id": user_id,
            "career_goal_id": career_goal_id,
            "total_topics": len(roadmap_nodes),
            "completed_topics": sum(1 for n in roadmap_nodes if n['status'] in ['Mastered', 'Completed']),
            "total_estimated_hours": round(cumulative_hours, 1),
            "daily_study_hours": available_hours_per_day,
            "estimated_completion_days": days_needed,
            "estimated_completion_date": est_completion_date,
            "nodes": roadmap_nodes
        }

        # Save or update personalized_roadmaps table
        existing_rm = query_db("SELECT id FROM personalized_roadmaps WHERE user_id = ?", (user_id,), one=True)
        roadmap_json_str = json.dumps(roadmap_data)
        if existing_rm:
            execute_db("UPDATE personalized_roadmaps SET career_goal_id = ?, last_adapted_at = CURRENT_TIMESTAMP, roadmap_json = ? WHERE user_id = ?", (career_goal_id, roadmap_json_str, user_id))
        else:
            execute_db("INSERT INTO personalized_roadmaps (user_id, career_goal_id, roadmap_json) VALUES (?, ?, ?)", (user_id, career_goal_id, roadmap_json_str))

        return roadmap_data

    @staticmethod
    def adapt_roadmap_after_assessment(user_id, topic_id, score_percentage, accuracy, time_taken_seconds):
        """
        Dynamic Roadmap Engine adaptation logic called post assessment.
        Modifies topic status, unlocks/delays dependent topics, generates AI hints.
        """
        # Determine new status & mastery
        if score_percentage >= 85.0:
            status = 'Mastered'
            rec_type = 'acceleration'
            message = f"Outstanding performance! You achieved {score_percentage:.0f}% in topic assessment. Topic marked as Mastered! Accelerating roadmap schedule."
        elif score_percentage >= 60.0:
            status = 'Completed'
            rec_type = 'general'
            message = f"Good job! You passed with {score_percentage:.0f}%. Move on to the next scheduled topic in your path."
        else:
            status = 'Weak'
            rec_type = 'remedial'
            message = f"AI Adaptation Alert: Score of {score_percentage:.0f}% detected in topic assessment. Topic marked as Weak. Extra remedial exercises injected and dependent topics locked until mastery is reached."

        # Update or insert student_progress
        existing_prog = query_db("SELECT id FROM student_progress WHERE user_id = ? AND topic_id = ?", (user_id, topic_id), one=True)
        if existing_prog:
            execute_db("""
                UPDATE student_progress
                SET status = ?, mastery_score = ?, completed_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND topic_id = ?
            """, (status, score_percentage, user_id, topic_id))
        else:
            execute_db("""
                INSERT INTO student_progress (user_id, topic_id, status, mastery_score, completed_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, topic_id, status, score_percentage))

        # Insert into AI recommendations table
        topic = query_db("SELECT name FROM topics WHERE id = ?", (topic_id,), one=True)
        tname = topic['name'] if topic else "Topic"

        execute_db("""
            INSERT INTO recommendations (user_id, type, message, action_link)
            VALUES (?, ?, ?, ?)
        """, (user_id, rec_type, f"[{tname}] {message}", f"#roadmap?topic={topic_id}"))

        # Insert learning history log
        execute_db("""
            INSERT INTO learning_history (user_id, activity_type, description, score_or_metric)
            VALUES (?, 'Assessment', ?, ?)
        """, (user_id, f"Completed assessment for '{tname}'", f"{score_percentage:.0f}% (Accuracy: {accuracy:.0f}%)"))

        # Fetch profile for career_goal_id
        profile = query_db("SELECT career_goal_id FROM student_profiles WHERE user_id = ?", (user_id,), one=True)
        career_goal_id = profile['career_goal_id'] if profile and profile['career_goal_id'] else 1

        # Trigger full roadmap recalculation & adaptation
        updated_roadmap = AdaptiveAIEngine.generate_personalized_roadmap(user_id, career_goal_id)

        return {
            "status": status,
            "score_percentage": score_percentage,
            "message": message,
            "updated_roadmap": updated_roadmap
        }
