import streamlit as st
from datetime import datetime
from helper.notification_data import (
    get_item_data, 
    add_notification, 
    get_notifications, 
    update_reminder, 
    delete_reminder
)

# ---------------------------
# Session State Initialization
# ---------------------------
# Persist user preferences for sorting across script reruns
if "sort_by" not in st.session_state:
    st.session_state["sort_by"] = "Date"

# Global list to store reminder objects
if "reminders_list" not in st.session_state:
    st.session_state["reminders_list"] = []

# ---------------------------
# Helper Functions
# ---------------------------

def format_date(dt):
    """
    Converts a datetime object into a user-friendly string.
    Example output: 'Monday 03:30pm 3/23'
    """
    if not dt:
        return ""
    # We use lowercase 'am/pm' to keep the UI clean and modern
    return dt.strftime("%A %I:%M%p %#m/%#d").replace("AM", "am").replace("PM", "pm")

@st.dialog("Edit Reminder", dismissible=True, on_dismiss="ignore")
def edit_reminder(reminder):
    """
    Modal window for modifying an existing reminder.
    Allows changing date, repeat status, and interval.
    """
    # Initialize inputs with current reminder data
    new_dt = st.datetime_input("Notify me at:", format="MM/DD/YYYY", value=reminder.get("date_time"))
    
    # Toggle repeat logic; defaults to current state in DB
    new_repeated = True if st.pills("Repeat", ["Yes", "No"], 
                                     default="Yes" if reminder.get("repeat") else "No") == "Yes" else False
    new_interval = None

    # Handle interval logic (converted to minutes for DB consistency)
    if new_repeated: 
        new_interval = st.pills("Repeat interval", ["Hourly", "Daily", "Weekly", "Monthly", "Custom"])

        if new_interval == "Custom":
            new_interval = st.text_input("Custom interval", placeholder="Enter in minutes")
        elif new_interval == "Hourly": new_interval = 60
        elif new_interval == "Daily": new_interval = 1440
        elif new_interval == "Weekly": new_interval = 10080
        elif new_interval == "Monthly": new_interval = 43830

    # Layout buttons in the footer of the dialog
    _, del_col, submit_col = st.columns([4, 1.2, 1], gap="xsmall")
    
    with del_col:
        # Delete action: uses unique key to prevent widget collision
        if st.button("Delete", key=f"del_{reminder['title']}"):
            delete_reminder(reminder['title'])
            st.toast("Deleted!")
            st.rerun() # Closes dialog and refreshes main list
            
    with submit_col:
        submitted = st.button("Edit", key="submit_new_reminder", type="primary")

    # Save changes logic
    if submitted:
        errors = []
        if new_repeated is None:
            errors.append("Must select a repeat mode.")
        if new_repeated is True and not new_interval:
            errors.append("Must select a repeat interval if repeat is selected.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Push updates to BigQuery helper
            update_reminder(reminder, new_dt, new_repeated, new_interval)
            st.toast("Reminder edited successfully!")
            st.rerun() 

# ---------------------------
# Core UI Functions
# ---------------------------
def load_reminders():
    """
    Fetches latest data from BigQuery and renders reminder 'cards' in a vertical list.
    """
    reminders = get_notifications()

    info_message = "Add Some Reminders"

    if st.session_state.choose_item_type == "Event":
        reminders = [r for r in reminders if r.get("type") == "Event"]
        info_message = "Add Some Event Reminders"
    elif st.session_state.choose_item_type == "Task":
        info_message = "Add Some Task Reminders"
        reminders = [r for r in reminders if r.get("type") == "Task"]

    if st.session_state.sort_by == "Date":
        reminders.sort(key=lambda x: x.get("date_time", datetime.max))
    elif st.session_state.sort_by == "A to Z":
        reminders.sort(key=lambda x: x.get("title", "").lower())



    if not reminders:
        st.info(info_message) 
        return

    # Use a column layout to center-align the cards slightly
    right, _ = st.columns([3, 1], vertical_alignment="center")
    
    with right:
        for idx, reminder in enumerate(reminders):
            # Outer container for the reminder "card"
            with st.container(border=True): 
                # Row 1: Type badge, Title, and Edit button
                with st.container(border=True): 
                    type_col, title_col, edit_col = st.columns([1, 5, 1], vertical_alignment="center")

                    with type_col:
                        if reminder.get("type"):
                            # Logic for dynamic badge coloring
                            color = "orange" if reminder["type"] == "Event" else "blue"
                            st.markdown(f':{color}-background[:{color}[{reminder["type"]}]]')

                    with title_col:
                        st.markdown(f"**{reminder['title']}**")

                    with edit_col:
                        # Icon button to open the Edit Dialog
                        st.button("", icon=":material/more_horiz:", key=f"edit_{idx}", 
                                  on_click=edit_reminder, args=(reminder,))

                # Row 2: Display notification time and recurrence info
                with st.container(border=True):
                    formatted_date = format_date(reminder.get("date_time"))
                    interval_str = ""
                    interval = reminder.get("interval", 0)
                    
                    # Logic to convert minutes back into readable days/hours/minutes
                    if not reminder.get("repeat"):
                        interval_str = "Once"
                    elif interval >= 1440:
                        days = interval // 1440
                        hours = (interval % 1440) // 60
                        interval_str = f"Every {days}d, {hours}h"
                    elif interval >= 60:
                        hours = interval // 60
                        minutes = interval % 60
                        interval_str = f"Every {hours}h {minutes}m"
                    else:
                        interval_str = f"Every {interval}m"
                    
                    st.markdown(f"**Notify me at:** :blue-background[{formatted_date}] • *{interval_str}*")

# ---------------------------
# Dialog for Adding Reminder
# ---------------------------
@st.dialog("Add Reminder", dismissible=True, on_dismiss="ignore")
def add_reminder():
    """
    Interface for creating a new reminder record. 
    Cross-references existing tasks/events in BigQuery via get_item_data.
    """
    st.write("*Choose an existing Event or Task to add a reminder for*")
    
    new_reminder = {
        "title": "",
        "type": None,
        "date_time": datetime.now(),
        "repeat": False,
        "interval": None,
        "completed": False
    }
    item_name = ""

    # Selection for source data (Calendar vs Task List)
    new_reminder["type"] = st.pills("Type of Reminder", ["Event (from calendar)", "Task (from to-do)"])
    if new_reminder["type"]:
        new_reminder["type"] = "Event" if new_reminder["type"].startswith("Event") else "Task"

    new_reminder["title"] = st.text_input("Title of the item:", placeholder="Preexisting event or task")
    
    # Validation check: Ensure the event actually exists in the separate events/tasks table
    if new_reminder["title"]:
        item_name = get_item_data(new_reminder["title"], new_reminder["type"])

    new_reminder["date_time"] = st.datetime_input("Notify me at:", format="MM/DD/YYYY")
    new_reminder["repeat"] = True if st.pills("Repeat", ["Yes", "No"]) == "Yes" else False

    # Repeat interval logic
    if new_reminder["repeat"]: 
        new_reminder["interval"] = st.pills("Repeat interval", ["Hourly", "Daily", "Weekly", "Monthly", "Custom"])

        if new_reminder["interval"] == "Custom":
            new_reminder["interval"] = st.text_input("Custom interval", placeholder="Enter in minutes")
        elif new_reminder["interval"] == "Hourly": new_reminder["interval"] = 60
        elif new_reminder["interval"] == "Daily": new_reminder["interval"] = 1440
        elif new_reminder["interval"] == "Weekly": new_reminder["interval"] = 10080
        elif new_reminder["interval"] == "Monthly": new_reminder["interval"] = 43830

    _, submit_col = st.columns([4, 1])
    with submit_col:
        submitted = st.button("Submit", key="submit_new_reminder", type="primary")

    if submitted:
        errors = []
        if not new_reminder["title"].strip():
            errors.append("Title is required.")
        if not new_reminder["type"]:
            errors.append("You must select a type.")
        if not item_name:
            errors.append("Event or task doesn't exist.")
        
        if errors:
            for e in errors:
                st.error(e)
        else:
            # Overwrite user input with the "Official" name found in BigQuery
            new_reminder["title"] = item_name
            add_notification(new_reminder)
            st.toast("Reminder added successfully!")
            st.rerun()

# ---------------------------
# Main App Page
# ---------------------------
def display_reminder_page():
    """Main execution point for rendering the Reminders page."""
    with st.container():
        st.title("Reminders")

        # Top controls for sorting
        col1, _ = st.columns([1.3, 2], vertical_alignment="bottom", gap="xsmall")
        with col1:
            st.selectbox("Sort By:", ("Date", "A to Z", "Events", "Tasks"), key="sort_by", placeholder="Date")

        # Main call-to-action button
        button_col1, _, _ = st.columns([.6, .7, 2], gap="xsmall")
        with button_col1:
            st.button("Add Reminder", key="add_reminder", on_click=add_reminder, width="stretch")
    
        pill_select, _ = st.columns([1, 2], gap="xsmall")
        with pill_select:
            st.pills("", ["All", "Event", "Task"], default="All", key="choose_item_type")

    st.divider()
    
    
    load_reminders()

if __name__ == "__main__":
    display_reminder_page()