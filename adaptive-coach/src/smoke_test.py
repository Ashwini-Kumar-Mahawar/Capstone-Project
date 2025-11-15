# src/smoke_test.py
from observability.logging_setup import get_logger
from tools.persistence import init_db, save_memory, load_memory

logger = get_logger("smoke_test")

def run():
    conn = init_db()
    user_id = "student_001"

    logger.info("intent_before_action", extra={"extra": {"trace_id": "trace-smoke-1", "action": "init_memory"}})

    memory = {
        "name": "Asha",
        "topic_mastery": {"linear_equations": 30},
        "preferred_explanation": "concise"
    }
    save_memory(conn, user_id, memory)
    logger.info("memory_saved", extra={"extra": {"user_id": user_id}})

    read_back = load_memory(conn, user_id)
    logger.info("memory_loaded", extra={"extra": {"user_id": user_id, "memory": read_back}})

    print("Smoke test done. Memory read back:", read_back)

if __name__ == "__main__":
    run()
