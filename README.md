# NEXUS-PM — The Cognitive Intelligence Layer for Project Management

NEXUS-PM is an **Adaptive AI Project Manager** that transcends traditional scheduling. By combining **Persistent Behavioral Memory (via Hindsight)**, a **Unified 6-Model ML Suite**, and **Real-time Proactive Intelligence**, NEXUS-PM evolves alongside your team to minimize risk and maximize delivery velocity.

![NEXUS-PM Dashboard Overview](file:///C:/Users/Rakshan25/.gemini/antigravity/brain/c652b5aa-182e-4633-a6d4-29a9b3d75f70/nexus_dashboard_1774021517172.png)
*Strategic Intelligence Dashboard showcasing real-time project health and AI-driven briefings.*

---

## 🧠 Cognitive Architecture: The ACTS Pipeline

NEXUS-PM operates on the **ACTS (Assessment, Correlation, Thought, Synthesis)** pipeline, ensuring every decision is backed by historical performance and predictive models.

1.  **Perceive**: Ingests new tasks, meeting transcripts, and project constraints.
2.  **Recall**: Queries **Hindsight Cloud** to retrieve past team outcomes, skill drifts, and delay patterns.
3.  **Reason**: Executes the **Unified 6-Model ML Suite** (XGBoost/SGD) to score risk, capacity, and affinity.
4.  **Adapt**: Automatically adjusts its assignment strategy weights based on real-time feedback loops.
5.  **Learn**: Persists final outcomes back to memory, completing the cognitive cycle.

---

## 🛠️ Unified ML Intelligence Suite

NEXUS-PM doesn't just guess; it calculates. Our multi-model engine runs on parallel tracks:

*   **Risk Predictor (XGBoost + SGD)**: Dynamic risk scoring with online learning capabilities.
*   **Skill Affinity (Cosine Similarity)**: Vector-based matching of developer skills to task requirements.
*   **Workload Forecaster (Regression)**: Predictive capacity monitoring to prevent burnout.
*   **Delay Classifier (Naive Bayes)**: Forensic analysis of past bottlenecks (Technical, Process, or External).
*   **Sprint Health (Random Forest)**: Probability-based success forecasting for every active sprint.
*   **Anomaly Detector (Isolation Forest)**: Identifies statistical outliers in team performance for early intervention.

---

## 🚀 Proactive Intelligence & SSE

Stay ahead of bottlenecks with **Build 18-35: Proactive Nudge**. NEXUS-PM monitors your project in the background and pushes real-time alerts via **Server-Sent Events (SSE)**.

*   **Morning Briefing**: Start your day with an AI-synthesized summary of critical watch-items.
*   **Proactive Nudges**: Immediate "NudgeToasts" for overdue tasks, high-risk anomalies, or team overloads.
*   **Automated Governance**: Generates comprehensive PDF/HTML performance reports with Hindsight-backed narratives.

![Strategic Analytics](file:///C:/Users/Rakshan25/.gemini/antigravity/brain/c652b5aa-182e-4633-a6d4-29a9b3d75f70/analytics_page_1774280466477.png)
*Advanced Analytics view showing memory-event correlations and strategy drift.*

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| **Intelligence** | Python 3.11+, XGBoost, Scikit-Learn, Groq LLM (Llama 3+) |
| **Memory** | Hindsight Cloud (Vectorized Memory Banks) |
| **API** | FastAPI, SQLAlchemy 2.0, APScheduler, SSE (Server-Sent Events) |
| **Frontend** | React 18, Vite, Tailwind CSS, Framer Motion, Recharts |
| **Database** | SQLite (for local state) / Hindsight (for persistent context) |

---

## 🏁 Quick Start

### 1. Environment Configuration
Clone the repository and configure your intelligence keys:
```bash
cp .env.example .env
# Required: HINDSIGHT_API_KEY, GROQ_API_KEY
```

### 2. Backend Initialization
Install dependencies and initialize the ML suite:
```bash
pip install -r requirements.txt
python -m backend.ml.train --mode synthetic  # Train initial 6-model suite
python backend/main.py                       # Launch NEXUS-PM API (Port 8000)
```

### 3. Frontend Execution
```bash
cd frontend
npm install
npm run dev                                  # Launch Dashboard (Port 5173)
```

### 4. Automated Demo
Run the cognitive audit script to see NEXUS in action:
```bash
python scripts/demo_runner.py  # Performs a full project lifecycle audit
```

---

*“The best AI tool is one that your non-technical teammates can understand without a guide.” — Built for the NEXT generation of high-velocity teams.*

