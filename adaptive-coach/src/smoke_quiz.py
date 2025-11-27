# src/smoke_quiz.py
from tools.persistence import init_db, load_memory
from agents.assessment_agent import AssessmentAgent
from agents.lesson_agent import LessonAgent
from agents.quiz_agent import QuizAgent
from eval.evaluator import run_evaluation
from observability.logging_setup import get_logger

logger = get_logger("smoke_quiz")

def run_full_demo():
    conn = init_db()
    user_id = "student_test_01"

    # Ensure memory has a baseline profile so evaluator can find it
    from tools.persistence import save_memory
    baseline_mem = {
        "name": "Test Student 1",
        "topic_mastery": {"linear_equations": 33},
        "preferred_explanation": "concise",
        "diagnostics": []
    }
    save_memory(conn, user_id, baseline_mem)
    logger.info("baseline_memory_saved", extra={"extra": {"user_id": user_id}})

    # 1. Assessment (simulate poor performance)
    assessor = AssessmentAgent(conn=conn)
    assessment = assessor.run_diagnostic(user_id, ["4", "3", "0"])  # score 33 expected
    print("Assessment:", assessment)

    # 2. Lesson
    lessoner = LessonAgent(conn=conn)
    lesson = lessoner.plan(user_id, [assessment])
    print("Lesson:", lesson["short_explanation"])

    # 3. Quiz generation
    quiz_agent = QuizAgent(conn=conn)
    quiz = quiz_agent.generate_quiz(user_id, lesson)
    print("Quiz questions:")
    for i,q in enumerate(quiz["questions"]):
        print(i+1, q["q"])

    # 4. Simulate student taking the quiz with improved answers (post-lesson)
    # We simulate improvement: correct answers now
    # Determine correct answers from expected_expr by solving them using code_executor
    # For simplicity, provide answers known from lesson worked_example solution variants
    user_answers_post = []
    for q in quiz["questions"]:
        expected_expr = q["expected_expr"]
        # parse expected with same logic as code_executor
        from tools.code_executor import solve_for_x
        sol = solve_for_x(expected_expr)
        user_answers_post.append(str(int(sol)) if sol is not None and float(sol).is_integer() else str(sol))

    print("Simulated post-quiz answers:", user_answers_post)
    graded = quiz_agent.grade_quiz(user_id, quiz, user_answers_post)
    print("Quiz graded:", graded)

    # 5. Run evaluation against golden_cases.json (this file includes case for student_test_01)
    eval_results = run_evaluation(
    conn=conn,
    golden_path="src/eval/golden_cases.json"
    )
    print("Evaluation results:", eval_results)

    # 6. Final memory snapshot
    mem = load_memory(conn, user_id)
    print("Final memory:", mem)

if __name__ == "__main__":
    run_full_demo()
