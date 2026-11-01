"""Level 3 — create an Amazon Bedrock AgentCore Memory and switch it on for the assistant.

  python setup/create_memory.py      # takes 2–3 minutes

The memory learns the user's preferences from conversations (e.g. "I'm vegetarian")
and gives them back to the assistant in later sessions.
Cost: only when used — see docs/costs.md. No monthly fee for an empty memory.
Undo: python setup/cleanup.py
"""

from bedrock_agentcore.memory import MemoryClient

import _local


def main() -> None:
    local = _local.read()
    if (local.get("memory") or {}).get("id"):
        print(f'Already created: {local["memory"]["id"]}. Run setup/cleanup.py first to recreate.')
        return
    print("Creating memory (2–3 minutes)…")
    memory = MemoryClient(region_name=_local.REGION).create_memory_and_wait(
        name="luna_assistant",
        description="Personal assistant demo — AWS User Group Ensenada",
        # Must match the namespace core.memory_session() reads from.
        strategies=[{"userPreferenceMemoryStrategy": {"name": "preferences", "namespaces": ["/preferences/{actorId}"]}}],
        event_expiry_days=30,
    )
    local["memory"] = {"enabled": True, "id": memory["id"]}
    _local.write(local)
    print(f'✅ Memory {memory["id"]} created and enabled in config.local.yaml')


if __name__ == "__main__":
    main()
