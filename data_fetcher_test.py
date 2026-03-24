#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
# Unit tests for data_fetcher.py using mocking to avoid real DB/AI calls.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock
from datetime import date
import data_fetcher


# --- Reusable fake BigQuery row ---
def make_row(data: dict):
    """Converts a dict into a mock BigQuery row object."""
    row = MagicMock()
    row.keys.return_value = data.keys()
    row.__iter__ = lambda self: iter(data.items())
    row.__getitem__ = lambda self, key: data[key]
    # This makes dict(row) work correctly
    row._properties = data
    row.items = lambda: data.items()
    return row


class FakeQueryJob:
    def __init__(self, rows=None):
        self._rows = rows or []

    def result(self):
        return self._rows


class FakeClient:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.last_query = None
        self.last_job_config = None

    def query(self, query, job_config=None):
        self.last_query = query
        self.last_job_config = job_config
        return FakeQueryJob(self.rows)


# -----------------------------------------------------------------------
# GET #1: get_user_activities
# -----------------------------------------------------------------------
class TestGetUserActivities(unittest.TestCase):

    def test_returns_activities_for_user_and_date(self):
        fake_rows = [
            {'title': 'Homework', 'time_span': 120.0, 'category': 'Productive', 'date': date(2026, 2, 23)},
            {'title': 'Netflix',  'time_span': 60.0,  'category': 'Fun',        'date': date(2026, 2, 23)},
        ]
        fake_client = FakeClient(rows=fake_rows)

        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_user_activities('user1', '2026-02-23')

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Homework')
        self.assertEqual(result[1]['category'], 'Fun')

    def test_queries_correct_table(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            data_fetcher.get_user_activities('user1', '2026-02-23')
        self.assertIn('analyser_table', fake_client.last_query)

    def test_returns_empty_list_when_no_data(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_user_activities('user1', '2026-02-23')
        self.assertEqual(result, [])

    def test_passes_correct_parameters(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            data_fetcher.get_user_activities('user1', '2026-02-23')
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['user_id'], 'user1')
        self.assertEqual(str(params['date']), '2026-02-23')


# GET #2: get_activity_history
class TestGetActivityHistory(unittest.TestCase):

    def test_returns_history_for_user(self):
        fake_rows = [
            {'title': 'Gaming', 'time_span': 90.0, 'category': 'Fun', 'date': date(2026, 2, 22)},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_activity_history('user1', days=7)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Gaming')

    def test_default_days_is_7(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            data_fetcher.get_activity_history('user1')
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['days'], 7)

    def test_uses_date_sub_in_query(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            data_fetcher.get_activity_history('user1', days=7)
        self.assertIn('DATE_SUB', fake_client.last_query)

    def test_returns_empty_list_when_no_history(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_activity_history('user1', days=7)
        self.assertEqual(result, [])


# -----------------------------------------------------------------------
# GET #3: get_activities_by_category
# -----------------------------------------------------------------------
class TestGetActivitiesByCategory(unittest.TestCase):

    def test_returns_activities_for_category(self):
        fake_rows = [
            {'title': 'Homework', 'time_span': 120.0, 'category': 'Productive', 'date': date(2026, 2, 23)},
            {'title': 'Reading',  'time_span': 45.0,  'category': 'Productive', 'date': date(2026, 2, 22)},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_activities_by_category('user1', 'Productive')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['category'] == 'Productive' for r in result))

    def test_passes_category_parameter(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            data_fetcher.get_activities_by_category('user1', 'Fun')
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['category'], 'Fun')

    def test_returns_empty_for_unknown_category(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_activities_by_category('user1', 'NonExistent')
        self.assertEqual(result, [])


# -----------------------------------------------------------------------
# GET #4: get_daily_summary
# -----------------------------------------------------------------------
class TestGetDailySummary(unittest.TestCase):

    def test_returns_summary_grouped_by_category(self):
        fake_rows = [
            {'category': 'Productive',   'total_minutes': 165.0},
            {'category': 'Fun',          'total_minutes': 135.0},
            {'category': 'Unproductive', 'total_minutes': 90.0},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_daily_summary('user1', '2026-02-23')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['category'], 'Productive')
        self.assertEqual(result[0]['total_minutes'], 165.0)

    def test_uses_group_by_in_query(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            data_fetcher.get_daily_summary('user1', '2026-02-23')
        self.assertIn('GROUP BY', fake_client.last_query)

    def test_returns_empty_when_no_data(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.client', fake_client):
            result = data_fetcher.get_daily_summary('user1', '2026-02-23')
        self.assertEqual(result, [])


# -----------------------------------------------------------------------
# GET #5 (GenAI): get_genai_advice
# -----------------------------------------------------------------------
class TestGetGenaiAdvice(unittest.TestCase):

    def test_returns_content_and_summary(self):
        fake_summary = [
            {'category': 'Productive', 'total_minutes': 120.0},
            {'category': 'Fun',        'total_minutes': 60.0},
        ]
        mock_response = MagicMock()
        mock_response.text = "Great job today! Try to reduce screen time tomorrow."

        with patch('data_fetcher.get_daily_summary', return_value=fake_summary), \
             patch('data_fetcher.vertexai.init'), \
             patch('data_fetcher.GenerativeModel') as MockModel:
            MockModel.return_value.generate_content.return_value = mock_response
            result = data_fetcher.get_genai_advice('user1')

        self.assertIn('content', result)
        self.assertIn('summary', result)
        self.assertIn('date', result)
        self.assertEqual(result['content'], "Great job today! Try to reduce screen time tomorrow.")

    def test_handles_no_activities_today(self):
        mock_response = MagicMock()
        mock_response.text = "No data yet — start logging your activities!"

        with patch('data_fetcher.get_daily_summary', return_value=[]), \
             patch('data_fetcher.vertexai.init'), \
             patch('data_fetcher.GenerativeModel') as MockModel:
            MockModel.return_value.generate_content.return_value = mock_response
            result = data_fetcher.get_genai_advice('user1')

        self.assertEqual(result['summary'], [])
        self.assertIsNotNone(result['content'])

    def test_calls_vertex_ai(self):
        with patch('data_fetcher.get_daily_summary', return_value=[]), \
             patch('data_fetcher.vertexai.init') as mock_init, \
             patch('data_fetcher.GenerativeModel') as MockModel:
            MockModel.return_value.generate_content.return_value = MagicMock(text="tip")
            data_fetcher.get_genai_advice('user1')

        mock_init.assert_called_once()
        MockModel.assert_called_once()


if __name__ == '__main__':
    unittest.main()