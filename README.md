# Brain-dump to game plan Agent (Google ADK + Gemini)

A fully deterministic, reliable **Life-Admin Concierge Agent** built using the **Google Agent Development Kit (ADK)** and **Gemini**.

You paste your messy, overwhelming “life dump” — visa renewal, bills, chores, job applications, personal reminders — and the agent turns it into:

- A **structured set of extracted tasks**
- **Categories & urgency scoring**
- A **balanced 7-day action plan** (no overcrowding)
- A **friendly, empathetic explanation**

This project demonstrates a practical, production-quality agent built with ADK tools + Gemini reasoning.

---

## ✨ Features

### 🔹 Single-Agent Architecture (root_agent)
The project uses **one main agent** (`root_agent`) that orchestrates tool usage:

- Calls the task extraction tool  
- Calls the 7-day planning tool  
- Generates the final human-readable plan & coaching  

This keeps behavior predictable, testable, and competition-aligned.

---

### 🔹 Function Tools for Customisation of logic

#### `extract_and_classify_tasks(raw_text: str) → dict`
- Splits messy text into candidate tasks  
- Classifies them (finance, immigration, chores, career, health, social, other)  
- Detects urgency from due phrases  
- Returns structured JSON with explanations  
- Fully deterministic Python logic — no LLM inside tools  

#### `build_7_day_plan(task_payload: dict) → dict`
- Balances tasks across the week  
- Prevents overcrowding  
- Uses urgency-based permitted scheduling ranges  
- Produces a structured, predictable weekly schedule  

---

### 🔹 Empathetic LLM Layer
After tools complete, Gemini generates:

- A readable weekly plan  
- Clear urgency grouping  
- Encouraging motivation & action rules  

---

### 🔹 CLI Interface (Local Use)
Run:

```bash
python app.py
```

Paste your tasks → get a clean weekly plan.

---

### 🔹 Clean Output (No Metadata)
The final response uses `run_async()` and returns only the human-readable output.

---

### 🔹 Future Improvements Deployment Ready
- `main.py` → FastAPI wrapper for hosting  
- Compatible with Render, Railway, Cloud Run  
- Includes optional Cloud Run Dockerfile + Agent Engine config  

---

## 🧠 Architecture Overview

```
User Input
    │
    ▼
root_agent (LLM)
    │
    ├── extract_and_classify_tasks (deterministic)
    │
    ├── build_7_day_plan (deterministic)
    │
    ▼
Gemini: final structured + empathetic response
```

### Key Principles

- Tools perform deterministic logic  
- LLM handles language, empathy, structuring  
- Agent orchestrates tool calls  
- Clean separation of concerns  

---

## 📂 Project Structure

```
life-admin-agent/
│
├── agents/
│   ├── __init__.py
│   └── life_admin/
│       ├── agent.py
│       └── tools.py
│
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

---

## 🚀 Running Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add `.env`

```
GOOGLE_API_KEY=your_key_here
```

### 3. Run

```bash
python app.py
```

Paste:

```
Extend my visa, clean the fridge, update my CV, apply for jobs, call mom, pay rent...
```

---

## 🧪 Competition Alignment

This project aligns strongly with the **Concierge Agent** track:

- Real-world problem (life-admin overload)
- Deterministic tool-based approach
- Clear value and practical utility
- Strong documentation and architecture clarity

---

## 📘 Documentation Included

- Problem statement  
- Solution explanation  
- Architecture design  
- Project value and outcomes
- Clean, modular code  

---
