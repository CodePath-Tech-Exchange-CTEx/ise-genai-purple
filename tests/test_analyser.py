# test_analyser.py
import pytest
from helper.logic import calculate_completion_percentage, get_time_difference, generate_suggestion

def test_completion_math():
    # Test 15/20 tasks (your mockup)
    assert calculate_completion_percentage(15, 20) == 75.0
    # Test division by zero edge case
    assert calculate_completion_percentage(0, 0) == 0

def test_screentime_comparison():
    # Test the "2 hours more" logic from your drawing
    today = 5
    yesterday = 3
    assert get_time_difference(today, yesterday) == 2

def test_suggestions():
    # Test if AI gives the right advice when screen > study
    advice = generate_suggestion(screentime_hrs=4, study_hrs=2)
    assert "Reduce screentime" in advice