import unittest
import os
import sys

# Add parent directory to module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import init_db, get_db_connection, create_user, query_db
from seed_data import seed
from ai_engine import AdaptiveAIEngine

class TestAIEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed()

    def test_topological_sort_and_roadmap_generation(self):
        # Sample Student User ID = 2
        roadmap = AdaptiveAIEngine.generate_personalized_roadmap(user_id=2, career_goal_id=1)
        self.assertIsNotNone(roadmap)
        self.assertIn('nodes', roadmap)
        self.assertGreater(len(roadmap['nodes']), 0)
        
        # Verify sequence order exists
        topic_names = [n['topic_name'] for n in roadmap['nodes']]
        self.assertIn('Java Basics', topic_names)
        self.assertIn('OOP Concepts', topic_names)

        # Check prerequisite ordering constraint (Java Basics must appear before OOP Concepts)
        java_idx = topic_names.index('Java Basics')
        oop_idx = topic_names.index('OOP Concepts')
        self.assertLess(java_idx, oop_idx, "Java Basics must precede OOP Concepts in topological order")

    def test_skill_gap_analysis(self):
        gap = AdaptiveAIEngine.analyze_skill_gap(user_id=2, career_goal_id=1)
        self.assertIsNotNone(gap)
        self.assertIn('overall_readiness_percentage', gap)
        self.assertIn('counts', gap)

    def test_adaptive_roadmap_update_on_high_score(self):
        # Master Java Basics with 90% score
        res = AdaptiveAIEngine.adapt_roadmap_after_assessment(user_id=2, topic_id=2, score_percentage=90.0, accuracy=100.0, time_taken_seconds=90)
        self.assertEqual(res['status'], 'Mastered')
        self.assertIn('Mastered', res['message'])

    def test_adaptive_roadmap_update_on_low_score(self):
        # Fail OOP Concepts with 40% score
        res = AdaptiveAIEngine.adapt_roadmap_after_assessment(user_id=2, topic_id=3, score_percentage=40.0, accuracy=40.0, time_taken_seconds=150)
        self.assertEqual(res['status'], 'Weak')
        self.assertIn('Weak', res['message'])

if __name__ == '__main__':
    unittest.main()
