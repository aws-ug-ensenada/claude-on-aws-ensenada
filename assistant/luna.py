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
import uuid

from strands.types.exceptions import MaxTokensReachedException

from core import active_agents, build_agency, build_solo, cost, load_config, usage_of

EXIT_WORDS = {"", "exit", "quit", "salir", "adios", "adiós"}


def main() -> None:
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
        if mode == "agency":
            billed += [(s["name"], members[s["name"]], s.get("model") or cfg["model"]["id"]) for s in active_agents(cfg)]

    print_banner(cfg, mode, args.no_tools)
    session_total = 0.0
    questions = [args.ask] if args.ask else None
    while True:
        question = questions.pop(0) if questions else (None if args.ask else ask())
        if question is None or question.strip().lower() in EXIT_WORDS:
            break
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
    try:
        return input("\nyou › ")
    except (EOFError, KeyboardInterrupt):
        return None


def print_banner(cfg: dict, mode: str, no_tools: bool) -> None:
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


if __name__ == "__main__":
    main()
