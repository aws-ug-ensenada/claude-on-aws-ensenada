"""Level 8 — entry point for Amazon Bedrock AgentCore Runtime.

Runs the same assistant (solo or agency, from config.yaml) as a cloud service.
Locally:  python app.py   then   curl -X POST localhost:8080/invocations -d '{"prompt": "hola"}'
"""

import os

import tools.todo
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from core import build_agency, build_solo, load_config

# Nobody is at a keyboard in the cloud to approve deletions, so the answer is always no.
tools.todo.ask_human = lambda question: False

app = BedrockAgentCoreApp()
# LUNA_PRESET picks a preset; LUNA_MODE (solo or agency) overrides config.yaml's mode.
CFG = load_config(os.environ.get("LUNA_PRESET"), [f"mode={m}"] if (m := os.environ.get("LUNA_MODE")) else [])


@app.entrypoint
def invoke(payload: dict, context) -> dict:
    """AgentCore Runtime calls this for every request (level 8): build the configured agent for the session and return its answer."""
    session_id = getattr(context, "session_id", None) or "default-session"
    if CFG.get("mode", "solo") == "solo":
        agent = build_solo(CFG, session_id=session_id, quiet=True)
    else:
        agent, _ = build_agency(CFG, session_id=session_id, quiet=True)
    return {"answer": str(agent(payload.get("prompt", ""))).strip()}


if __name__ == "__main__":
    app.run()
