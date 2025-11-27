# src/smoke_assessment.py
from agents.assessment_agent import AssessmentAgent
from tools.persistence import init_db
from observability.logging_setup import get_logger

logger = get_logger("smoke_assessment")

def run_demo():
    conn = init_db()
    agent = AssessmentAgent(conn=conn)
    user_id = "student_001"

    print("Running assessment for user:", user_id)
    # Simulate a student providing answers (strings). Change these to test different outcomes.
    # Here: Q1: x=4, Q2: x=5, Q3: x=-3  (all correct)
    user_answers_all_correct = ["4", "5", "-3"]
    result_all_correct = agent.run_diagnostic(user_id, user_answers_all_correct)
    print("Result (all correct):", result_all_correct)

    # Simulate partially correct
    user_answers_some = ["4", "3", "-3"]  # Q2 incorrect
    result_some = agent.run_diagnostic(user_id, user_answers_some)
    print("Result (some correct):", result_some)

    # Load memory to validate persistence
    from tools.persistence import load_memory
    mem = load_memory(conn, user_id)
    print("Memory snapshot after diagnostics:", mem)

if __name__ == "__main__":
    run_demo()
