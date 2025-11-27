# src/smoke_lesson.py
from agents.assessment_agent import AssessmentAgent
from agents.lesson_agent import LessonAgent
from tools.persistence import init_db, load_memory
from observability.logging_setup import get_logger

logger = get_logger("smoke_lesson")

def run_demo():
    conn = init_db()
    user_id = "student_001"
    assessor = AssessmentAgent(conn=conn)
    lessoner = LessonAgent(conn=conn)

    # Simulate a diagnostic run (some answers incorrect to see targeted lesson)
    # Example: Q1 correct, Q2 incorrect, Q3 incorrect
    user_answers = ["4", "3", "0"]  # note: Q2 should be 5, Q3 should be -3
    assessment_result = assessor.run_diagnostic(user_id, user_answers)
    print("Assessment Result:", assessment_result)

    # Plan a lesson based on diagnostics
    lesson = lessoner.plan(user_id, assessment_result.get("per_question") and [assessment_result] or [])
    # For clarity: our planner expects diagnostics list; here we pass [assessment_result]
    print("Generated Lesson:", lesson)

    # Show memory snapshot
    mem = load_memory(conn, user_id)
    print("Memory snapshot after lesson:", mem)

if __name__ == "__main__":
    run_demo()
