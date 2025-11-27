# src/agents/lesson_agent.py
import random
from datetime import datetime
from typing import Dict, Any, Optional

from observability.logging_setup import get_logger
from tools.persistence import init_db, load_memory, save_memory
import sympy as sp

logger = get_logger("lesson_agent")


def generate_linear_equation_example(a: int = None, b: int = None, c: int = None) -> Dict[str, Any]:
    """
    Build a simple linear equation of the form a*x + b = c (integers),
    solve it symbolically with sympy, and produce step-by-step reasoning.
    Returns a dict:
      {
        "equation_str": "2*x + 3 = 11",
        "solution": 4.0,
        "steps": ["2*x + 3 = 11", "2*x = 8", "x = 4"]
      }
    """
    # Choose random coefficients if not given (avoid zero for a)
    if a is None:
        a = random.choice([1, 2, 3, 4, 5])
    if b is None:
        b = random.choice([-6, -4, -2, 0, 2, 3, 4])
    if c is None:
        # ensure solution is integer by picking x_sol then computing c = a*x_sol + b
        x_sol = random.choice([-3, -2, -1, 1, 2, 3, 4, 5])
        c = a * x_sol + b

    x = sp.symbols('x')
    left = f"{a}*x + ({b})" if b < 0 else f"{a}*x + {b}"
    equation = f"{left} = {c}"

    # Solve with sympy
    sol = sp.solve(sp.Eq(sp.sympify(a)*x + sp.sympify(b), sp.sympify(c)), x)
    solution = float(sol[0].evalf()) if sol else None

    # Build human steps:
    steps = []
    steps.append(f"Start: {equation}")
    # isolate ax term
    if b != 0:
        steps.append(f"Subtract {b} from both sides: {a}*x = {c - b}")
    else:
        steps.append(f"No subtraction needed: {a}*x = {c}")
    # divide by a
    if a != 1:
        steps.append(f"Divide both sides by {a}: x = {(c - b)/a}")
    else:
        steps.append(f"x = {c - b}")
    return {
        "equation_str": equation,
        "solution": solution,
        "steps": steps
    }


class LessonAgent:
    """
    Lightweight Lesson Planner:
    - Accepts the assessment result structure and produces a short micro-lesson.
    - Stores lesson into persistent memory (under 'last_lesson' and appends to 'lessons').
    - If an LLM is available, you can hook `expand_with_llm(lesson_text)` to produce richer text.
    """

    def __init__(self, conn=None, llm_hook: Optional[callable] = None):
        self.conn = conn or init_db()
        # Optional hook: a function that takes short lesson dict and returns expanded lesson text
        self.llm_hook = llm_hook

    def _build_short_lesson_text(self, topic: str, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct a micro-lesson based on topic and diagnostic summary.
        For this capstone we focus on 'linear_equations'.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        # simple diagnosis: use latest diagnostic score
        latest_diag = diagnostics[-1] if diagnostics else {}
        score = latest_diag.get("score_percent", 0)

        # Decide focus area
        if score >= 80:
            focus = "Practice solving linear equations quickly and check steps."
            difficulty = "Practice"
        elif score >= 50:
            focus = "Work on correctly isolating variables and handling negative constants."
            difficulty = "Remedial"
        else:
            focus = "Begin with isolating the variable, move step-by-step, and verify each operation."
            difficulty = "Foundational"

        # Create a worked example programmatically
        example = generate_linear_equation_example()

        lesson = {
            "topic": topic,
            "created_at": timestamp,
            "difficulty": difficulty,
            "learning_objectives": [
                "Isolate the variable x in single-variable linear equations",
                "Perform arithmetic operations on both sides of the equation",
                "Check solutions by substitution"
            ],
            "focus": focus,
            "short_explanation": (
                "To solve equations like a*x + b = c, first move constants to the right side "
                "by subtracting b, then divide by a to get x. Keep each step explicit."
            ),
            "worked_example": example,
            "practice_prompt": "Solve 3 similar equations and check your steps. Try both positive and negative constants.",
            "score_prior": score
        }

        # Optionally expand text with an LLM if hook provided (no keys in repo)
        if self.llm_hook:
            try:
                lesson["expanded_explanation"] = self.llm_hook(lesson["short_explanation"])
            except Exception as e:
                logger.info("llm_hook_failed", extra={"extra": {"error": str(e)}})

        return lesson

    def plan(self, user_id: str, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point:
        - Build a lesson tailored to diagnostics
        - Save to DB under last_lesson and append to lessons
        - Emit structured logs for observability
        """
        trace_id = f"lesson-{user_id}"
        logger.info("intent_before_lesson_plan", extra={"extra": {"trace_id": trace_id, "user_id": user_id}})

        # Build lesson only for linear_equations (for this capstone)
        lesson = self._build_short_lesson_text("linear_equations", diagnostics)

        # Persist lesson into memory
        mem = load_memory(self.conn, user_id) or {}
        mem.setdefault("lessons", [])
        mem["lessons"].append(lesson)
        mem["last_lesson"] = lesson
        save_memory(self.conn, user_id, mem)

        logger.info("lesson_planned", extra={"extra": {"trace_id": trace_id, "user_id": user_id, "topic": lesson["topic"], "difficulty": lesson["difficulty"]}})

        return lesson
