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

    def test_todo_ui_elements(self):
        """checks that the input widgets and button render correctly"""
        at = AppTest.from_function(display_todo_page)
        at.run()
        self.assertEqual(at.selectbox[0].label, "category")
        self.assertEqual(at.text_input[0].label, "new task......")
        self.assertEqual(at.button[0].label, "add task")

    def test_todo_columns(self):
        """checks that the four category columns render"""
        at = AppTest.from_function(display_todo_page)
        at.run()
        subheaders = [sh.value for sh in at.subheader]
        self.assertIn(":blue[SCHOOL]", subheaders)
        self.assertIn(":green[WORK]", subheaders)
        self.assertIn(":orange[LIFE]", subheaders)
        self.assertIn(":red[URGENT 🕒]", subheaders)

    def test_todo_ai_elements(self):
        """checks that the ai overview section renders"""
        at = AppTest.from_function(display_todo_page)
        at.run(timeout=15)

        self.assertEqual(at.button[1].label, "generate overview")
        subheaders = [sh.value for sh in at.subheader]
        self.assertIn("AI tasks overview", subheaders)

if __name__ == "__main__":
    unittest.main()