# src/tools/code_executor.py
"""
Safe math & algebra checker tool.
Provides helpers to grade numeric or algebraic answers for simple equations.
Uses sympy to symbolically solve simple linear equations and compare user answers.
"""
from typing import Dict, Any, Union
import sympy as sp

def solve_for_x(equation: str) -> Union[float, None]:
    """
    Solve simple linear equation in one variable (x).
    Example inputs: "2*x + 3 = 11", "3*x-6=0", "5x+2=12"
    Returns a float (solution for x) or None if not solvable with this helper.
    """
    try:
        # Replace common implicit multiplication like '5x' -> '5*x' for sympy
        eq = equation.replace(" ", "").replace("X", "x").replace("X", "x")
        # insert '*' between digit and x (e.g., 5x -> 5*x)
        import re
        eq = re.sub(r"(?P<num>\d)(?P<var>x\b)", r"\g<num>*\g<var>", eq)
        left, right = eq.split("=")
        x = sp.symbols('x')
        sol = sp.solve(sp.Eq(sp.sympify(left), sp.sympify(right)), x)
        if not sol:
            return None
        # sol can be list with symbolic results; handle first
        val = sol[0]
        return float(val.evalf())
    except Exception:
        return None

def grade_answer(expected_expr: str, user_answer: str, tolerance: float = 1e-6) -> Dict[str, Any]:
    """
    Compare the user's numeric answer to the expected expression.
    expected_expr: equation string like "2*x+3=11" or direct numeric like "4"
    user_answer: string provided by user like "4", "4.0"
    Returns dict: {"correct": bool, "expected": float|None, "user": float|None, "explanation": str}
    """
    result = {"correct": False, "expected": None, "user": None, "explanation": ""}

    # Try to find the expected numeric answer:
    expected_val = None
    # If expected_expr looks like an equation, try to solve for x
    if "=" in expected_expr:
        expected_val = solve_for_x(expected_expr)
    else:
        try:
            expected_val = float(sp.sympify(expected_expr))
        except Exception:
            expected_val = None

    # Try to parse user answer as a number
    user_val = None
    try:
        # remove spaces and common text like 'x=', just in case
        ua = user_answer.strip().replace(" ", "")
        if ua.lower().startswith("x="):
            ua = ua.split("=", 1)[1]
        user_val = float(sp.sympify(ua))
    except Exception:
        user_val = None

    result["expected"] = expected_val
    result["user"] = user_val

    if expected_val is None:
        result["explanation"] = "Unable to compute expected answer from the expected expression."
        return result

    if user_val is None:
        result["explanation"] = "Unable to parse user's numeric answer."
        return result

    # compare with tolerance
    if abs(user_val - expected_val) <= tolerance:
        result["correct"] = True
        result["explanation"] = f"Correct — expected {expected_val}, got {user_val}."
    else:
        result["explanation"] = f"Incorrect — expected {expected_val}, got {user_val}."

    return result
