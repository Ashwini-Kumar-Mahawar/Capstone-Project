# 🧠 Adaptive Learning Coach

### Personalized AI Tutoring powered by Multi-Agents + Memory + Auto-Evaluation

The **Adaptive Learning Coach** is an AI-driven educational platform that builds a personalized learning path for every student.
It continuously adapts based on performance using a **Lesson → Quiz → Feedback → Evaluation loop** and maintains long-term memory to track mastery.

---

## 🚀 Features

| Component             | Purpose                                                 |
| --------------------- | ------------------------------------------------------- |
| **Assessment Agent**  | Diagnoses the learner’s skill level                     |
| **Lesson Agent**      | Generates structured micro-lessons with worked examples |
| **Quiz Agent**        | Builds targeted practice questions from lessons         |
| **Feedback Agent**    | Provides step-by-step feedback for mistakes             |
| **Evaluation Engine** | Tracks progress and topic mastery                       |
| **Persistent Memory** | Stores preferences, performance, and lessons history    |

---

## 🧩 Learning Loop (Core Innovation)

```
Diagnostic Assessment
        ↓
Lesson Generation (personalized)
        ↓
Quiz Creation (topic-focused)
        ↓
Automated Grading
        ↓
Feedback & Reinforcement
        ↓
Evaluation & Memory Update
        ↓
Next Lesson (based on mastery)
```

The system continues cycling until mastery is reached.

---

## 📂 Project Structure

```
adaptive-coach/
│
├── streamlit_app/           # Full UI interface
├── notebooks/
│   └── demo.ipynb           # Interactive Demo (official submission)
│
├── agents/
│   ├── assessment_agent.py
│   ├── lesson_agent.py
│   ├── quiz_agent.py
│   └── feedback_agent.py
│
├── tools/
│   ├── persistence.py       # Lightweight database + memory store
│   └── grading.py           # Expression parsing + numeric grading
│
├── eval/
│   └── report.py            # Evaluation and mastery score logic
│
└── api.py                   # Unified callable interface for all agents
```

---

## 🛠 Tech Stack

| Category                | Tools                         |
| ----------------------- | ----------------------------- |
| UI                      | Streamlit                     |
| Core Language           | Python                        |
| Math Engine             | SymPy                         |
| Tracing & Observability | OpenTelemetry                 |
| Data Storage            | SQLite (local lightweight DB) |

---

## ▶ How to Run Locally

### Clone the repository

```bash
git clone https://github.com/your_username/adaptive-learning-coach.git
cd adaptive-learning-coach
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the Streamlit app

```bash
streamlit run streamlit_app/app.py
```

### Or run the official notebook demo

```bash
notebooks/demo.ipynb
```

No API keys or cloud services required.

---

## 📌 Recommended Workflow for Reviewers

| Mode                | Where to Test          | Notes                                                  |
| ------------------- | ---------------------- | ------------------------------------------------------ |
| Full UI + Memory    | `streamlit_app/app.py` | Best demonstration                                     |
| Quick Agent Testing | Python REPL            | `from api import run_assessment, generate_lesson, ...` |
| Official Demo       | `notebooks/demo.ipynb` | Used for project submission                            |

---

## 🧪 Sample Test Scenario

| Step | Action                                   |
| ---- | ---------------------------------------- |
| 1    | Submit answers to assessment             |
| 2    | Generate personalized lesson             |
| 3    | Generate quiz                            |
| 4    | Submit quiz answers                      |
| 5    | Receive feedback                         |
| 6    | View evaluation report                   |
| 7    | Run again to observe mastery improvement |

Every cycle updates memory and adjusts difficulty dynamically.

---

## 📉 Visualization and Metrics

The platform tracks and displays:

* Score history
* Topic proficiency
* Attempt history
* Memory-based learning curve

---

## 🧭 Future Enhancements

| Category   | Upcoming Upgrade                           |
| ---------- | ------------------------------------------ |
| AI Models  | Gemini / GPT-powered Teaching Agent        |
| UI         | Chat-based tutoring mode                   |
| Curriculum | CS, ML, Web Dev, DSA tracks                |
| Routing    | Automatic topic classifier to select agent |
| Streaming  | Real-time token streaming responses        |

---

## 👤 Author

**Capstone Project — Adaptive Learning Coach**
Developed by: Ashwini Kumar Mahawar

If you like this project, ⭐ star the repository.

---

## 📜 License

This project is released under the **MIT License**.


