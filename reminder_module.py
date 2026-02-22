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

    # reminder card template

    left, center, right = st.columns([1, 5, 1])

    with center:
        with st.container(border=True):
            with st.container(border=True): # reminder title (top)

                tag, name, edit = st.columns([2, 6, 1], vertical_alignment="center")

                with tag:
                    st.markdown(':red-background[:red[Important]]')
                
                with name:
                    st.markdown("**The big interview**", text_alignment="left")

                with edit:
                    st.button("", icon=":material/more_horiz:", key="edit1")
            
            
            
            with st.container(border=True): # reminder info (bottom)
                priority, date, spacer, notify = st.columns([1.3, 3, .5, 2], vertical_alignment="center")
                
                with priority:
                    st.markdown(":orange-background[:orange[Priority 1]]")

                with date:
                    st.markdown(":blue-background[Wednesday 3:30pm 3/15]", text_alignment="center")
                
                with notify:
                    st.button("Notification")

        



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
