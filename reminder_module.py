import streamlit as st


if 'sort_by' not in st.session_state:
    st.session_state["sort_by"] = "Date"

if "reminders_list" not in st.session_state:
    st.session_state.reminders_list = []

def sort_list_by():
    st.session_state.sort_by = st.session_state.sort_by_input

def switch_reminder_status():
    # Loop through all reminders
    for idx, reminder in enumerate(st.session_state.reminders_list):
        key = f"complete_{idx}"
        # Read the checkbox value from session state
        reminder["completed"] = st.session_state.get(key, False)

def load_reminders():
    reminders = st.session_state.reminders_list
    left, center, right = st.columns([1, 5, 1])
    if not reminders:
        center.error("Add some reminders")
    else:
        with center:
            for idx, i in enumerate(reminders):
                with st.container(border=True):
                        # reminder title (top)
                        with st.container(border=True): 
                            tag, name, edit = st.columns([2, 6, 1], vertical_alignment="center")
                            with tag:
                                if i["tag"]:
                                    st.markdown(f':{i["tag_color"]}-background[:{i["tag_color"]}[{i["tag"]}]]', text_alignment="center")
                            with name:
                                st.markdown(f"**{i["title"]}**", text_alignment="center")
                            with edit:
                                st.button("", icon=":material/more_horiz:", key=f"edit_{idx}")
                        # reminder info (bottom)
                        with st.container(border=True):
                            priority, date, complete = st.columns([3, 6, 3.2], vertical_alignment="center")
                            with priority:
                                match(i["priority"]):
                                    case "Priority 1":
                                        st.markdown(":red-background[:red[Priority 1]]")
                                    case "Priority 2":
                                        st.markdown(":orange-background[:orange[Priority 2]]")
                                    case "Priority 3":
                                        st.markdown(":yellow-background[:yellow[Priority 3]]")
                                    case "Priority 4":
                                        st.markdown(":green-background[:green[Priority 4]]")
                                    case "Priority 5":
                                        st.markdown(":blue-background[:blue[Priority 5]]")
                            with date:
                                formatted_date = i["date"].strftime("%A %I:%M%p %#m/%#d").replace("AM", "am").replace("PM", "pm")
                                st.markdown(f":blue-background[{formatted_date}]", text_alignment="center")
                            
                            with complete:
                                st.checkbox("Completed", key=f"complete_{idx}", on_change=switch_reminder_status)

                    


@st.dialog("Add Reminder", dismissible=True, on_dismiss="ignore")
def add_reminder():
    new_reminder = {"title": "", "date": None, "priority": "", "tag": None, "tag_color": "", "completed": False}
    new_reminder["title"] = st.text_input("Reminder Name", placeholder="Name of reminder", max_chars=50)
    new_reminder["date"] = st.datetime_input("Date and Time", format="MM/DD/YYYY", value="now")
    new_reminder["priority"] = st.pills("Priority Level", ["Priority 1", "Priority 2", "Priority 3", "Priority 4", "Priority 5"])
    new_reminder["tag"] = st.text_input("Tag this reminder", placeholder='Leave empty to skip', max_chars=14)
    new_reminder["tag_color"] = st.pills("Tag Color", ["red", "orange", "yellow", "green", "blue", "violet", "gray"], disabled=not new_reminder["tag"])

    col1, col2 = st.columns([4, 1])
    with col2:
        submitted = st.button("Submit", type="primary")

    if submitted:

        errors = []

        if not new_reminder["title"].strip():
            errors.append("Title is required.")

        if not new_reminder["priority"]:
            errors.append("Please select a priority level.")

        if new_reminder["tag"] and not new_reminder["tag_color"]:
            errors.append("Select a tag color if you add a tag.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            st.session_state.reminders_list.append(new_reminder)
            load_reminders()
            st.rerun()


def clear_completed():
    reminders = st.session_state.reminders_list
    if not reminders:
        st.toast("There are no reminders!")

    for idx, i in enumerate(reminders):
        if i["completed"]:
            reminders.pop(idx)

def display_app_page():
    # title and sort by / add reminders buttons
    with st.container():
        st.title("Reminders", width="content", text_alignment="center")

        col1, spacer = st.columns([1.3, 2], vertical_alignment="bottom", gap="xsmall")
        with col1:
            st.selectbox(f"Sort By: {st.session_state.sort_by}", ("Date", "Priority", "A to Z"), key="sort_by_input", on_change=sort_list_by)

        button_col1, button_col2, spacer = st.columns([.7, 1, 2], gap="xsmall")
        with button_col1:
            st.button("Add Reminder", key = "add_reminder", on_click=add_reminder, width="stretch")
        with button_col2:
            st.button("Clear Completed", on_click=clear_completed)
    st.divider()

    
    load_reminders()
        



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
