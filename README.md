# 📘 Adaptive Learning Coach (Multi-Agent Personalized Tutoring System)

This project is built for the **Google DeepLearning.ai — Agentic AI Engineering Challenge**, showcasing a **multi-agent learning system** that adapts to students using **memory, evaluation, and continuous feedback loops**.

The app functions as an **AI tutor for mathematics (linear equations)**, powered by **sequential and loop agents** that assess performance, generate lessons, deliver quizzes, and provide corrective feedback.

---

## 🚀 Demo

Run the interactive Streamlit interface:

```bash
streamlit run streamlit_app/app.py
```

Or explore the demonstration notebook:

```
notebooks/demo.ipynb
```

---

## 🧠 System Architecture

```
 Assessment Agent → Lesson Agent → Quiz Agent → Feedback Agent
                         ↑              ↓
                    Memory Bank ← Mastery Tracking
```

The **Learning Loop tab** automates this process so the student stays in a continuous improvement cycle.

---

## ✨ Key Agentic Features (Rubric-Aligned)

This submission implements more than the minimum **3 required agentic concepts**.

| Feature Category                     | How it is implemented                                                           |
| ------------------------------------ | ------------------------------------------------------------------------------- |
| **Multi-Agent System**               | 4 autonomous agents: Assessment Agent, Lesson Agent, Quiz Agent, Feedback Agent |
| **Sequential Agents**                | Assessment → Lesson → Quiz → Feedback pipeline                                  |
| **Loop Agent**                       | Continuous "Lesson → Quiz → Feedback → Next Lesson" cycle in the Streamlit UI   |
| **Sessions & Memory**                | SQLite memory stores mastery, quiz history, lessons, preferences                |
| **Long-Term Memory**                 | Topic mastery improves after every graded quiz                                  |
| **Observability: Logging & Tracing** | Implemented through OpenTelemetry logs and spans                                |
| **Agent Evaluation**                 | `evaluation_report()` generates mastery summaries and reports                   |
| **Agent Deployment**                 | Exposed through a full Streamlit frontend                                       |

⚠️ LLM tool integrations (Gemini API, OpenAPI tools, MCP protocol) were intentionally excluded due to submission deadline constraints.

---

## 📂 Project Structure

```
adaptive-coach/
│
├── agents/
│   ├── assessment_agent.py
│   ├── lesson_agent.py
│   ├── quiz_agent.py
│   └── feedback_agent.py
│
├── memory/
│   ├── db.py
│   ├── memory.py
│   └── evaluation.py
│
├── streamlit_app/
│   └── app.py
│
├── notebooks/
│   └── demo.ipynb
│
├── api.py
├── requirements.txt
└── README.md
```

---

## 🧩 How the Agents Work

| Agent                | Responsibilities                                             |
| -------------------- | ------------------------------------------------------------ |
| **Assessment Agent** | Diagnoses initial skill level using a short problem set      |
| **Lesson Agent**     | Designs a micro-lesson with worked example and focus areas   |
| **Quiz Agent**       | Generates practice questions and grades them                 |
| **Feedback Agent**   | Explains mistakes step-by-step using deterministic reasoning |

---

## 🔄 Adaptive Learning Loop

The **Learning Loop tab** automates student progression:

1. (Optional) Assessment
2. Lesson generation
3. Quiz creation
4. Quiz grading
5. Feedback & mastery update
6. Loop continues with the next lesson

This forms a **personalized closed-loop learning system**.

---

## 📊 Memory & Progress Tracking

Memory is stored per student and includes:

| Data Stored   | Purpose                         |
| ------------- | ------------------------------- |
| last_lesson   | Resume where learning paused    |
| last_quiz     | Recover incomplete quiz         |
| quiz history  | Skill improvement tracking      |
| topic_mastery | Adaptive difficulty progression |
| preferences   | Personalized teaching style     |

This enables **persistent sessions across multiple logins**.

---

## 🛠 Installation

```bash
git clone <repo>
cd adaptive-coach
pip install -r requirements.txt
```

Start the UI:

```bash
streamlit run streamlit_app/app.py
```

---

## 📌 Requirements

```
streamlit
sympy
rich
opentelemetry-api
opentelemetry-sdk
python-dotenv
jupyter
plotly
requests
pandas
```

---

## 🧪 Testing (quick check)

Simply start a session in the UI and follow:

```
Assessment → Lesson → Quiz → Feedback → Report
```

Or use the **Learning Loop** to automate the cycle.

---

## 🙌 Acknowledgment

This project was created for the **5-Day AI Agents Intensive Course with Google × Kaggle**, demonstrating:

* **multi-agent orchestration**
* **sequential and loop agent control**
* **persistent memory & mastery adaptation**
* **observability via logging and tracing**
* **agent evaluation through reports**

---
