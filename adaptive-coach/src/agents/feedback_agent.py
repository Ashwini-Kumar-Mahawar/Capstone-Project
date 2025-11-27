# src/agents/feedback_agent.py
from typing import Dict, Any, List, Optional
from datetime import datetime
from observability.logging_setup import get_logger
from tools.persistence import init_db, load_memory, save_memory
from tools.code_executor import grade_answer, solve_for_x
from observability.tracing import init_tracing

logger = get_logger("feedback_agent")
tracer = init_tracing("feedback_agent")  # simple local tracer

def deterministic_hint_for_mistake(question: str, expected: float, user_val: Optional[float]) -> str:
    """
    Produce a concise deterministic hint explaining the likely mistake.
    We inspect numeric relationship and give a short targeted hint.
    """
    if user_val is None:
        return "I couldn't parse your answer. Make sure to submit only the numeric value for x (for example '4' or '-3')."

    # Common mistake types
    if abs(user_val - expected) < 0.5 and not user_val == expected:
        return f"You were close. Check arithmetic when moving constants. Expected {expected} but got {user_val}."
    # sign mistakes
    if user_val == -expected:
        return "It looks like you forgot to change sign when moving a term across the equals sign."
    # simple off-by-one
    if abs(user_val - expected) == 1:
        return "Off by one — double-check the arithmetic steps (subtract/add) when isolating x."
    # otherwise generic hint
    return "Verify you first subtracted/added the constant term, then divided by the coefficient. Show each step."

def build_step_by_step_explanation(question: str, expected_expr: str, user_answer_raw: str) -> Dict[str, Any]:
    """
    Build a small structured feedback object:
      - parsed expected and user values
      - correction steps (deterministic)
      - hint

    Signature accepts:
      question: original question text (for context)
      expected_expr: the expected equation string like "2*x+3=11"
      user_answer_raw: the raw answer string provided by the user
    """
    # compute expected numeric solution (if possible)
    exp_val = solve_for_x(expected_expr) if expected_expr else None

    # parse user's numeric value if possible
    try:
        ua = user_answer_raw.strip()
        if ua.lower().startswith("x="):
            ua = ua.split("=", 1)[1]
        user_val = float(ua)
    except Exception:
        user_val = None

    # deterministic corrective steps (for a*x + b = c)
    steps = []
    steps.append(f"Target question: {question}")
    steps.append(f"Target equation: {expected_expr}")
    if exp_val is not None:
        steps.append(f"Expected solution: x = {exp_val}")
    else:
        steps.append("Could not compute expected solution deterministically.")

    # Add a short worked checklist the student can follow
    steps.append("Checklist:")
    steps.append("1) Move the constant term to the right side (subtract/add).")
    steps.append("2) Divide both sides by the coefficient of x.")
    steps.append("3) Substitute your solution back to check.")

    hint = deterministic_hint_for_mistake(question=question, expected=exp_val if exp_val is not None else 0, user_val=user_val)
    return {
        "question": question,
        "expected_expr": expected_expr,
        "expected_value": exp_val,
        "user_value": user_val,
        "steps": steps,
        "hint": hint
    }


class FeedbackAgent:
    """
    FeedbackAgent:
    - For each incorrectly answered quiz question, produce:
        * a deterministic explanation & checklist,
        * an optional LLM-expanded feedback text (if llm_hook provided)
    - Persist feedback to memory under 'last_feedback' and append to 'feedbacks'
    - Emit tracing spans for the feedback generation step to support observability
    """

    def __init__(self, conn=None, llm_hook: Optional[callable] = None):
        self.conn = conn or init_db()
        self.llm_hook = llm_hook
        # reuse tracer from tracing module
        from opentelemetry import trace
        self.tracer = trace.get_tracer("feedback_agent")

    def provide_feedback(self, user_id: str, quiz_answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        quiz_answers: the graded quiz result structure returned by QuizAgent.grade_quiz (contains per_question etc.)
        Returns feedback dict with per-question feedback and overall guidance.
        """
        trace_id = f"feedback-{user_id}"
        logger.info("intent_before_feedback", extra={"extra": {"trace_id": trace_id, "user_id": user_id}})

        feedback_items = []
        with self.tracer.start_as_current_span("feedback-generation"):
            for q in quiz_answers.get("per_question", []):
                if q.get("correct"):
                    # short praise message
                    item = {
                        "q_index": q["q_index"],
                        "status": "correct",
                        "message": "Good job — solution is correct.",
                        "details": {"expected": q.get("expected"), "user": q.get("user_answer_parsed")}
                    }
                else:
                    # deterministic analysis
                    det = build_step_by_step_explanation(q.get("question"), q.get("expected"), q.get("user_answer_raw"))
                    item = {
                        "q_index": q["q_index"],
                        "status": "incorrect",
                        "message": "See step-by-step guidance and hint below.",
                        "details": det
                    }
                    # optional LLM expansion
                    if self.llm_hook:
                        try:
                            # pass a concise prompt; llm_hook returns expanded text
                            expanded = self.llm_hook({
                                "question": q.get("question"),
                                "expected_expr": q.get("expected"),
                                "user_answer": q.get("user_answer_raw"),
                                "deterministic": det
                            })
                            item["llm_expanded"] = expanded
                        except Exception as e:
                            logger.info("llm_hook_failed", extra={"extra": {"error": str(e), "user_id": user_id}})
                feedback_items.append(item)

        # assemble feedback report
        report = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "quiz_score": quiz_answers.get("score_percent"),
            "items": feedback_items
        }

        # persist
        mem = load_memory(self.conn, user_id) or {}
        mem.setdefault("feedbacks", [])
        mem["feedbacks"].append(report)
        mem["last_feedback"] = report
        save_memory(self.conn, user_id, mem)

        logger.info("feedback_saved", extra={"extra": {"trace_id": trace_id, "user_id": user_id, "score": report["quiz_score"]}})
        return report
