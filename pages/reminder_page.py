import streamlit as st
from datetime import datetime

# ---------------------------
# Session State Initialization
# ---------------------------
# Initialize default sorting option if it doesn't exist
if "sort_by" not in st.session_state:
    st.session_state["sort_by"] = "Date"

# Initialize the reminders list in session state if it doesn't exist
if "reminders_list" not in st.session_state:
    st.session_state["reminders_list"] = []

# ---------------------------
# Helper Functions
# ---------------------------
def sort_list_by():
    """Update the sorting preference from the selectbox widget."""
    # Set the current sort option from the selectbox value in session state
    st.session_state.sort_by = st.session_state.sort_by_input

def switch_reminder_status():
    """Update the completed status for all reminders based on checkboxes."""
    # Loop over all reminders and read checkbox values from session state
    for idx, reminder in enumerate(st.session_state.reminders_list):
        key = f"complete_{idx}"  # Construct checkbox key
        # Update reminder's 'completed' status safely using .get() with default False
        reminder["completed"] = st.session_state.get(key, False)

def clear_completed():
    """Remove completed reminders from the list."""
    reminders = st.session_state.reminders_list
    if not reminders:
        st.toast("There are no reminders!")  # Show message if list is empty
        return

    # Keep only reminders that are not completed
    st.session_state.reminders_list = [r for r in reminders if not r.get("completed", False)]
    st.toast("Completed reminders cleared!")  # Feedback for user

def format_date(dt):
    """Format a datetime object to a readable 12-hour format with day and month/day."""
    if not dt:
        return ""
    # Example format: 'Monday 03:30pm 2/23', with lowercase am/pm
    return dt.strftime("%A %I:%M%p %#m/%#d").replace("AM", "am").replace("PM", "pm")

# ---------------------------
# Core UI Functions
# ---------------------------
def load_reminders():
    """Render all reminders in the main UI."""
    reminders = st.session_state.reminders_list
    _, center, _ = st.columns([1, 5, 1])  # Center the reminder content

    if not reminders:
        center.error("Add some reminders")  # Prompt if no reminders exist
        return

    with center:
        for idx, reminder in enumerate(reminders):
            # Container for each reminder card
            with st.container(border=True):
                # Top row: tag, title, edit button
                with st.container(border=True):
                    tag_col, title_col, edit_col = st.columns([2, 6, 1], vertical_alignment="center")

                    # Display tag as colored badge if it exists
                    with tag_col:
                        if reminder.get("tag"):
                            st.markdown(
                                f':{reminder["tag_color"]}-background[:{reminder["tag_color"]}[{reminder["tag"]}]]',
                                text_alignment="center"
                            )

                    # Display reminder title
                    with title_col:
                        st.markdown(f"**{reminder['title']}**", text_alignment="center")

                    # Edit button (currently placeholder)
                    with edit_col:
                        st.button("", icon=":material/more_horiz:", key=f"edit_{idx}")

                # Bottom row: priority, date, completed checkbox
                with st.container(border=True):
                    priority_col, date_col, complete_col = st.columns([3, 6, 3.2], vertical_alignment="center")

                    # Show priority as colored badge
                    with priority_col:
                        priority_color_map = {
                            "Priority 1": "red",
                            "Priority 2": "orange",
                            "Priority 3": "yellow",
                            "Priority 4": "green",
                            "Priority 5": "blue"
                        }
                        color = priority_color_map.get(reminder.get("priority"), "gray")
                        if reminder.get("priority"):
                            st.markdown(f":{color}-background[:{color}[{reminder['priority']}]]")

                    # Display formatted date
                    with date_col:
                        formatted_date = format_date(reminder.get("date"))
                        st.markdown(f":blue-background[{formatted_date}]", text_alignment="center")

                    # Checkbox to mark reminder as completed
                    with complete_col:
                        st.checkbox(
                            "Completed",
                            key=f"complete_{idx}",  # Unique key for each checkbox
                            value=reminder.get("completed", False),  # Initial state
                            on_change=switch_reminder_status  # Update status on change
                        )

# ---------------------------
# Dialog for Adding Reminder
# ---------------------------
@st.dialog("Add Reminder", dismissible=True, on_dismiss="ignore")
def add_reminder():
    """Dialog window to add a new reminder with validation."""
    # Initialize a new reminder dictionary with default values
    new_reminder = {
        "title": "",
        "date": datetime.now(),
        "priority": "",
        "tag": None,
        "tag_color": "",
        "completed": False
    }

    # Input fields for the dialog
    new_reminder["title"] = st.text_input("Reminder Name", placeholder="Name of reminder", max_chars=50)
    new_reminder["date"] = st.datetime_input("Date and Time", value=datetime.now(), format="MM/DD/YYYY")
    new_reminder["priority"] = st.pills("Priority Level", ["Priority 1", "Priority 2", "Priority 3", "Priority 4", "Priority 5"])
    new_reminder["tag"] = st.text_input("Tag this reminder", placeholder='Leave empty to skip', max_chars=14)
    new_reminder["tag_color"] = st.pills(
        "Tag Color",
        ["red", "orange", "yellow", "green", "blue", "violet", "gray"],
        disabled=not new_reminder["tag"]  # Disable color selection if no tag
    )

    # Submit button aligned to the right
    _, submit_col = st.columns([4, 1])
    with submit_col:
        submitted = st.button("Submit", type="primary")

    # Validation logic
    if submitted:
        errors = []
        if not new_reminder["title"].strip():
            errors.append("Title is required.")
        if not new_reminder["priority"]:
            errors.append("Please select a priority level.")
        if new_reminder["tag"] and not new_reminder["tag_color"]:
            errors.append("Select a tag color if you add a tag.")

        # Display validation errors
        if errors:
            for e in errors:
                st.error(e)
        else:
            # Add reminder to session state and provide feedback
            st.session_state.reminders_list.append(new_reminder)
            st.toast("Reminder added successfully!")
            load_reminders()  # Reload reminders to update UI
            st.rerun()  # Refresh app to reflect changes

# ---------------------------
# Main App Page
# ---------------------------
def display_reminder_page():
    """Render the main Reminders page with sort options and action buttons."""
    with st.container():
        st.title("Reminders", width="content", text_alignment="center")

        # Sort selectbox
        col1, _ = st.columns([1.3, 2], vertical_alignment="bottom", gap="xsmall")
        with col1:
            st.selectbox(
                f"Sort By: {st.session_state.sort_by}",
                ("Date", "Priority", "A to Z"),
                key="sort_by_input",
                on_change=sort_list_by
            )

        # Action buttons: Add Reminder, Clear Completed
        button_col1, button_col2, _ = st.columns([0.7, 1, 2], gap="xsmall")
        with button_col1:
            st.button("Add Reminder", key="add_reminder", on_click=add_reminder, width="stretch")
        with button_col2:
            st.button("Clear Completed", on_click=clear_completed)

    st.divider()
    load_reminders()  # Load all reminders into the UI

# ---------------------------
# Entry Point
# ---------------------------
if __name__ == "__main__":
    display_reminder_page()  # Start the Streamlit app