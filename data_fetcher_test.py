import unittest
from unittest.mock import patch, MagicMock
from datetime import date
import data_fetcher


def make_row(data: dict):
    row = MagicMock()
    row.keys.return_value = data.keys()
    row.__iter__ = lambda self: iter(data.items())
    row.__getitem__ = lambda self, key: data[key]
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
# GET #1
# -----------------------------------------------------------------------
class TestGetUserActivities(unittest.TestCase):

    def test_returns_activities_for_user_and_date(self):
        fake_rows = [
            {'title': 'Homework', 'time_span': 120.0, 'category': 'Productive', 'date': date(2026, 2, 23)},
            {'title': 'Netflix',  'time_span': 60.0,  'category': 'Fun',        'date': date(2026, 2, 23)},
        ]
        fake_client = FakeClient(rows=fake_rows)

        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_user_activities('user1', '2026-02-23', "test_user")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Homework')
        self.assertEqual(result[1]['category'], 'Fun')

    def test_queries_correct_table(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_user_activities('user1', '2026-02-23', "test_user")
        self.assertIn('analyser_table', fake_client.last_query)

    def test_returns_empty_list_when_no_data(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_user_activities('user1', '2026-02-23', "test_user")
        self.assertEqual(result, [])

    def test_passes_correct_parameters(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_user_activities('user1', '2026-02-23', "test_user")
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['user_id'], 'user1')
        self.assertEqual(str(params['date']), '2026-02-23')


# -----------------------------------------------------------------------
# GET #2
# -----------------------------------------------------------------------
class TestGetActivityHistory(unittest.TestCase):

    def test_returns_history_for_user(self):
        fake_rows = [
            {'title': 'Gaming', 'time_span': 90.0, 'category': 'Fun', 'date': date(2026, 2, 22)},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_activity_history('user1', "test_user", days=7)
        self.assertEqual(len(result), 1)

    def test_default_days_is_7(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_activity_history('user1', "test_user")
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['days'], 7)

    def test_uses_date_sub_in_query(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_activity_history('user1', "test_user", days=7)
        self.assertIn('DATE_SUB', fake_client.last_query)

    def test_returns_empty_list_when_no_history(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_activity_history('user1', "test_user", days=7)
        self.assertEqual(result, [])


# -----------------------------------------------------------------------
# GET #3
# -----------------------------------------------------------------------
class TestGetActivitiesByCategory(unittest.TestCase):

    def test_returns_activities_for_category(self):
        fake_rows = [
            {'title': 'Homework', 'time_span': 120.0, 'category': 'Productive', 'date': date(2026, 2, 23)},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_activities_by_category('user1', 'Productive', "test_user")
        self.assertTrue(all(r['category'] == 'Productive' for r in result))

    def test_passes_category_parameter(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_activities_by_category('user1', 'Fun', "test_user")
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['category'], 'Fun')

    def test_returns_empty_for_unknown_category(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_activities_by_category('user1', 'NonExistent', "test_user")
        self.assertEqual(result, [])


# -----------------------------------------------------------------------
# GET #4
# -----------------------------------------------------------------------
class TestGetDailySummary(unittest.TestCase):

    def test_returns_summary_grouped_by_category(self):
        fake_rows = [
            {'category': 'Productive', 'total_minutes': 165.0},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_daily_summary('user1', '2026-02-23', "test_user")
        self.assertEqual(result[0]['category'], 'Productive')

    def test_uses_group_by_in_query(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_daily_summary('user1', '2026-02-23', "test_user")
        self.assertIn('GROUP BY', fake_client.last_query)

    def test_returns_empty_when_no_data(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_daily_summary('user1', '2026-02-23', "test_user")
        self.assertEqual(result, [])


# -----------------------------------------------------------------------
# GET #5
# -----------------------------------------------------------------------
class TestGetGenaiAdvice(unittest.TestCase):

    def test_returns_content_and_summary(self):
        fake_summary = [{'category': 'Productive', 'total_minutes': 120.0}]
        mock_response = MagicMock()
        mock_response.text = "Great job!"

        with patch('data_fetcher.get_daily_summary', return_value=fake_summary), \
             patch('data_fetcher.vertexai.init'), \
             patch('data_fetcher.GenerativeModel') as MockModel:

            MockModel.return_value.generate_content.return_value = mock_response
            result = data_fetcher.get_genai_advice('user1', "test_user")

        self.assertIn('content', result)

    def test_handles_no_activities_today(self):
        mock_response = MagicMock()
        mock_response.text = "No data"

        with patch('data_fetcher.get_daily_summary', return_value=[]), \
             patch('data_fetcher.vertexai.init'), \
             patch('data_fetcher.GenerativeModel') as MockModel:

            MockModel.return_value.generate_content.return_value = mock_response
            result = data_fetcher.get_genai_advice('user1', "test_user")

        self.assertEqual(result['summary'], [])

    def test_calls_vertex_ai(self):
        with patch('data_fetcher.get_daily_summary', return_value=[]), \
             patch('data_fetcher.vertexai.init') as mock_init, \
             patch('data_fetcher.GenerativeModel') as MockModel:

            MockModel.return_value.generate_content.return_value = MagicMock(text="tip")
            data_fetcher.get_genai_advice('user1', "test_user")

        mock_init.assert_called_once()


# -----------------------------------------------------------------------
# GET #6: get_todays_tasks
# -----------------------------------------------------------------------
class TestGetTodaysTasks(unittest.TestCase):

    def test_returns_tasks_for_user_today(self):
        fake_rows = [
            {'name_of_task': 'Do homework', 'task_id': 1, 'category': 'Study',
             'due_date': date(2026, 4, 19), 'completion': False},
            {'name_of_task': 'Exercise', 'task_id': 2, 'category': 'Health',
             'due_date': date(2026, 4, 19), 'completion': True},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_todays_tasks('remi_the_rems')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name_of_task'], 'Do homework')

    def test_passes_correct_username(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_todays_tasks('remi_the_rems')
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['username'], 'remi_the_rems')

    def test_returns_empty_when_no_tasks(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_todays_tasks('remi_the_rems')
        self.assertEqual(result, [])

    def test_queries_correct_table(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_todays_tasks('remi_the_rems')
        self.assertIn('tasks_table', fake_client.last_query)


# -----------------------------------------------------------------------
# GET #7: get_upcoming_reminders
# -----------------------------------------------------------------------
class TestGetUpcomingReminders(unittest.TestCase):

    def test_returns_upcoming_reminders(self):
        fake_rows = [
            {'title': 'Team meeting', 'type': 'Work',
             'date_time': '2026-04-19T10:00:00'},
            {'title': 'Gym session', 'type': 'Health',
             'date_time': '2026-04-19T17:00:00'},
        ]
        fake_client = FakeClient(rows=fake_rows)
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_upcoming_reminders('remi_the_rems')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Team meeting')

    def test_default_limit_is_3(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_upcoming_reminders('remi_the_rems')
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['limit'], 3)

    def test_passes_correct_username(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_upcoming_reminders('remi_the_rems')
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['username'], 'remi_the_rems')

    def test_returns_empty_when_no_reminders(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            result = data_fetcher.get_upcoming_reminders('remi_the_rems')
        self.assertEqual(result, [])

    def test_queries_correct_table(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.get_upcoming_reminders('remi_the_rems')
        self.assertIn('notification_table', fake_client.last_query)

# -----------------------------------------------------------------------
# POST: add_task
# -----------------------------------------------------------------------
class TestAddTask(unittest.TestCase):

    def test_inserts_into_tasks_table(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            success, message = data_fetcher.add_task(
                'remi', 'Do homework', 'Study', '2026-04-20'
            )
        self.assertIn('tasks_table', fake_client.last_query)
        self.assertIn('INSERT INTO', fake_client.last_query)

    def test_returns_success(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            success, message = data_fetcher.add_task(
                'remi', 'Do homework', 'Study', '2026-04-20'
            )
        self.assertTrue(success)
        self.assertEqual(message, "Task added successfully!")

    def test_passes_correct_parameters(self):
        fake_client = FakeClient(rows=[])
        with patch('data_fetcher.get_client', return_value=fake_client):
            data_fetcher.add_task('remi', 'Do homework', 'Study', '2026-04-20')
        params = {p.name: p.value for p in fake_client.last_job_config.query_parameters}
        self.assertEqual(params['username'], 'remi')
        self.assertEqual(params['name_of_task'], 'Do homework')
        self.assertEqual(params['category'], 'Study')

# -----------------------------------------------------------------------
# GenAI: get_home_ai_overview
# -----------------------------------------------------------------------
class TestGetHomeAiOverview(unittest.TestCase):

    def test_returns_string_with_tasks(self):
        fake_tasks = [
            {'name_of_task': 'Do homework', 'completion': False},
            {'name_of_task': 'Exercise', 'completion': True},
        ]
        mock_response = MagicMock()
        mock_response.text = "Great progress! Focus on your homework next."

        with patch('data_fetcher.get_todays_tasks', return_value=fake_tasks), \
             patch('data_fetcher.vertexai.init'), \
             patch('data_fetcher.GenerativeModel') as MockModel:
            MockModel.return_value.generate_content.return_value = mock_response
            result = data_fetcher.get_home_ai_overview('remi')

        self.assertIsInstance(result, str)
        self.assertEqual(result, "Great progress! Focus on your homework next.")

    def test_returns_string_with_no_tasks(self):
        mock_response = MagicMock()
        mock_response.text = "No tasks yet — plan a productive day!"

        with patch('data_fetcher.get_todays_tasks', return_value=[]), \
             patch('data_fetcher.vertexai.init'), \
             patch('data_fetcher.GenerativeModel') as MockModel:
            MockModel.return_value.generate_content.return_value = mock_response
            result = data_fetcher.get_home_ai_overview('remi')

        self.assertIsInstance(result, str)
        self.assertEqual(result, "No tasks yet — plan a productive day!")

    def test_calls_vertex_ai(self):
        with patch('data_fetcher.get_todays_tasks', return_value=[]), \
             patch('data_fetcher.vertexai.init') as mock_init, \
             patch('data_fetcher.GenerativeModel') as MockModel:
            MockModel.return_value.generate_content.return_value = MagicMock(text="tip")
            data_fetcher.get_home_ai_overview('remi')

        mock_init.assert_called_once()
        MockModel.assert_called_once()


if __name__ == '__main__':
    unittest.main()