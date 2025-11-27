# streamlit_app/app.py
import streamlit as st
import json
import pandas as pd

# local imports
from api import (
    run_assessment,
    generate_lesson,
    generate_quiz,
    grade_quiz,
    generate_feedback,
    evaluation_report,
    read_memory,
    write_preference
)

# ------------------------------------------------------------------
# Page Configuration + UI Polish
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Adaptive Learning Coach",
    page_icon="📘",
    layout="wide",
)

# Custom CSS for a cleaner interface
st.markdown("""
<style>
    .metric-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #DDD;
        background-color: #FAFAFA;
        margin-bottom: 15px;
    }
    .header-box {
        padding: 12px;
        border-radius: 8px;
        background-color: #EEF7FF;
        border-left: 4px solid #4299E1;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Utility UI helpers
# ------------------------------------------------------------------
def show_json(obj):
    st.code(json.dumps(obj, indent=2, ensure_ascii=False), language="json")


# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = ""


# ------------------------------------------------------------------
# Sidebar UI – User setup
# ------------------------------------------------------------------
with st.sidebar:
    st.title("Student Session")
    st.session_state.user_id = st.text_input(
        "Name / User ID", 
        value=st.session_state.user_id
    )

    learning_style = st.selectbox("Learning style", ["textual", "visual", "step-by-step"])
    difficulty = st.selectbox("Difficulty", ["easy", "normal", "hard"], index=1)

    if st.button("Save preferences"):
        uid = st.session_state.user_id.strip()
        if uid == "":
            st.warning("Enter a User ID first.")
        else:
            write_preference(uid, learning_style, difficulty)
            st.success("Preferences saved.")

    st.markdown("---")
    st.caption("Adaptive Coach · Streamlit UI")


# ------------------------------------------------------------------
# Main UI
# ------------------------------------------------------------------
st.title("📘 Adaptive Learning Coach")
st.write("Navigate through Assessment, Lessons, Quizzes, Feedback, Reports, and the Learning Loop.")


# ------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Assessment",
    "Lesson",
    "Quiz",
    "Feedback",
    "Report",
    "Learning Loop"
])

# ============================================================
# TAB 1 — Assessment
# ============================================================
with tab1:
    st.header("📝 Assessment")
    st.write("Answer the diagnostic questions.")

    q1 = st.text_input("1) Solve for x: 2*x + 3 = 11")
    q2 = st.text_input("2) Solve for x: 5*x - 4 = 21")
    q3 = st.text_input("3) Solve for x: 3*x + 9 = 0")

    answers = [q1, q2, q3]
    uid = st.session_state.user_id.strip() or "student_demo"

    if st.button("Submit Assessment"):
        with st.spinner("Grading assessment..."):
            result = run_assessment(uid, answers)

        st.success("Assessment complete.")
        show_json(result)

        mem = read_memory(uid)
        st.subheader("Stored Memory")
        show_json(mem)


# ============================================================
# TAB 2 — Lesson
# ============================================================
with tab2:
    st.header("📚 Generated Lesson")
    st.write("Lesson tailored to the user preferences.")

    if st.button("Generate Lesson"):
        uid = st.session_state.user_id.strip() or "student_demo"
        prefs = read_memory(uid).get("preferences", {})

        with st.spinner("Generating lesson..."):
            lesson = generate_lesson(uid, prefs)

        st.subheader("Lesson Details")
        show_json(lesson)

        st.markdown("### Explanation")
        st.write(lesson.get("short_explanation", "No explanation available."))


# ============================================================
# TAB 3 — Quiz
# ============================================================
with tab3:
    st.header("🧠 Quiz")
    st.write("Practice questions based on the generated lesson.")

    if st.button("Generate Quiz"):
        uid = st.session_state.user_id.strip() or "student_demo"

        last_lesson = read_memory(uid).get("last_lesson")
        if last_lesson is None:
            st.error("Generate a lesson first.")
        else:
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(uid, last_lesson)

            st.session_state.latest_quiz = quiz
            st.success("Quiz ready! Scroll down to answer.")

    quiz = st.session_state.get("latest_quiz")
    if quiz:
        st.subheader("Questions")
        answers = {}

        for i, q in enumerate(quiz.get("questions", [])):
            st.write(f"Q{i+1}: {q['q']}")
            answers[i] = st.text_input(f"Answer Q{i+1}", key=f"quiz_answer_{i}")

        if st.button("Submit Quiz"):
            uid = st.session_state.user_id.strip() or "student_demo"

            with st.spinner("Grading..."):
                graded = grade_quiz(uid, answers)

            st.session_state.last_graded = graded
            st.success("Quiz graded.")
            show_json(graded)


# ============================================================
# TAB 4 — Feedback
# ============================================================
with tab4:
    st.header("💡 Feedback & Recommendations")

    if st.button("Generate Feedback"):
        uid = st.session_state.user_id.strip() or "student_demo"

        with st.spinner("Analyzing your quiz answers..."):
            fb = generate_feedback(uid)

        st.success("Feedback generated!")
        show_json(fb)

    if st.button("Show Stored Memory"):
        uid = st.session_state.user_id.strip() or "student_demo"
        show_json(read_memory(uid))


# ============================================================
# TAB 5 — Report
# ============================================================
with tab5:
    st.header("📊 Evaluation Report")

    uid = st.session_state.user_id.strip() or "student_demo"

    if st.button("Run Evaluation Report"):
        with st.spinner("Evaluating progress..."):
            res = evaluation_report(uid)

        show_json(res)

    st.subheader("Mastery Progress")
    mastery = read_memory(uid).get("topic_mastery", {}).get("linear_equations", 0)
    st.progress(mastery / 100)
    st.metric("Mastery (%)", mastery)

    # Line chart (mastery history)
    history = read_memory(uid).get("mastery_history", [])
    if history:
        df = pd.DataFrame(history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("timestamp")["mastery"])
    else:
        st.info("No mastery history yet. Complete a quiz to start tracking!")


# ============================================================
# TAB 6 — Learning Loop (Lesson → Quiz → Feedback)
# ============================================================
with tab6:
    st.header("🔁 Adaptive Learning Loop")
    st.write("Automated flow: Lesson → Quiz → Feedback")

    uid = st.session_state.user_id.strip() or "student_demo"
    run_assess = st.checkbox("Run assessment before each loop", value=False)

    if st.button("Start Learning Loop"):
        # Optional assessment
        if run_assess:
            with st.spinner("Running assessment..."):
                run_assessment(uid, ["", "", ""])
            st.success("Assessment complete.")

        # Lesson
        prefs = read_memory(uid).get("preferences", {})
        with st.spinner("Generating lesson..."):
            lesson = generate_lesson(uid, prefs)
        st.session_state.loop_lesson = lesson
        st.success("Lesson created.")

        # Quiz
        with st.spinner("Generating quiz..."):
            quiz = generate_quiz(uid, lesson)
        st.session_state.loop_quiz = quiz
        st.success("Quiz ready.")

    # Show quiz
    quiz = st.session_state.get("loop_quiz")
    if quiz:
        st.subheader("Quiz Questions")
        loop_answers = {}

        for i, q in enumerate(quiz.get("questions", [])):
            st.write(f"Q{i+1}: {q['q']}")
            loop_answers[i] = st.text_input(f"Answer Q{i+1}", key=f"loop_answer_{i}")

        if st.button("Submit Loop Quiz"):
            with st.spinner("Grading quiz..."):
                graded = grade_quiz(uid, loop_answers)
            st.session_state.loop_graded = graded
            st.success("Quiz graded.")

    # Show feedback
    graded = st.session_state.get("loop_graded")
    if graded:
        st.subheader("Feedback")

        with st.spinner("Generating feedback..."):
            fb = generate_feedback(uid)
        st.json(fb)

        st.markdown("### Next Cycle")
        if st.button("Next Lesson"):
            st.session_state.pop("loop_quiz", None)
            st.session_state.pop("loop_graded", None)
            st.success("Click 'Start Learning Loop' to continue.")

