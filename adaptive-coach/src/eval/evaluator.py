# src/eval/evaluator.py
import json
from typing import Dict, Any
from observability.logging_setup import get_logger
from tools.persistence import init_db, load_memory

logger = get_logger("evaluator")

def simple_numeric_improvement_check(pre_score: int, post_score: int, min_delta: int) -> Dict[str, Any]:
    result = {
        "pre_score": pre_score,
        "post_score": post_score,
        "delta": post_score - pre_score,
        "passed": (post_score - pre_score) >= min_delta
    }
    return result

def lm_as_judge_stub(expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder for an LLM judge. For now perform a deterministic comparison:
    - If expected contains 'expected_score_min', check post.score >= that.
    - Return a dict with 'score' (0-100) and 'comment'.
    Swap this stub with a real LLM wrapper later.
    """
    post_score = actual.get("score_percent", 0)
    expected_min = expected.get("expected_score_min", 0)
    delta_min = expected.get("expected_delta_min", 0)
    pre_score = actual.get("pre_score", 0)
    delta = post_score - pre_score
    passed = (post_score >= expected_min) and (delta >= delta_min)
    commentary = "Passed" if passed else f"Failed: post {post_score} pre {pre_score} delta {delta} (needs >= {delta_min})"
    # map bool to numeric score 0/100
    return {"score": 100 if passed else 0, "comment": commentary, "passed": passed}

def run_evaluation(conn=None, golden_path: str = "adaptive-coach/src/eval/golden_cases.json"):
    conn = conn or init_db()
    with open(golden_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    results = []
    for c in cases:
        user_id = c.get("user_id")
        mem = load_memory(conn, user_id)
        # extract pre and post
        pre = c.get("pre_assessment", {})
        # try to find actual post in memory
        last_quiz = mem.get("last_quiz", {})
        answers = last_quiz.get("answers") or {}
        # build actual structure for judge
        actual = {
            "score_percent": answers.get("score_percent", 0),
            "pre_score": pre.get("score_percent", 0)
        }
        judge_expected = c.get("post_quiz", {})
        judgement = lm_as_judge_stub(judge_expected, actual)
        result = {
            "case_id": c.get("id"),
            "user_id": user_id,
            "actual": actual,
            "judgement": judgement
        }
        logger.info("eval_case_result", extra={"extra": result})
        results.append(result)
    return results
