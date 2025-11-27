# src/smoke_feedback.py
from tools.persistence import init_db, save_memory, load_memory
from agents.assessment_agent import AssessmentAgent
from agents.lesson_agent import LessonAgent
from agents.quiz_agent import QuizAgent
from agents.feedback_agent import FeedbackAgent
from observability.logging_setup import get_logger

logger = get_logger("smoke_feedback")

def run_full_flow():
    conn = init_db()
    user_id = "student_test_feedback"

    # Seed baseline memory for this user so evaluator later can read it
    baseline = {
        "name": "Feedback Test",
        "topic_mastery": {"linear_equations": 30},
        "preferred_explanation": "concise",
        "diagnostics": []
    }
    save_memory(conn, user_id, baseline)
    logger.info("baseline_saved", extra={"extra": {"user_id": user_id}})

    # 1. Assessment (simulate poor performance)
    assessor = AssessmentAgent(conn=conn)
    assessment = assessor.run_diagnostic(user_id, ["4", "3", "0"])  # expectation: score 33
    print("Assessment result score:", assessment["score_percent"])

    # 2. Lesson
    lessoner = LessonAgent(conn=conn)
    lesson = lessoner.plan(user_id, [assessment])
    print("Lesson focus:", lesson["focus"])
    print("Worked example:", lesson["worked_example"])

    # 3. Quiz generation
    quiz_agent = QuizAgent(conn=conn)
    quiz = quiz_agent.generate_quiz(user_id, lesson)
    print("Quiz generated with", len(quiz["questions"]), "questions")

    # 4. Student attempts the quiz with same wrong answers to show feedback
    user_answers = ["4", "3", "0"]  # still incorrect for some; simulate no improvement
    graded = quiz_agent.grade_quiz(user_id, quiz, user_answers)
    print("Post-quiz score:", graded["score_percent"])

    # 5. Feedback generation
    fb_agent = FeedbackAgent(conn=conn)
    feedback = fb_agent.provide_feedback(user_id, graded)
    print("Feedback report (abridged):")
    for item in feedback["items"]:
        print("-", f"Q{item['q_index']+1}", item["status"], "-", item.get("message"))
        if item["status"] == "incorrect":
            print("  Hint:", item["details"]["hint"])
            for s in item["details"]["steps"][:3]:
                print("   ", s)

    # 6. Show memory snapshot keys for verification
    mem = load_memory(conn, user_id)
    print("Memory keys:", list(mem.keys()))

if __name__ == "__main__":
    run_full_flow()
