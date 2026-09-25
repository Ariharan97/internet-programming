import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from seed_data import seed

class TestAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed()
        app.testing = True
        cls.client = app.test_client()

    def test_get_career_goals(self):
        res = self.client.get('/api/career-goals')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreater(len(data), 0)

    def test_get_dashboard(self):
        res = self.client.get('/api/dashboard')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('overall_progress_percentage', data)
        self.assertIn('career_goal', data)

    def test_get_skill_gap_analysis(self):
        res = self.client.get('/api/skill-gap-analysis')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('counts', data)

    def test_submit_assessment(self):
        payload = {
            'assessment_id': 2, # OOP assessment
            'answers': {'4': 'extends', '5': 'The ability of an object to take on many forms'},
            'time_taken_seconds': 60
        }
        res = self.client.post('/api/assessment/submit', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('score_percentage', data)
        self.assertIn('adaptation', data)

    def test_admin_analytics(self):
        res = self.client.get('/api/admin/analytics')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreaterEqual(data['total_students'], 1)

if __name__ == '__main__':
    unittest.main()
