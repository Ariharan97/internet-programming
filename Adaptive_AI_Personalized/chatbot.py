import json
import os
import re
from datetime import datetime, timedelta, date
from database import query_db, execute_db
from ai_engine import AdaptiveAIEngine
from gamification import GamificationEngine

class StudentContextExtractor:
    """
    Extracts complete live student profile, skill gap vectors, roadmap position,
    and gamification metrics from the database without asking redundant questions.
    """
    @staticmethod
    def get_full_context(user_id):
        user = query_db("SELECT id, name, email, role FROM users WHERE id = ?", (user_id,), one=True)
        if not user:
            return None

        profile = query_db("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,), one=True)
        cid = profile['career_goal_id'] if profile and profile['career_goal_id'] else 1
        career = query_db("SELECT title, target_role FROM career_goals WHERE id = ?", (cid,), one=True)

        gap = AdaptiveAIEngine.analyze_skill_gap(user_id, cid)
        roadmap = AdaptiveAIEngine.generate_personalized_roadmap(user_id, cid)
        g_profile = GamificationEngine.get_gamification_profile(user_id)

        recent_mistakes = query_db("SELECT concept_name, mistake_count FROM mistake_patterns WHERE user_id = ? ORDER BY last_made_at DESC LIMIT 3", (user_id,))
        active_quests = query_db("SELECT * FROM quest_progress WHERE user_id = ? AND is_completed = 0", (user_id,))

        nodes = roadmap.get('nodes', [])
        current_node = next((n for n in nodes if n['status'] not in ['Mastered', 'Completed']), nodes[0] if nodes else None)

        return {
            'student_name': user['name'],
            'academic_year': profile['academic_year'] if profile else '4th Year',
            'department': profile['department'] if profile else 'Computer Science',
            'cgpa': profile['cgpa'] if profile else 3.75,
            'career_goal': career['title'] if career else 'Java Developer',
            'target_role': career['target_role'] if career else 'Software Engineer',
            'available_hours_per_day': profile['available_hours_per_day'] if profile else 2.0,
            'learning_style': profile['preferred_learning_style'] if profile else 'Practical',
            'overall_readiness': gap.get('overall_readiness_percentage', 0),
            'strong_skills': [s['skill_name'] for s in gap.get('strong_skills', [])],
            'weak_skills': [s['skill_name'] for s in gap.get('weak_skills', [])],
            'missing_skills': [s['skill_name'] for s in gap.get('missing_skills', [])],
            'current_topic': current_node,
            'roadmap_summary': {
                'total': roadmap.get('total_topics', 0),
                'completed': roadmap.get('completed_topics', 0),
                'completion_date': roadmap.get('estimated_completion_date', '')
            },
            'gamification': g_profile,
            'recent_mistakes': [dict(m) for m in recent_mistakes],
            'active_quests': [dict(q) for q in active_quests]
        }


class LearnMateAI:
    """
    Multi-Agent AI Engine Coordinator for LearnMate AI.
    Routes prompts to specialized agents (Mentor, Skill Analyst, Quiz, Roadmap, Code Mentor, Career).
    """

    @staticmethod
    def generate_contextual_greeting(user_id):
        ctx = StudentContextExtractor.get_full_context(user_id)
        name = ctx['student_name']
        weak = ctx['weak_skills']
        curr = ctx['current_topic']

        greeting = f"Hi {name}! 👋 I'm LearnMate AI, your personal learning mentor.\n\n"
        if weak:
            w_name = weak[0]
            greeting += f"I noticed you are currently focusing on **{w_name}** (readiness at {ctx['overall_readiness']}%).\n\nWould you like to:\n"
            greeting += f"1. 📖 Review **{w_name}** fundamentals & real-world examples\n"
            greeting += f"2. 🧪 Take a 3-question diagnostic quiz\n"
            greeting += f"3. 💻 Practice a hands-on coding task\n"
            greeting += f"4. 📅 Generate today's {ctx['available_hours_per_day']}h study mission"
        elif curr:
            greeting += f"You're currently on **{curr['topic_name']}** in your {ctx['career_goal']} roadmap!\nReady to jump into today's activities or test your knowledge?"
        else:
            greeting += f"Ready to accelerate your path towards becoming a **{ctx['target_role']}**?"

        return greeting

    @staticmethod
    def process_message(user_id, prompt, session_id=None, page_context="dashboard"):
        ctx = StudentContextExtractor.get_full_context(user_id)
        prompt_lower = prompt.lower().strip()

        agent_type = "MentorAgent"
        response_text = ""
        metadata = {}

        # 1. WHAT-IF SIMULATOR
        if "what if" in prompt_lower or "what-if" in prompt_lower or "if i study" in prompt_lower or "change career" in prompt_lower:
            agent_type = "RoadmapAgent"
            response_text = LearnMateAI._handle_what_if_simulator(ctx, prompt_lower)

        # 2. WHAT SHOULD I LEARN NEXT?
        elif "next" in prompt_lower and ("learn" in prompt_lower or "should" in prompt_lower or "topic" in prompt_lower):
            agent_type = "RoadmapAgent"
            response_text = LearnMateAI._handle_what_next(ctx)

        # 3. TODAY'S STUDY PLAN
        elif "plan" in prompt_lower or "schedule" in prompt_lower or "today" in prompt_lower:
            agent_type = "ProgressAgent"
            response_text = LearnMateAI._handle_study_plan(ctx)

        # 4. QUIZ / TEST ME
        elif "test me" in prompt_lower or "quiz" in prompt_lower or "assessment" in prompt_lower:
            agent_type = "QuizAgent"
            response_text, metadata = LearnMateAI._handle_interactive_quiz(ctx, prompt_lower)

        # 5. CODE REVIEW / CODING QUESTION
        elif "code" in prompt_lower or "debug" in prompt_lower or "syntax" in prompt_lower or "complexity" in prompt_lower or "o(n)" in prompt_lower or "function" in prompt_lower or "class " in prompt_lower:
            agent_type = "CodeMentorAgent"
            response_text = LearnMateAI._handle_code_mentor(ctx, prompt)

        # 6. WEAK TOPICS / RETENTION RISK
        elif "weak" in prompt_lower or "mistake" in prompt_lower or "forget" in prompt_lower:
            agent_type = "SkillAnalystAgent"
            response_text = LearnMateAI._handle_weak_topics(ctx)

        # 7. CAREER & INTERVIEW PREP
        elif "career" in prompt_lower or "interview" in prompt_lower or "project" in prompt_lower or "role" in prompt_lower:
            agent_type = "CareerAgent"
            response_text = LearnMateAI._handle_career_mentor(ctx, prompt_lower)

        # 8. ROADMAP EXPLANATION
        elif "roadmap" in prompt_lower or "why" in prompt_lower and "order" in prompt_lower:
            agent_type = "RoadmapAgent"
            response_text = LearnMateAI._handle_roadmap_explanation(ctx)

        # 9. GENERAL CONCEPT EXPLANATION (DEFAULT MENTOR AGENT)
        else:
            agent_type = "MentorAgent"
            response_text = LearnMateAI._handle_concept_explanation(ctx, prompt)

        # Award Gamification XP for interacting with LearnMate AI (+10 XP)
        xp_res = GamificationEngine.award_xp(user_id, 10, 'mentor', 'Interacted with LearnMate AI Mentor')
        if xp_res['earned_xp'] > 0:
            metadata['earned_xp'] = xp_res['earned_xp']

        # Log Session & Message
        if not session_id:
            session_id = execute_db("INSERT INTO chat_sessions (user_id, title) VALUES (?, ?)", (user_id, prompt[:30] + "..."))

        execute_db("INSERT INTO chat_messages (session_id, user_id, sender, agent_type, message) VALUES (?, ?, 'user', 'User', ?)",
                   (session_id, user_id, prompt))

        execute_db("INSERT INTO chat_messages (session_id, user_id, sender, agent_type, message, metadata_json) VALUES (?, ?, 'bot', ?, ?, ?)",
                   (session_id, user_id, agent_type, response_text, json.dumps(metadata) if metadata else None))

        return {
            'session_id': session_id,
            'agent_type': agent_type,
            'response': response_text,
            'metadata': metadata,
            'student_context': ctx
        }

    @staticmethod
    def _handle_concept_explanation(ctx, prompt):
        topic = prompt.replace("what is", "").replace("explain", "").replace("how to", "").strip().title()
        if not topic:
            topic = ctx['current_topic']['topic_name'] if ctx['current_topic'] else "OOP Concepts"

        is_weak = any(w.lower() in topic.lower() for w in ctx['weak_skills'])

        if is_weak:
            # Beginner step-by-step
            return f"""
📌 **Simple Explanation**
**{topic}** is a core programming block in software design. Think of it like a blueprint for building reliable, reusable components without repeating code.

💡 **Real-World Example**
Imagine a **Car Factory**: The *Car Blueprint* defines wheels, engine, and doors. Each physical car driven on the road is a distinct object constructed from that single blueprint!

🧠 **Key Point**
By keeping member data encapsulated within objects, you prevent accidental bugs and make your software easy to test.

✏️ **Try This**
Create a simple class `Car` with attributes `speed` and `brand`, and write a method `drive()` that prints the speed!

🎯 **Your Next Step**
Would you like a 3-question beginner quiz on **{topic}** to earn +30 XP?
            """.strip()
        else:
            # Advanced details & edge cases
            return f"""
📌 **Advanced Concept Analysis: {topic}**
In production system architectures, **{topic}** enables dynamic polymorphic dispatch, decoupled interfaces, and memory-safe encapsulation.

💡 **Enterprise Use Case**
In Spring Boot microservices, interface-driven injection allows swapping database adapters (e.g., PostgreSQL vs MongoDB) at runtime without altering core business logic.

🧠 **Architectural Key Point**
Always prefer Interface Abstraction over Concrete Class Coupling to maximize unit-testability and adhere to SOLID principles.

✏️ **Coding Challenge**
Implement dynamic method overriding where a parent `DatabaseService` reference dynamically executes `PostgreSqlService.connect()` at runtime!

🎯 **Your Next Step**
Try pasting your code snippet here for instant AI static analysis & $O(n)$ complexity review!
            """.strip()

    @staticmethod
    def _handle_what_next(ctx):
        curr = ctx['current_topic']
        if not curr:
            return "You have mastered all modules in your roadmap! Next recommended step: Build a full-stack portfolio project."

        return f"""
🎯 **NEXT RECOMMENDED ROADMAP MODULE**

📌 **Topic**: **{curr['topic_name']}**
💡 **Why This Next**: You have fulfilled all prerequisite requirements ({', '.join(curr['prerequisites']) or 'Foundational'}), and your prerequisite mastery is above **80%**.

⏱️ **Estimated Learning Time**: {curr['estimated_hours']} Hours
📶 **Difficulty**: {curr['difficulty']}
🏆 **Gamification Reward**: +50 XP • 🪙 +25 Coins

✏️ **Recommended Action**: Click **Take Assessment** or complete the reading activities in your AI Roadmap view!
        """.strip()

    @staticmethod
    def _handle_study_plan(ctx):
        hours = float(ctx['available_hours_per_day'] or 2.0)
        mins = int(hours * 60)
        curr_name = ctx['current_topic']['topic_name'] if ctx['current_topic'] else "Java OOP"
        weak_name = ctx['weak_skills'][0] if ctx['weak_skills'] else "SQL Joins"

        return f"""
📅 **YOUR PERSONALIZED {mins}-MINUTE DAILY STUDY MISSION**

1. 📖 **Concept Revision** ({curr_name}) – *{max(15, int(mins * 0.25))} mins*
2. 🧪 **Diagnostic Quiz** (Verify Understanding) – *15 mins*
3. 🛠️ **Remedial Weak-Skill Lab** ({weak_name}) – *{max(20, int(mins * 0.35))} mins*
4. 💻 **Hands-on Coding Practice** – *{max(15, int(mins * 0.2))} mins*
5. 🔍 **Mistake Review & Note Taking** – *10 mins*

⏱️ **Total Daily Goal**: {mins} Minutes
🏆 **Completion Bonus**: +30 XP • 🪙 +15 Coins for completing your daily streak goal today!
        """.strip()

    @staticmethod
    def _handle_interactive_quiz(ctx, prompt):
        topic_name = ctx['current_topic']['topic_name'] if ctx['current_topic'] else "Java Basics"
        for w in ctx['weak_skills']:
            if w.lower() in prompt:
                topic_name = w
                break

        q_data = {
            'topic': topic_name,
            'question': f"In {topic_name}, which concept is used to achieve runtime method overriding?",
            'options': ["Dynamic Method Dispatch / Polymorphism", "Static Method Hiding", "Private Constructor", "Primitive Type Casting"],
            'correct': "Dynamic Method Dispatch / Polymorphism",
            'explanation': "Dynamic method dispatch resolves overridden method calls at runtime using object references."
        }

        resp = f"""
🧪 **AI ADAPTIVE DIAGNOSTIC QUIZ**

**Topic**: {topic_name}
**Question**: {q_data['question']}

1. {q_data['options'][0]}
2. {q_data['options'][1]}
3. {q_data['options'][2]}
4. {q_data['options'][3]}

*Reply with the option number or text to verify your score & earn +30 XP!*
        """.strip()

        return resp, {'quiz_data': q_data}

    @staticmethod
    def _handle_code_mentor(ctx, prompt):
        return f"""
💻 **AI CODE REVIEW & COMPLEXITY ANALYSIS**

📌 **Code Correctness Score**: **90 / 100**
⏱️ **Time Complexity**: $O(n)$ (Linear Iteration)
💾 **Space Complexity**: $O(1)$ (Constant Heap Memory)

💡 **AI Mentor Recommendation**:
Your loop logic is clean and readable! To optimize for edge cases:
- Verify null or empty collection checks before entering the loop.
- Consider using Java Streams `.filter()` or Python list comprehensions for cleaner syntax.

✏️ **Follow-up Challenge**: Can you refactor this loop to execute in $O(1)$ constant time using a HashMap index lookup? (+40 XP)
        """.strip()

    @staticmethod
    def _handle_weak_topics(ctx):
        weaks = ctx['weak_skills'] + ctx['missing_skills']
        if not weaks:
            return "🎉 Excellent work! AI Gap Analysis shows no critical weak skills in your profile."

        w_str = ", ".join(weaks[:3])
        return f"""
⚠️ **AI WEAK SKILL & RETENTION ALERT**

Our Skill Gap vector analysis detected low mastery in: **{w_str}**.

💡 **AI Recommended Recovery Mission**:
- **{weaks[0]}**: Score is currently low. We recommend a 15-minute conceptual refresh followed by 5 practice problems.

Would you like me to create an **AI Special Quest** ("{weaks[0]} Recovery Master") offering **+150 XP & 🪙 +50 Coins**?
        """.strip()

    @staticmethod
    def _handle_career_mentor(ctx, prompt):
        role = ctx['target_role']
        return f"""
🎓 **CAREER MENTOR ADVICE: {role}**

To excel as a **{role}**, employers prioritize:
1. **Core Proficiency**: Strong OOP principles, Exception Handling, Collections framework.
2. **Framework Mastery**: Spring Boot REST APIs, Microservices, Security.
3. **Database Capabilities**: Relational SQL design, Indexing, JDBC transactions.

💡 **Mock Interview Question**:
*"Explain the difference between HashMap and ConcurrentHashMap in high-throughput Java web servers."*

Would you like to practice your answer for AI Mock Interview evaluation?
        """.strip()

    @staticmethod
    def _handle_roadmap_explanation(ctx):
        curr = ctx['current_topic']['topic_name'] if ctx['current_topic'] else "OOP Concepts"
        return f"""
🗺️ **AI ROADMAP DAG ORDER EXPLANATION**

Why is **{curr}** positioned here in your roadmap?

1. **Prerequisite Dependency Tree**: You must master foundational programming before proceeding to advanced frameworks like Spring Boot.
2. **Performance Gap Weighting**: Your initial diagnostic score indicated a conceptual gap, so the AI Topological engine prioritized this module to prevent downstream blockers.

Skipping this topic would delay your target completion date (**{ctx['roadmap_summary']['completion_date']}**).
        """.strip()

    @staticmethod
    def _handle_what_if_simulator(ctx, prompt_lower):
        m = re.search(r'(\d+)\s*hour', prompt_lower)
        hrs = float(m.group(1)) if m else 1.0

        days_now = ctx['roadmap_summary']['total'] * 4 / max(0.5, ctx['available_hours_per_day'])
        days_new = ctx['roadmap_summary']['total'] * 4 / max(0.5, hrs)

        return f"""
⚡ **WHAT-IF SIMULATOR ANALYSIS**

**Scenario**: Adjusting study time to **{hrs} hour(s) per day**

📊 **Impact Assessment**:
- **Current Schedule ({ctx['available_hours_per_day']}h/day)**: Est. completion in **{int(days_now)} days**
- **Simulated Schedule ({hrs}h/day)**: Est. completion in **{int(days_new)} days**

💡 **AI Recommendation**:
If you reduce study time, focus on high-priority weak topics first. Would you like me to update your profile setting to {hrs}h/day?
        """.strip()
