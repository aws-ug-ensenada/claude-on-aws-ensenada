"""A to-do list saved in a local file (data/todo.json). Deleting asks a human first."""

import json
import os
import pathlib

from strands import tool

# LUNA_DATA_DIR moves it somewhere writable, e.g. /tmp/luna on AgentCore Runtime.
FILE = pathlib.Path(os.environ.get("LUNA_DATA_DIR") or pathlib.Path(__file__).parent.parent / "data") / "todo.json"


def ask_human(question: str) -> bool:
    """Human-in-the-loop check. The cloud runtime replaces this with a function that says no."""
    return input(f"\n⚠️  {question} [y/N] ").strip().lower() in ("y", "yes", "s", "si", "sí")


def _load() -> list[dict]:
    """All tasks from the to-do file, or [] when it does not exist yet."""
    return json.loads(FILE.read_text()) if FILE.exists() else []


def _save(tasks: list[dict]) -> None:
    """Write the tasks back to the to-do file, creating its folder if needed."""
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False))


@tool
def add_task(task: str, due: str = "") -> dict:
    """Add a task to the to-do list.

    Args:
        task: What needs to be done.
        due: Optional due date or day, e.g. "2026-11-07" or "Friday".
    """
    tasks = _load()
    tasks.append({"task": task, "due": due, "done": False})
    _save(tasks)
    return {"added": task, "number": len(tasks)}


@tool
def list_tasks(include_done: bool = False) -> list[dict]:
    """List the tasks on the to-do list, numbered.

    Args:
        include_done: Also show tasks already completed.
    """
    return [{"number": i, **t} for i, t in enumerate(_load(), 1) if include_done or not t["done"]]


@tool
def complete_task(number: int) -> dict:
    """Mark a task as done.

    Args:
        number: The task number from list_tasks.
    """
    tasks = _load()
    if not 1 <= number <= len(tasks):
        return {"error": f"No task number {number}"}
    tasks[number - 1]["done"] = True
    _save(tasks)
    return {"completed": tasks[number - 1]["task"]}


@tool
def delete_task(number: int) -> dict:
    """Delete a task permanently. A human must approve it first.

    Args:
        number: The task number from list_tasks.
    """
    tasks = _load()
    if not 1 <= number <= len(tasks):
        return {"error": f"No task number {number}"}
    if not ask_human(f'Delete task "{tasks[number - 1]["task"]}"?'):
        return {"deleted": False, "reason": "The user did not approve."}
    removed = tasks.pop(number - 1)
    _save(tasks)
    return {"deleted": removed["task"]}


TOOLS = [add_task, list_tasks, complete_task, delete_task]
