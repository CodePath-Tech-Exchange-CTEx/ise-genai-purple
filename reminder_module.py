import streamlit as st


if 'sort_by' not in st.session_state:
    st.session_state["sort_by"] = "Date"

def sort_list_by():
    st.session_state.sort_by = st.session_state.sort_by_input


def add_reminder():
    pass

def display_app_page():
    

    # title and sort by / add reminders buttons
    with st.container():
        
        st.title("Reminders", width="content", text_alignment="center")

        inner_col1, inner_col2 = st.columns(2, vertical_alignment="bottom", gap="xsmall", width=400,)
        with inner_col1:
            st.selectbox(f"Sort By: {st.session_state.sort_by}", ("Date", "Priority", "A to Z"), 
                        key="sort_by_input", on_change=sort_list_by)
        with inner_col2:
            st.button("Add Reminder", key = "add_reminder", on_click=add_reminder)
    st.divider()

    with st.container(border=True):
        st.write("Im in a container!!!")



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
