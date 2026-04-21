# Intro
- Hello willing participant. Today you will be taking part in a user study for our group project. As the subject of this user study, your role is to complete the given task to the best of your ability while providing feedback throughout the process.
- To get the most out of this study, we want you take on a user persona as you complete the task so we can align the feature to the needs of our app users.
- Your persona for this test will be Alice, a busy college student who feels overwhelmed by all the events and assignments going on in her life. She realizes she needs a way to track it all in once place which is how she found our app. As you complete the task, try to get into the mind of Alice and think about her motivations.
- During the test, it is important that you voice all of the thoughts you have as you go through the process. Explain every thought and intention behind your actions before you perform them. Try your best to leave nothing unsaid.

# Tasks
### Task #1
- After Alice logs into the app, she arrives at her main page and is greeted by a quick overview of her day’s todo’s and reminders. Now, add a task from the main page.
### Task #2
- Afer she sussessfully added a task, Alice wants to see what her calender looks like. open the calender.

# Notes
-   The user was clear on what actions they had to take to complete the task. Although the user did express specific confusions.
- when trying to create a new task, user was confused on date input field. was it the due date or today's date?
- user also mentioned the need to have an optional task description should incase they wanted to specify further what the task was.
- user noted there was no button to indicate a new task had been created and shared confusion as to how they could see the task they added
- user also shared confusion regarding ai overview section, was confused in general on what the overview did.
- During the second task the user, also shared how there was no way to return to the home page if they were done looking at the calender.
- Overall each task was completed quickly and useful feedback was given and the test was a success.
# Feedback
- How easy/hard was it to complete the task given?
  - " I'll rate the ease a 7.5 as I was majorly confused on what indicates if a task is successfully created."
- What confusions were there? Why were they confused?
  - "What does the ai overview section do?, How do i succesfully create a task, how do I return to the homepage from the calender?" 
- What could be improved?
  - " make it much clearer what each input field does and instead of linking to the task a quicker way to add task would be to create a nice pop up box that adds the tasks directly from the homepage" 
# Results
- The date input field lacked clear labeling - "was it the due date or today's date?"
  - Hypothesis: The date field label is ambiguous and does not communicate its purpose to the user
  - Fix: Rename the label to explicitly say "Due Date" and consider adding placeholder text or a tooltip for clarity

- There was no confirmation or visibility when a task was created - "I was majorly confused on what indicates if a task is successfully created"
  - Hypothesis: The absence of a success state (toast, confirmation message, or redirect) left the user uncertain whether their action worked
  - Fix: Add a success notification and ensure the newly created task is immediately visible after creation with a new tag.

- Task creation flow requires leaving the main page - "a quicker way to add task would be to create a nice pop up box that adds the tasks directly from the homepage"
  - Hypothesis: Navigating away from the main page to create a task feels disruptive and slow for a busy user
  - Fix: Implement a modal/popup form for quick task creation directly from the main page without a page redirect

- The AI overview section was unclear in purpose - "What does the AI overview section do?"
  - Hypothesis: The feature lacks any descriptive label, tooltip, or onboarding hint explaining its functionality
  - Fix: Add a brief description or a longer header title to the ai overview section, and consider a small info icon with a tooltip explaining what the AI overview provides

- There was no way to return to the home page from the calendar - "how do I return to the homepage from the calendar?"
  - Hypothesis: The calendar view lacks a back button or home navigation, leaving the user feeling stuck
  - Fix: Add a visible Home/back button within the calendar view so users can easily return

- The task description field was missing - user mentioned "the need to have an optional task description"
  - Hypothesis: Users want the flexibility to add context to their tasks beyond just a title
  - Fix: Add an optional description input field to the task creation form
