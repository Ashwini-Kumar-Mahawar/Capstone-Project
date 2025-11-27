import streamlit as st
from api import run_assessment

st.set_page_config(
    page_title="Assessment",
    page_icon="📝",
)

st.title("📝 Math Assessment")
st.write("Answer all questions below. Your results will be graded instantly.")

# -----------------------------
# Question Inputs
# -----------------------------
st.subheader("Your Answers")

q1 = st.text_input("1) Solve for x: 2*x + 3 = 11", key="q1")
q2 = st.text_input("2) Solve for x: 5*x - 4 = 21", key="q2")
q3 = st.text_input("3) Solve for x: 3*x + 9 = 0", key="q3")

user_answers = [q1.strip(), q2.strip(), q3.strip()]

st.write("---")

# -----------------------------
# User ID
# -----------------------------
user_id = st.text_input("Enter your User ID:", value="student001")

# -----------------------------
# Submit Button Logic
# -----------------------------
if st.button("Submit Assessment"):
    if not user_id.strip():
        st.error("User ID is required.")
    elif any(ans == "" for ans in user_answers):
        st.error("Please answer all questions before submitting.")
    else:
        with st.spinner("Grading your answers..."):
            # Send answers to backend
            result = run_assessment(user_id, user_answers)

        st.success("Assessment Completed!")

        # -----------------------------
        # Score Display
        # -----------------------------
        st.subheader("Your Score")
        st.metric(
            label="Score (%)",
            value=result.get("score_percent", 0)
        )

        st.write("---")

        # -----------------------------
        # Detailed Breakdown
        # -----------------------------
        st.subheader("Question Breakdown")

        for item in result["per_question"]:
            correct = item["correct"]
            color = "green" if correct else "red"

            st.markdown(
                f"""
                <div style="border:1px solid #CCC; padding:12px; 
                            border-radius:8px; margin-bottom:12px; background:#FAFAFA;">
                    <b>Q{item['q_index']+1}:</b> {item['question']}<br>
                    <b>Your Answer:</b> {item['user_answer_raw']}<br>
                    <b>Status:</b> 
                    <span style="color:{color}; font-weight:bold">
                        {"Correct" if correct else "Incorrect"}
                    </span><br>
                    <b>Explanation:</b> {item['explanation']}
                </div>
                """,
                unsafe_allow_html=True
            )
