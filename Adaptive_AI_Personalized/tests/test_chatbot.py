import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import init_db, query_db, execute_db
from seed_data import seed
from chatbot import LearnMateAI, StudentContextExtractor
from app import app

class TestLearnMateAIChatbot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed()
        app.testing = True
        cls.client = app.test_client()

    def test_context_extractor(self):
        ctx = StudentContextExtractor.get_full_context(user_id=2)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx['student_name'], 'Alex Mercer')
        self.assertIn('career_goal', ctx)
        self.assertIn('weak_skills', ctx)

    def test_contextual_greeting(self):
        greeting = LearnMateAI.generate_contextual_greeting(user_id=2)
        self.assertIn('Alex', greeting)
        self.assertIn('LearnMate AI', greeting)

    def test_concept_explanation_formatting(self):
        res = LearnMateAI.process_message(user_id=2, prompt="What is Polymorphism?")
        self.assertEqual(res['agent_type'], 'MentorAgent')
        self.assertIn('Key Point', res['response'])
        self.assertIn('Your Next Step', res['response'])

    def test_what_if_simulator(self):
        res = LearnMateAI.process_message(user_id=2, prompt="What if I study 1 hour per day?")
        self.assertEqual(res['agent_type'], 'RoadmapAgent')
        self.assertIn('WHAT-IF SIMULATOR', res['response'])

    def test_study_plan_generator(self):
        res = LearnMateAI.process_message(user_id=2, prompt="Create a study plan for today")
        self.assertEqual(res['agent_type'], 'ProgressAgent')
        self.assertIn('STUDY MISSION', res['response'])

    def test_chat_api_endpoint(self):
        payload = {'prompt': 'What should I learn next?'}
        res = self.client.post('/api/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('response', data)
        self.assertEqual(data['agent_type'], 'RoadmapAgent')

if __name__ == '__main__':
    unittest.main()
