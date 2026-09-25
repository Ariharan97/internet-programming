import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import init_db, query_db, execute_db
from seed_data import seed
from gamification import GamificationEngine
from app import app

class TestGamificationSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed()
        app.testing = True
        cls.client = app.test_client()

    def test_xp_award_and_level_up(self):
        user_id = 2 # Alex Mercer
        initial_xp = GamificationEngine.get_user_xp(user_id)
        
        # Award 150 XP to trigger Level progression
        res = GamificationEngine.award_xp(user_id, 150, 'quiz', 'Completed Unit Test Quiz')
        self.assertEqual(res['earned_xp'], 150)
        
        new_xp = GamificationEngine.get_user_xp(user_id)
        self.assertEqual(new_xp, initial_xp + 150)

        # Check Level info
        lvl_info = GamificationEngine.get_level_info(new_xp)
        self.assertGreaterEqual(lvl_info['level'], 2)

    def test_streak_update_and_shield(self):
        user_id = 2
        streak_res = GamificationEngine.update_streak(user_id)
        self.assertIsNotNone(streak_res)
        self.assertIn('streak', streak_res)
        self.assertGreaterEqual(streak_res['streak'], 1)

    def test_gamification_dashboard_endpoint(self):
        res = self.client.get('/api/gamification/dashboard')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('level', data)
        self.assertIn('total_xp', data)
        self.assertIn('coins', data)

    def test_gamification_badges_endpoint(self):
        res = self.client.get('/api/gamification/badges')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreater(len(data), 0)

    def test_reward_shop_redemption(self):
        user_id = 2
        # Award coins to ensure sufficient balance
        GamificationEngine.award_coins(user_id, 500, 'Test Coin Award')
        
        # Redeem Streak Shield (Reward ID 1)
        redeem_res = GamificationEngine.redeem_reward(user_id, 1)
        self.assertTrue(redeem_res['success'])
        self.assertIn('Successfully purchased', redeem_res['message'])

    def test_leaderboard_privacy(self):
        res = self.client.get('/api/gamification/leaderboard')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main()
