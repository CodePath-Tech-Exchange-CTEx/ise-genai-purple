#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from pages.to_do_module import display_todo_page
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass

class TestDisplayTodoPage(unittest.TestCase):
    """tests the display_todo_page function."""

    def test_todo_title(self):
        """checks that the page title works"""
        at = AppTest.from_function(display_todo_page)
        at.run()
        self.assertEqual(at.title[0].value, "to-do")

    def test_todo_initial_state(self):
        """checks the task list so that it start empty"""
        at = AppTest.from_function(display_todo_page)
        at.run()
        self.assertEqual(at.session_state["tasks"], [])

if __name__ == "__main__":
    unittest.main()
