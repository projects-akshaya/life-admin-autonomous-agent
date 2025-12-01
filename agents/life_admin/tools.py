import datetime
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Literal


@dataclass
class Task:
    id: int
    raw: str
    clean: str
    category: str
    urgency: Literal["high", "medium", "low"]
    reason: str
    detected_due_phrase: Optional[str] = None


# Text splitting
def _split_into_candidates(text: str) -> List[str]:
    """
    Split a messy life-admin dump into candidate task sentences.
    Deterministic, no LLM.
    """
    tmp = text.replace("•", "\n").replace("·", "\n")
    tmp = tmp.replace(" and ", ". ")
    raw_parts = re.split(r"[\n;\.]", tmp)
    candidates = []
    for part in raw_parts:
        c = part.strip("-• \t").strip()
        if len(c) >= 3:
            candidates.append(c)
    return candidates


# Category & due detection

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "money/finance": [
        "tax", "invoice", "insurance", "health insurance", "krankenkasse",
        "bank", "konto", "credit", "loan", "bill", "rent", "miete", "pay",
    ],
    "immigration/admin": [
        "visa", "residence", "aufenthalt", "blue card", "pr", "permanent",
        "einbürgerung", "bürgeramt", "agent", "agentur für arbeit",
        "appointment letter", "termin", "registration", "anmeldung",
    ],
    "health": [
        "doctor", "arzt", "dentist", "dermatologist", "therapy", "hospital",
        "clinic", "blood test", "medication", "gym", "workout", "physio",
    ],
    "home/chores": [
        "clean", "laundry", "dish", "fridge", "kitchen", "cupboard",
        "vacuum", "groceries", "shopping", "trash", "garbage", "repair",
    ],
    "work/career": [
        "cv", "resume", "linkedin", "job", "interview", "presentation",
        "slides", "report", "deadline", "manager", "project", "task",
        "coding", "ml", "ai", "ticket", "jira",
    ],
    "relationships/social": [
        "birthday", "call", "message", "text", "meet", "dinner", "date",
        "parents", "mom", "dad", "family", "friend", "partner",
    ],
}

DUE_KEYWORDS = {
    "today": "today",
    "tonight": "today",
    "tomorrow": "tomorrow",
    "this week": "this week",
    "next week": "next week",
    "this weekend": "this weekend",
    "next weekend": "next weekend",
}


def _guess_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return cat
    return "other"


def _detect_due_phrase(text: str) -> Optional[str]:
    t = text.lower()
    for phrase in DUE_KEYWORDS.keys():
        if phrase in t:
            return phrase
    if re.search(r"\b\d{1,2}[./-]\d{1,2}\b", t):
        return "specific date mentioned"
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", t):
        return "specific date mentioned"
    return None


def _guess_urgency(due_phrase: Optional[str], text: str) -> (str, str):
    t = text.lower()
    if "urgent" in t or "asap" in t:
        return "high", "Marked as urgent/ASAP by you."

    if due_phrase in ("today", "tonight", "tomorrow", "this week", "this weekend"):
        return "high", f"Due phrase detected: '{due_phrase}'."

    if due_phrase in ("next week", "next weekend", "specific date mentioned"):
        return "medium", f"Upcoming due phrase: '{due_phrase}'."

    if any(w in t for w in ["visa", "insurance", "tax", "rent", "miete"]):
        return "medium", "Administrative/financial task with potential deadlines."

    return "low", "No clear due phrase or deadline indicators found."


# Tool 1: extract & classify

def extract_and_classify_tasks(raw_text: str) -> Dict[str, Any]:
    """
    Deterministic tool:
    - Extract candidate tasks from messy text
    - Guess category
    - Guess simple urgency (high/medium/low)
    Returns a JSON-serializable dict of tasks.
    """
    candidates = _split_into_candidates(raw_text)
    tasks: List[Task] = []

    for i, c in enumerate(candidates, start=1):
        due_phrase = _detect_due_phrase(c)
        urgency, reason = _guess_urgency(due_phrase, c)
        clean = c[0].upper() + c[1:] if c else c
        category = _guess_category(c)
        tasks.append(
            Task(
                id=i,
                raw=c,
                clean=clean,
                category=category,
                urgency=urgency,  # type: ignore[arg-type]
                reason=reason,
                detected_due_phrase=due_phrase,
            )
        )

    return {
        "tasks": [asdict(t) for t in tasks],
        "summary": {
            "total_tasks": len(tasks),
            "high_urgency": sum(1 for t in tasks if t.urgency == "high"),
            "medium_urgency": sum(1 for t in tasks if t.urgency == "medium"),
            "low_urgency": sum(1 for t in tasks if t.urgency == "low"),
        },
    }


def build_7_day_plan(task_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic tool:
    - Takes output of extract_and_classify_tasks (dict with tasks list)
    - Spreads tasks across the next 7 calendar days
      in a balanced way, without crowding one day
      if other days in the urgency range are free.
    """
    today = datetime.date.today()
    tasks_data = task_payload.get("tasks", [])

    # Rebuild Task objects
    tasks: List[Task] = [
        Task(
            id=t["id"],
            raw=t["raw"],
            clean=t["clean"],
            category=t["category"],
            urgency=t["urgency"],
            reason=t["reason"],
            detected_due_phrase=t.get("detected_due_phrase"),
        )
        for t in tasks_data
    ]

    # Sort tasks by urgency (high → medium → low) then id
    urgency_order = {"high": 0, "medium": 1, "low": 2}
    tasks_sorted = sorted(
        tasks,
        key=lambda t: (
            urgency_order.get(t.urgency, 2),
            t.id,
        ),
    )

    # Prepare 7 days
    days: List[Dict[str, Any]] = []
    for offset in range(7):
        d = today + datetime.timedelta(days=offset)
        label = "Today" if offset == 0 else ("Tomorrow" if offset == 1 else d.strftime("%A"))
        days.append({"date": d.isoformat(), "label": label, "tasks": []})

    max_tasks_per_day = 3  # keep any single day from being overloaded

    def candidate_indices_for(task: Task) -> List[int]:
        """Define which days are preferred for each urgency level."""
        if task.urgency == "high":
            # High: spread over first 4 days, but not only today
            return list(range(0, min(4, len(days))))
        elif task.urgency == "medium":
            # Medium: focus on days 2–6 (avoid stuffing today)
            return list(range(1, len(days)))
        else:
            # Low: prefer later days in the week
            return list(range(2, len(days)))

    for t in tasks_sorted:
        candidates = candidate_indices_for(t)

        # Among candidates, pick the day with the fewest tasks so far
        # but also respect max_tasks_per_day.
        # First, filter by days that are not full
        not_full = [i for i in candidates if len(days[i]["tasks"]) < max_tasks_per_day]

        if not_full:
            # choose the least loaded of the not-full candidates
            best_idx = min(not_full, key=lambda i: len(days[i]["tasks"]))
        else:
            # if all candidate days are full, choose globally least loaded day
            best_idx = min(range(len(days)), key=lambda i: len(days[i]["tasks"]))

        days[best_idx]["tasks"].append(asdict(t))

    return {
        "start_date": today.isoformat(),
        "end_date": (today + datetime.timedelta(days=6)).isoformat(),
        "days": days,
    }
