# src/agents/quiz_agent.py
from typing import Dict, Any, List, Tuple
from datetime import datetime
from observability.logging_setup import get_logger
from tools.persistence import init_db, load_memory, save_memory
from tools.code_executor import grade_answer

logger = get_logger("quiz_agent")


class QuizAgent:
    """
    QuizAgent:
    - Given a lesson dict, generate a short quiz (3 questions) derived from the lesson's worked example.
    - Grade answers using grade_answer (safe tool).
    - Persist quiz results into memory under 'last_quiz' and append to 'quizzes'.
    """

    def __init__(self, conn=None):
        self.conn = conn or init_db()

    def _derive_questions_from_example(self, worked_example: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Derive simple variation questions from the worked example.
        Returns list of tuples: (question_text, expected_expression)
        Example: if worked_example has equation "2*x + 3 = 11" and solution 4,
        produce 3 variations with different constants/coefs.
        """
        eq = worked_example.get("equation_str")
        solution = worked_example.get("solution")
        questions = []

        # Base question: same pattern
        questions.append((f"Solve for x: {eq}", eq))

        # Variation 1: change RHS by +2 => expected new solution
        try:
            import re
            # crude parsing to change RHS numeric value
            left, right = eq.split("=")
            right_val = float(right.strip())
            new_right1 = int(right_val + 2)
            q1 = (f"Solve for x: {left.strip()} = {new_right1}", f"{left.strip()} = {new_right1}")
            questions.append(q1)
            # Variation 2: change coefficient a by +1 if present like '2*x'
            m = re.search(r"(?P<a>-?\d+)\*x", left.replace(" ", ""))
            if m:
                a = int(m.group("a"))
                new_a = a + 1
                left2 = left.replace(f"{a}*x", f"{new_a}*x")
                q2 = (f"Solve for x: {left2} = {right.strip()}", f"{left2} = {right.strip()}")
                questions.append(q2)
            else:
                # fallback simple arithmetic change
                questions.append((f"Solve for x: {left.strip()} = {int(right_val)-1}", f"{left.strip()} = {int(right_val)-1}"))
        except Exception:
            # fallback trivial repeats if parsing fails
            questions = [(f"Solve for x: {eq}", eq)]

        # limit to 3 questions
        return questions[:3]

    def generate_quiz(self, user_id: str, lesson: Dict[str, Any]) -> Dict[str, Any]:
        trace_id = f"quiz-gen-{user_id}"
        logger.info("intent_before_quiz_generate", extra={"extra": {"trace_id": trace_id, "user_id": user_id}})
        worked = lesson.get("worked_example", {})
        questions = self._derive_questions_from_example(worked)
        quiz = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "questions": [{"q": q, "expected_expr": exp} for q, exp in questions]
        }
        # Persist skeleton quiz (no answers yet)
        mem = load_memory(self.conn, user_id) or {}
        mem.setdefault("quizzes", [])
        mem["quizzes"].append({"quiz_meta": quiz, "answers": None})
        mem["last_quiz"] = {"quiz_meta": quiz, "answers": None}
        save_memory(self.conn, user_id, mem)
        logger.info("quiz_generated", extra={"extra": {"trace_id": trace_id, "user_id": user_id, "num_q": len(questions)}})
        return quiz

    def grade_quiz(self, user_id: str, quiz: Dict[str, Any], user_answers: List[str]) -> Dict[str, Any]:
        """
        Grade the quiz using grade_answer for each expected_expr.
        Returns result with per-question grading and summary.
        """
        trace_id = f"quiz-grade-{user_id}"
        logger.info("intent_before_quiz_grade", extra={"extra": {"trace_id": trace_id, "user_id": user_id}})
        per_q = []
        correct_count = 0
        qs = quiz.get("questions", [])
        for idx, q in enumerate(qs):
            expected = q["expected_expr"]
            ans = user_answers[idx] if idx < len(user_answers) else ""
            grade = grade_answer(expected, ans)
            per_q.append({
                "q_index": idx,
                "question": q["q"],
                "expected": grade["expected"],
                "user_answer_raw": ans,
                "user_answer_parsed": grade["user"],
                "correct": grade["correct"],
                "explanation": grade["explanation"]
            })
            if grade["correct"]:
                correct_count += 1
            logger.info("quiz_question_graded", extra={"extra": {"trace_id": trace_id, "q_index": idx, "correct": grade["correct"]}})

        score = int((correct_count / max(1, len(qs))) * 100)
        result = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "per_question": per_q,
            "correct_count": correct_count,
            "total_questions": len(qs),
            "score_percent": score
        }

        # Update memory: append answers and update topic mastery simple delta
        mem = load_memory(self.conn, user_id) or {}
        mem.setdefault("quizzes", [])
        # replace last quiz skeleton with graded answers
        if mem.get("last_quiz"):
            mem["last_quiz"]["answers"] = result
            # also update the last appended quiz
            if mem["quizzes"]:
                mem["quizzes"][-1]["answers"] = result
        else:
            mem["quizzes"].append({"quiz_meta": quiz, "answers": result})
            mem["last_quiz"] = {"quiz_meta": quiz, "answers": result}

        # Simple mastery update rule: average with prior mastery
        prior = mem.get("topic_mastery", {}).get("linear_equations", 0)
        new_mastery = int((prior + score) / 2) if prior else score
        mem.setdefault("topic_mastery", {})["linear_equations"] = new_mastery

        save_memory(self.conn, user_id, mem)
        logger.info("quiz_graded", extra={"extra": {"trace_id": trace_id, "user_id": user_id, "score": score, "new_mastery": new_mastery}})

        return result
