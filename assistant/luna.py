"""Chat with your assistant in the terminal.

  python luna.py                          # solo assistant, as set in config.yaml
  python luna.py --no-tools               # plain chatbot: same brain, no hands
  python luna.py --mode agency            # a Director agent gives orders to specialists
  python luna.py --mode fleet             # same, over A2A (start: python fleet_server.py --all)
  python luna.py --preset student         # a ready-made profile from presets/
  python luna.py --preset my-business --check   # check a preset you wrote, without calling AWS or Claude
  python luna.py --set assistant.personality=funny --set model.id=global.anthropic.claude-sonnet-4-6
  python luna.py --ask "What should I wear today?"   # one question, then exit
"""

import argparse
import os
import uuid

from strands.types.exceptions import MaxTokensReachedException

from core import active_agents, build_agency, build_solo, cost, load_config, usage_of

EXIT_WORDS = {"", "exit", "quit", "salir", "adios", "adiós"}


def main() -> None:
    """The terminal chat: build the solo agent or the agency from config, then answer questions until the user says exit."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--preset", help="profile from presets/ (student, professional, family)")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override any config value")
    parser.add_argument("--mode", choices=["solo", "agency", "fleet"], help="override config mode")
    parser.add_argument("--no-tools", action="store_true", help="solo mode without tools (plain chatbot)")
    parser.add_argument("--ask", help="ask one question and exit")
    parser.add_argument("--check", action="store_true", help="check the preset and config (no AWS, no Claude) and exit")
    args = parser.parse_args()

    if args.check:
        import check

        raise SystemExit(check.run(args.preset, args.set))
    cfg = load_config(args.preset, args.set)
    mode = args.mode or cfg.get("mode", "solo")
    session_id = uuid.uuid4().hex

    if mode == "solo":
        agent = build_solo(cfg, use_tools=not args.no_tools, session_id=session_id)
        billed = [("assistant", agent, cfg["model"]["id"])]
    else:
        agent, members = build_agency(cfg, session_id=session_id, remote=mode == "fleet")
        billed = [("director", agent, cfg["agency"]["director"].get("model") or cfg["model"]["id"])]
        # Local specialists bill in this process; in fleet mode they bill on their own servers, so only the Director is counted.
        if mode == "agency":
            billed += [(s["name"], members[s["name"]], s.get("model") or cfg["model"]["id"]) for s in active_agents(cfg)]

    print_banner(cfg, mode, args.no_tools)
    session_total = 0.0
    questions = [args.ask] if args.ask else None
    while True:
        question = questions.pop(0) if questions else (None if args.ask else ask())
        if question is None or question.strip().lower() in EXIT_WORDS:
            break
        # Token counts before the question, so the cost line shows only this answer's usage.
        before = {label: usage_of(a) for label, a, _ in billed}
        try:
            result = agent(question)
        except MaxTokensReachedException:
            # The answer outgrew model.max_tokens: keep the session, say why, and let them ask for less.
            print(f"\n(answer cut off at model.max_tokens = {cfg['model']['max_tokens']}: ask for a shorter answer, or raise it)\n")
            continue
        if all(usage_of(a) == before[label] for label, a, _ in billed):
            print(str(result).strip())  # nothing was streamed: e.g. the guardrail stopped it before Claude
        print()
        if cfg.get("show_cost"):
            session_total += print_cost(cfg, billed, before, session_total, fleet=mode == "fleet")


def ask() -> str | None:
    """Read one question from the terminal; None on Ctrl-D or Ctrl-C, which ends the chat."""
    try:
        return input("\nyou › ")
    except (EOFError, KeyboardInterrupt):
        return None


def print_banner(cfg: dict, mode: str, no_tools: bool) -> None:
    """Print the summary at the top of the chat: mode, model, tools, and which levels (guardrail, memory, RAG, MCP) are on."""
    a, m = cfg["assistant"], cfg["model"]
    extras = [name for name in ("guardrail", "memory", "knowledge_base") if (cfg.get(name) or {}).get("enabled")]
    if "guardrail" in extras and m.get("provider", "bedrock") != "bedrock":
        extras[extras.index("guardrail")] = "guardrail (your input, via ApplyGuardrail)"  # see core.input_guardrail
    extras += [f"mcp:{n}" for n, s in (cfg.get("mcp_servers") or {}).items() if s.get("enabled")]
    if mode == "solo":
        team = "none (plain chatbot)" if no_tools else ", ".join(cfg["tools"])
        print(f"\n🌙 {a['name']} · solo · {m['provider']}:{m['id']} · tools: {team}")
    else:
        team = ", ".join(s["name"] for s in active_agents(cfg))
        print(f"\n🌙 {a['name']} · {mode} · director + {team}")
    if extras:
        print(f"   extras: {', '.join(extras)}")
    print("   (type 'exit' to quit)")


def print_cost(cfg, billed, before, session_total, fleet) -> float:
    """Print what this answer cost per agent (tokens and dollars) and the session total; returns this answer's cost."""
    turn, parts = 0.0, []
    for label, agent, model_id in billed:
        (in0, out0), (in1, out1) = before[label], usage_of(agent)
        if in1 - in0 or out1 - out0:
            c = cost(cfg, model_id, in1 - in0, out1 - out0)
            turn += c
            parts.append(f"{label} {in1 - in0:,}→{out1 - out0:,} tok ${c:.4f}")
    note = "  (specialists bill on their own servers)" if fleet else ""
    print(f"💲 {' · '.join(parts)}  |  this answer ${turn:.4f} · session ${session_total + turn:.4f}{note}")
    return turn


def explain(error: Exception) -> str | None:
    """A one-line reason and fix for the failures that happen on a bad day: credentials, model access, network."""
    name, text = type(error).__name__, str(error)
    if name == "AuthenticationError" or "UnrecognizedClientException" in text or "ExpiredToken" in text:
        return "Credentials were refused. Check ANTHROPIC_API_KEY, or AWS_PROFILE and `aws sso login`."
    if "AccessDenied" in text or "PermissionDenied" in name:
        return "This account or key is not allowed to do that. Check model access (docs/bedrock-access.md)."
    if "ValidationException" in text and "model identifier" in text:
        return "Unknown model id. Check model.id in config.local.yaml."
    if "Throttl" in text or "RateLimit" in name or "quota" in text.lower():
        return "Rate limit or quota reached. Wait a minute, or switch model (Plan B: Bedrock Claude 4.x)."
    if name in ("EndpointConnectionError", "ConnectError", "APIConnectionError", "ConnectTimeout", "ProxyConnectionError", "ReadTimeoutError") or "Could not connect" in text or "Failed to connect" in text:
        return "No network to the model. Check the Wi-Fi (or the phone hotspot), or play the recorded clip."
    if "credit balance" in text.lower():
        return "The Claude API account is out of credit. Add credit in the Console, or switch to Bedrock."
    return None


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - last line of defence: say what to do, not just a stack trace
        reason = explain(error)
        if reason is None or os.environ.get("LUNA_DEBUG"):
            raise
        print(f"\n❌ {reason}\n   ({type(error).__name__}; set LUNA_DEBUG=1 for the full trace)")
        raise SystemExit(1)
