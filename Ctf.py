import streamlit as st
import time
from backend import (
    extract_text,
    generate_summary,
    generate_flashcards,
    generate_quiz,
    ask_question,
    evaluate_answer
)

# PAGE CONFIGURATION
st.set_page_config(
    page_title="AI NoteMate",
    page_icon="📚",
    layout="wide"
)


# CUSTOM CSS
st.markdown("""
<style>

/* Main app background */
.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--secondary-background-color);
}

/* Headings */
h1, h2, h3, h4 {
    color: var(--text-color);
}

/* Paragraphs and text */
p, label, .stMarkdown {
    color: var(--text-color);
}

/* Buttons */
.stButton > button {
    background-color: #3478F6;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}

.stButton > button:hover {
    background-color: #1D5FD1;
    color: white;
}

/* Cards */
.card {
    background-color: var(--secondary-background-color);
    padding: 22px;
    border-radius: 15px;
    border: 1px solid var(--border-color);
    margin-bottom: 15px;
}

/* Metrics */
.metric {
    font-size: 30px;
    font-weight: bold;
    color: #3478F6;
}

.small {
    color: var(--text-color);
    font-size: 14px;
    opacity: 0.75;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
}

</style>
""", unsafe_allow_html=True)




# SESSION STATE
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "progress" not in st.session_state:
    st.session_state.progress = 0

if "card" not in st.session_state:
    st.session_state.card = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if "quiz_done" not in st.session_state:
    st.session_state.quiz_done = False
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = set()

if "flashcards_generated" not in st.session_state:
    st.session_state.flashcards_generated = 0

if "quizzes_generated" not in st.session_state:
    st.session_state.quizzes_generated = 0

if "summaries_generated" not in st.session_state:
    st.session_state.summaries_generated = 0

if "quizzes_completed" not in st.session_state:
    st.session_state.quizzes_completed = 0

if "flashcard_questions" not in st.session_state:
    st.session_state.flashcard_questions = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []



# SIDEBAR
with st.sidebar:

    st.markdown("# 📚 NoteMate")
    st.caption("Your personal study companion")

    st.divider()

    st.markdown("### MENU")

    pages = [
        "Dashboard",
        "My Notes",
        "Flashcards",
        "AI Quiz",
        "Study Progress",
        "AI Assistant"
    ]

    for page in pages:
        if st.button(page, use_container_width=True):
            st.session_state.page = page

    st.divider()

    st.markdown("### YOUR PROFILE")
    st.write("👤 Student")
    st.caption("Keep learning. Keep growing.")



# DASHBOARD
if st.session_state.page == "Dashboard":

    st.markdown("# Good morning! 👋")
    st.markdown("### Ready to make learning easier today?")

    st.write("Welcome to your personal AI-powered study space.")

    # TOP METRICS
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="card">
        <div class="small">📚 Notes uploaded</div>
        <div class="metric">{len(st.session_state.uploaded_files)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
        <div class="small">🧠 Flashcard sets generated</div>
        <div class="metric">{st.session_state.flashcards_generated}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
        <div class="small">🎯 Quizzes completed</div>
        <div class="metric">{st.session_state.quizzes_completed}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## Your study progress")

    total_activities = (
        len(st.session_state.uploaded_files)
        + st.session_state.summaries_generated
        + st.session_state.flashcards_generated
        + st.session_state.quizzes_completed
    )

    weekly_progress = min(total_activities * 10, 100)

    st.progress(weekly_progress / 100)

    st.write(f"{weekly_progress}% activity goal completed!")

    st.caption("Progress is based on learning activities during this app session.")

    st.markdown("## Quick access")

    a, b, c = st.columns(3)

    with a:
        if st.button("📖 Open Notes"):
            st.session_state.page = "My Notes"
            st.rerun()

    with b:
        if st.button("🧠 Study Flashcards"):
            st.session_state.page = "Flashcards"
            st.rerun()

    with c:
        if st.button("✨ Take a Quiz"):
            st.session_state.page = "AI Quiz"
            st.rerun()


# MY NOTES

elif st.session_state.page == "My Notes":

    st.title("📖 My Notes")

    st.write("Upload your notes and keep everything organised.")

    uploaded_file = st.file_uploader(
        "Upload your study material",
        type=["pdf", "txt", "docx"]
    )

    if uploaded_file:

        notes_text = extract_text(uploaded_file)

        st.session_state.notes_text = notes_text

        st.session_state.current_file = uploaded_file.name
        st.session_state.uploaded_files.add(uploaded_file.name)

        st.markdown("### Current Document")

        st.info(f"📄 {st.session_state.current_file}")

        st.success("Your file has been uploaded successfully!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate Summary"):

                with st.spinner("Generating summary..."):
                    summary = generate_summary(notes_text)
                    st.session_state.summary = summary
                    st.session_state.summaries_generated += 1

        with col2:
             if st.button("🗑️ Clear File"):
                 st.session_state.pop("notes_text", None)
                 st.session_state.pop("summary", None)
                 st.session_state.pop("current_file", None) 

                 st.rerun()       

        if "summary" in st.session_state:

            st.subheader("AI Summary")

            st.write(st.session_state.summary)

    else:

        st.info("Upload a PDF, DOCX, or TXT file to begin.")
        


# FLASHCARDS
elif st.session_state.page == "Flashcards":

    st.title("🧠 Smart Flashcards")
    st.write("Test your memory with AI-generated flashcards!")

    if "notes_text" not in st.session_state:
        st.warning("Please upload your notes first in My Notes.")

    else:

        if st.button("✨ Generate Flashcards"):

            with st.spinner("Creating your flashcards..."):

                result = generate_flashcards(
                    st.session_state.notes_text
                )

                # Parse Gemini response
                cards = []
                current_question = None

                for line in result.splitlines():

                    line = line.strip()

                    if line.startswith("Q:"):
                        current_question = line[2:].strip()

                    elif line.startswith("A:") and current_question:
                        answer = line[2:].strip()

                        cards.append((current_question, answer))
                        current_question = None

                if cards:
                    st.session_state.flashcard_questions = cards
                    st.session_state.card = 0
                    st.session_state.show_answer = False

                    if "flashcards_generated" not in st.session_state:
                        st.session_state.flashcards_generated = 0

                    st.session_state.flashcards_generated += 1

                else:
                    st.error("Could not read the generated flashcards. Please try again.")

        if "flashcard_questions" in st.session_state:

            questions = st.session_state.flashcard_questions

            if questions and st.session_state.card < len(questions):
                question, answer = questions[st.session_state.card]
            else:
                st.warning("No flashcards available. Please generate flashcards from your notes.")
                st.stop()

            # Flashcard styling
            st.markdown("""
            <style>
            .st-key-flip_flashcard button {
                width: 100%;
                min-height: 250px;
                white-space: pre-wrap;
                text-align: center;
                font-size: 20px;
                font-weight: 600;
                border-radius: 18px;
                border: 2px solid var(--border-color);
                background-color: var(--secondary-background-color);
                color: var(--text-color);
                padding: 35px;
                transition: all 0.3s ease;
            }

            .st-key-flip_flashcard button:hover {
                border-color: #3478F6;
                transform: translateY(-3px);
            }
            </style>
            """, unsafe_allow_html=True)

            # Display front or back
            if st.session_state.show_answer:
                card_label = f"💡 ANSWER\n\n{answer}\n\n↻ Click to see question"
            else:
                card_label = f"❓ QUESTION\n\n{question}\n\n↻ Click to reveal answer"

            # Click anywhere on card to flip
            if st.button(
                card_label,
                key="flip_flashcard",
                use_container_width=True
            ):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                if st.button("⬅ Previous"):
                    st.session_state.card = (
                        st.session_state.card - 1
                    ) % len(questions)

                    st.session_state.show_answer = False
                    st.rerun()

            with col2:
                if st.button("Next ➡"):
                    st.session_state.card = (
                        st.session_state.card + 1
                    ) % len(questions)

                    st.session_state.show_answer = False
                    st.rerun()

            st.caption(
                f"Card {st.session_state.card + 1} of {len(questions)}"
            )




# AI QUIZ
elif st.session_state.page == "AI Quiz":

    st.title("✨ Interactive AI Quiz")
    st.write("Test your knowledge using your uploaded notes!")

    if "notes_text" not in st.session_state:

        st.warning("Please upload your notes first in My Notes.")

    else:

        if st.button("✨ Generate Quiz"):

            with st.spinner("Generating your quiz..."):

                result = generate_quiz(
                    st.session_state.notes_text
                )

                # Parse Gemini response
                quiz_questions = []
                current_question = None
                current_answer = None

                for line in result.splitlines():

                    line = line.strip()

                    if line.startswith("Question:"):

                        if current_question and current_answer:
                            quiz_questions.append(
                                (current_question, current_answer)
                            )

                        current_question = line.replace(
                            "Question:", ""
                        ).strip()

                        current_answer = None

                    elif line.startswith("Answer:"):

                        current_answer = line.replace(
                            "Answer:", ""
                        ).strip()

                if current_question and current_answer:
                    quiz_questions.append(
                        (current_question, current_answer)
                    )

                if quiz_questions:

                    st.session_state.quiz_questions = quiz_questions
                    st.session_state.quiz_index = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_done = False
                    st.session_state.quiz_feedback = ""

                    if "quizzes_generated" not in st.session_state:
                        st.session_state.quizzes_generated = 0

                    st.session_state.quizzes_generated += 1

                else:
                    st.error(
                        "Could not read the generated quiz. Please try again."
                    )

        # DISPLAY QUIZ

        if "quiz_questions" in st.session_state:

            questions = st.session_state.quiz_questions

            if not st.session_state.quiz_done:

                index = st.session_state.quiz_index

                if not questions:
                    st.warning(
                        "No quiz questions available. Please generate a new quiz."
                    )
                    st.stop()

                if index >= len(questions):
                    st.session_state.quiz_index = 0
                    index = 0

                question, correct_answer = questions[index]

                st.markdown(
                    f"### Question {index + 1} of {len(questions)}"
                )

                st.markdown(f"#### {question}")

                user_answer = st.text_input(
                    "Your answer:",
                    key=f"quiz_input_{index}"
                )

                if not st.session_state.quiz_answered:

                    if st.button("Submit Answer"):

                        if not user_answer.strip():

                            st.warning("Please enter your answer.")

                        else:

                            try:

                                with st.spinner("Evaluating your answer..."):

                                    is_correct, feedback = evaluate_answer(
                                        question,
                                        correct_answer,
                                        user_answer,
                                        st.session_state.notes_text
                                    )

                                if is_correct:

                                    st.session_state.quiz_score += 1

                                    st.session_state.quiz_feedback = (
                                        f"🎉 Correct answer! {feedback}"
                                    )

                                else:

                                    st.session_state.quiz_feedback = (
                                        f"❌ Not quite! {feedback}\n\n"
                                        f"Correct answer: {correct_answer}"
                                    )

                                st.session_state.quiz_answered = True
                                st.rerun()

                            except Exception as e:

                                st.error(
                                    "Unable to evaluate your answer right now. "
                                    "Please try submitting again."
                                )

                                st.caption(f"Error: {e}")

                # DISPLAY FEEDBACK

                if st.session_state.quiz_answered:

                    if st.session_state.quiz_feedback.startswith("🎉"):
                        st.success(st.session_state.quiz_feedback)

                    else:
                        st.error(st.session_state.quiz_feedback)

                    if st.button("Next Question ➡"):

                        if index + 1 < len(questions):

                            st.session_state.quiz_index += 1

                        else:

                            st.session_state.quiz_done = True

                        st.session_state.quiz_answered = False
                        st.session_state.quiz_feedback = ""

                        st.rerun()

            else:

                st.markdown("### 🎉 Quiz Completed!")

                score = st.session_state.quiz_score
                total = len(questions)

                st.progress(score / total if total > 0 else 0)

                st.success(
                    f"Your Score: {score}/{total}"
                )

                if st.button("Try Another Quiz"):

                    del st.session_state.quiz_questions

                    st.session_state.quiz_done = False
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_feedback = ""

                    st.rerun()



# STUDY PROGRESS
elif st.session_state.page == "Study Progress":

    st.title("📊 Study Progress")
    st.write("Track your actual learning activity.")

    # ACTUAL ACTIVITY COUNTS

    notes_count = len(st.session_state.get("uploaded_files", set()))

    summaries_count = st.session_state.get("summaries_generated", 0)

    flashcards_count = st.session_state.get("flashcards_generated", 0)

    quizzes_count = st.session_state.get("quizzes_generated", 0)

    completed_count = st.session_state.get("quizzes_completed", 0)

    # ACTIVITY METRICS

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("📚 Notes Uploaded", notes_count)

    with c2:
        st.metric("📝 Summaries Generated", summaries_count)

    with c3:
        st.metric("🧠 Flashcard Sets", flashcards_count)

    c4, c5 = st.columns(2)

    with c4:
        st.metric("✨ Quizzes Generated", quizzes_count)

    with c5:
        st.metric("🎯 Quizzes Completed", completed_count)

    st.divider()

    # STUDY ACTIVITY

    st.subheader("Your Learning Activity")

    activities = [
        ("Notes uploaded", notes_count),
        ("Summaries generated", summaries_count),
        ("Flashcard sets generated", flashcards_count),
        ("Quizzes generated", quizzes_count),
        ("Quizzes completed", completed_count)
    ]

    for activity, count in activities:

        st.write(f"**{activity}**")

        st.progress(min(count / 5, 1.0))

        st.caption(f"{count} activities")

    st.divider()

    # ACHIEVEMENTS

    st.subheader("🏆 Your Achievements")

    if notes_count >= 1:
        st.success("📚 First Notes Uploaded")

    if summaries_count >= 1:
        st.success("📝 First Summary Generated")

    if flashcards_count >= 1:
        st.success("🧠 First Flashcard Set Created")

    if completed_count >= 1:
        st.success("🎯 First Quiz Completed")

    if not any([
        notes_count,
        summaries_count,
        flashcards_count,
        completed_count
    ]):
        st.info("Start studying to unlock your achievements!")

    if "quizzes_completed" not in st.session_state:
        st.session_state.quizzes_completed = 0

    st.session_state.quizzes_completed += 1

# AI ASSISTANT
elif st.session_state.page == "AI Assistant":

    st.title("💬 Your AI Study Assistant")
    st.write("Ask questions, explore concepts, and get help with your studies!")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Ask me anything...")

    if user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        try:
            with st.spinner("Thinking..."):

                notes = st.session_state.get("notes_text", "")

                response = ask_question(notes, user_input)

        except Exception as e:
            response = "Sorry, I couldn't get an answer right now. Please try again later."

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        with st.chat_message("assistant"):
            st.write(response)




