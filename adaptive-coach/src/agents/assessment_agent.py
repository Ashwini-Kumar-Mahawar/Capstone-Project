# src/agents/assessment_agent.py
from typing import List, Dict, Any
from tools.persistence import init_db, save_memory, load_memory
from observability.logging_setup import get_logger
from tools.code_executor import grade_answer

logger = get_logger("assessment_agent")

class AssessmentAgent:
    """
    Minimal Assessment Agent that:
    - Holds a small diagnostic question set
    - Presents questions (here we simulate by reading prefilled answers)
    - Grades answers using the code_executor.grade_answer()
    - Saves diagnostic results into the memory DB under key 'last_diagnostic'
    """

    def __init__(self, conn=None):
        self.conn = conn or init_db()
        # Minimal diagnostic for linear equations (3 questions)
        # Questions are tuples: (prompt_text, expected_expression)
        self.questions = [
            ("Solve for x: 2*x + 3 = 11", "2*x + 3 = 11"),
            ("Solve for x: 5*x - 4 = 21", "5*x - 4 = 21"),
            ("Solve for x: 3*x + 9 = 0", "3*x + 9 = 0"),
        ]

    def run_diagnostic(self, user_id: str, user_answers: List[str]) -> Dict[str, Any]:
        """
        user_answers: list of strings corresponding to answers for each question
        Returns: result dict with per-question grading and summary
        """
        trace_id = f"assess-{user_id}"
        logger.info("intent_before_assessment", extra={"extra": {"trace_id": trace_id, "user_id": user_id}})
        per_q = []
        correct_count = 0
        for idx, (q, expected) in enumerate(self.questions):
            ans = user_answers[idx] if idx < len(user_answers) else ""
            grade = grade_answer(expected, ans)
            per_q.append({
                "q_index": idx,
                "question": q,
                "expected": grade["expected"],
                "user_answer_raw": ans,
                "user_answer_parsed": grade["user"],
                "correct": grade["correct"],
                "explanation": grade["explanation"]
            })
            if grade["correct"]:
                correct_count += 1
            logger.info("question_graded", extra={"extra": {"trace_id": trace_id, "q_index": idx, "correct": grade["correct"]}})

        score = 0 if not self.questions else int((correct_count / len(self.questions)) * 100)
        result = {
            "user_id": user_id,
            "timestamp": None,
            "per_question": per_q,
            "correct_count": correct_count,
            "total_questions": len(self.questions),
            "score_percent": score
        }

        # Save to memory under 'last_diagnostic' and update mastery for this topic (simple logic)
        mem = load_memory(self.conn, user_id) or {}
        mem.setdefault("diagnostics", [])
        mem["diagnostics"].append(result)
        # Simplest mastery update: store latest score for topic "linear_equations"
        mem.setdefault("topic_mastery", {})
        mem["topic_mastery"]["linear_equations"] = score
        save_memory(self.conn, user_id, mem)
        logger.info("assessment_completed", extra={"extra": {"trace_id": trace_id, "user_id": user_id, "score": score}})
        return result
