# logic.py

def calculate_completion_percentage(completed, total):
    if total == 0:
        return 0
    return round((completed / total) * 100, 2)

def get_time_difference(today_time, yesterday_time):
    """Returns the difference in hours."""
    return today_time - yesterday_time

def generate_suggestion(screentime_hrs, study_hrs):
    """Simple logic-based suggestions."""
    if screentime_hrs > study_hrs:
        return "Reduce screentime to achieve more tasks tomorrow."
    return "You're doing great! Keep up the balance."