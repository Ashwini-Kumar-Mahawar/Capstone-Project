# streamlit_app/api.py
import os
import sys
from typing import Dict, Any

# Ensure src is importable when running from streamlit_app
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# Import your agents (adjust names if different)
from agents.assessment_agent import AssessmentAgent
from agents.lesson_agent import LessonAgent
from agents.quiz_agent import QuizAgent
from agents.feedback_agent import FeedbackAgent
from eval.evaluator import run_evaluation  # or your report builder

# Persistence helpers
from tools.persistence import init_db, save_memory, load_memory

# make sure init_db is called once
_conn = None
def get_conn():
    global _conn
    if _conn is None:
        _conn = init_db()  # uses DB_PATH in persistence
    return _conn

# UI-facing wrapper functions
def run_assessment(user_id: str, answers: list) -> Dict[str, Any]:
    """
    Run the diagnostic assessment using real user answers.
    """
    conn = get_conn()
    agent = AssessmentAgent(conn=conn)

    # Use real answers from Streamlit
    result = agent.run_diagnostic(user_id, answers)

    return result



def generate_lesson(user_id: str, preferences: dict = None):
    conn = get_conn()
    agent = LessonAgent(conn=conn)

    # Load previous diagnostic results from memory
    mem = read_memory(user_id)
    diagnostics = mem.get("diagnostics", [])

    # Call the real method name
    lesson = agent.plan(user_id, diagnostics)

    return lesson


def generate_quiz(user_id: str, lesson: Dict[str, Any]) -> Dict[str, Any]:
    """
    UI wrapper: generate a quiz based on the lesson.
    """
    conn = get_conn()
    agent = QuizAgent(conn=conn)

    # Correct call: pass both user_id and lesson
    quiz = agent.generate_quiz(user_id, lesson)

    return quiz



def grade_quiz(user_id: str, answers_dict: dict):
    """
    Grade quiz by:
    - fetching last_quiz from memory
    - converting streamlit answers into ordered list
    - calling agent.grade_quiz(user_id, quiz, user_answers)
    """
    conn = get_conn()
    agent = QuizAgent(conn=conn)

    # Load memory
    mem = read_memory(user_id)
    last_quiz = mem.get("last_quiz")

    if not last_quiz:
        raise ValueError("No quiz found. Please generate a quiz first.")

    quiz_meta = last_quiz.get("quiz_meta")
    if not quiz_meta:
        raise ValueError("Quiz metadata missing — cannot grade quiz.")

    # Convert dict {0:"ans", 1:"ans2"} → ["ans", "ans2"]
    # Guarantees order by index
    user_answers = [answers_dict[k] for k in sorted(answers_dict.keys())]

    # Call the agent correctly (3 parameters)
    graded = agent.grade_quiz(user_id, quiz_meta, user_answers)

    return graded


def generate_feedback(user_id: str):
    """
    Generate feedback by loading the user's last graded quiz
    and calling FeedbackAgent.provide_feedback().
    """
    conn = get_conn()
    agent = FeedbackAgent(conn=conn)

    # Load memory
    mem = read_memory(user_id)
    last_quiz = mem.get("last_quiz")

    if not last_quiz or not last_quiz.get("answers"):
        raise ValueError("No graded quiz found. Please complete a quiz before requesting feedback.")

    graded_quiz = last_quiz["answers"]

    # Call the correct method
    feedback = agent.provide_feedback(user_id, graded_quiz)

    return feedback


def evaluation_report(user_id: str) -> Dict[str, Any]:
    # If you have a function that builds a report and returns a dict
    conn = get_conn()
    # Example: run_evaluation returns a list of cases or a report
    results = run_evaluation(conn=conn, golden_path=os.path.join(SRC, "eval", "golden_cases.json"))
    return results

# memory helpers
def read_memory(user_id: str) -> Dict[str, Any]:
    conn = get_conn()
    return load_memory(conn, user_id)

def write_preference(user_id: str, learning_style: str, difficulty: str):
    conn = get_conn()
    mem = load_memory(conn, user_id) or {}
    prefs = mem.get("preferences", {})
    prefs["learning_style"] = learning_style
    prefs["difficulty_curve"] = difficulty
    mem["preferences"] = prefs
    save_memory(conn, user_id, mem)
    return mem
