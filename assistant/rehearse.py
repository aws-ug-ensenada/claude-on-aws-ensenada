"""Rehearse the talk's demo: run every scene once, non-interactively, and check each answer.

  python rehearse.py               # every scene, in talk order
  python rehearse.py agent rag     # only these scenes
  python rehearse.py --list        # show the scenes

Each scene runs luna.py --ask (or agentcore invoke for the cloud scene) exactly as on stage, then
checks the output for what the audience should see. The to-do list goes to a scratch folder, so
your real list isn't touched; the briefing scene saves a report in business/winery/reports/ (git-ignored).
A full run costs about 15 cents and takes about 5 minutes.
Scenes whose setup is missing (no knowledge base, no agentcore CLI…) are skipped, not failed.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from core import load_config

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKED = "outside what I'm allowed to do"

# name, what it shows, luna.py arguments, question, pattern the output must match, pattern it must NOT match
SCENES = [
    ("chatbot", "Level 1: a plain chatbot can only guess",
     ["--no-tools"], "What should I wear today?", r".", r"Tool #"),
    ("agent", "Level 1: same brain plus hands: real weather, real rate, the to-do list",
     [], "What should I wear today, and how much is 85 dollars in pesos? Add 'buy sunscreen' to my list.",
     r"Tool #.*(?s:.*)MXN|MXN(?s:.*)Tool #", None),
    ("preset", "Make it yours: a preset changes name, personality and model",
     ["--preset", "family"], "Hola, ¿quién eres?", r".", None),
    ("agency", "Level 6: the Director gives orders to specialists",
     ["--mode", "agency"], "Plan my Saturday at the beach, budget 50 USD", r"📨(?s:.*)✅", None),
    ("guardrail", "Level 2: a denied topic is refused",
     [], "Should I buy bitcoin with my savings?", re.escape(BLOCKED), None),
    ("memory", "Level 3: it remembers you across sessions (and the guardrail lets that through)",
     [], "Suggest a dinner for tonight based on what you know about me.", r"(?i)vegetarian", re.escape(BLOCKED)),
    ("rag", "Level 5: answers from your own documents",
     [], "According to my lease, when is the rent due and how much is it?", r"9,?500(?s:.*)5|5(?s:.*)9,?500", None),
    ("mcp", "Level 4: many sources through MCP servers: the time, then a web page",
     ["--preset", "winery"], "What time is it in Los Angeles right now? Then read https://en.wikipedia.org/wiki/Valle_de_Guadalupe "
     "and give me two facts I can tell my US guests.", r"get_current_time(?s:.*)fetch", None),
    ("business", "Your business: your files (MCP) plus your documents (RAG), in one answer",
     ["--preset", "coffee-shop"], "What do I need to reorder this week, and from which supplier is espresso cheaper?",
     r"(?i)oat milk(?s:.*)Tostadores|Tostadores(?s:.*)(?i:oat milk)", None),
    ("clinic", "Any business: a third example, a clinic, with no change to the agent: files plus policies",
     ["--preset", "clinic"], "A patient cancelled tomorrow's cleaning with 5 hours' notice. Is there a fee? And which patient on Monday "
     "has an allergy the dentists should know about?", r"(?i)20 ?%(?s:.*)penicillin|penicillin(?s:.*)20 ?%", None),
    ("spanish", "Any language: the same clinic agent, asked in Spanish",
     ["--preset", "clinic"], "¿Cobran por cancelar una cita con 5 horas de aviso? ¿Cuánto cuesta una corona?",
     r"(?i)20 ?%(?s:.*)7,?500|7,?500(?s:.*)20 ?%", None),
    ("briefing", "Advanced: the agency prepares the owner's Monday briefing and saves it as a file",
     ["--preset", "winery", "--mode", "agency"], "Prepare my Monday briefing: will the patio be usable this weekend, how this "
     "weekend's sales compared with the weekend before, Saturday's reservations and allergies, what 100 dollars is in pesos "
     "for US guests, and which cork supplier to use. Save it as a report.", r"📨(?s:.*)office", None),
    ("cloud", "Level 8: the same agent on AgentCore Runtime, tools through the Gateway",
     None, "What should I wear today in Ensenada, and how much is 85 dollars in pesos?", r"(?i)MXN|pesos", re.escape(BLOCKED)),
]


def needs(name: str, cfg: dict) -> str | None:
    """Why a scene can't run on this machine, or None."""
    if name == "guardrail" and not (cfg.get("guardrail") or {}).get("enabled"):
        return "no guardrail (python setup/create_guardrail.py)"
    if name == "memory" and not (cfg.get("memory") or {}).get("enabled"):
        return "no memory (python setup/create_memory.py)"
    if name == "rag" and not (cfg.get("knowledge_base") or {}).get("enabled"):
        return "no knowledge base (python setup/create_knowledge_base.py)"
    if name in ("mcp", "business", "clinic", "spanish", "briefing") and not shutil.which("uvx"):
        return "uvx not installed"
    if name in ("business", "clinic", "spanish", "briefing") and not shutil.which("npx"):
        return "npx not installed (Node.js), needed by the files server"
    if name in ("business", "clinic", "spanish", "briefing") and not (cfg.get("knowledge_base") or {}).get("enabled"):
        return "no knowledge base (python setup/create_knowledge_base.py)"
    if name == "cloud" and not shutil.which("agentcore"):
        return "agentcore CLI not installed (npm install -g @aws/agentcore)"
    return None


def run(args: list[str] | None, question: str, env: dict) -> str:
    if args is None:  # the cloud scene
        cmd = ["agentcore", "invoke", "--runtime", "luna", "--payload", json.dumps({"prompt": question})]
        cwd = os.path.dirname(HERE)
    else:
        cmd = [sys.executable, "luna.py", *args, "--ask", question]
        cwd = HERE
    out = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=300)
    return out.stdout + out.stderr


def warn_stray_memory(cfg: dict) -> None:
    """Memory learns from every rehearsal; stray records can make the guardrail refuse later scenes."""
    if not (cfg.get("memory") or {}).get("enabled"):
        return
    try:
        sys.path.insert(0, str(Path(HERE) / "setup"))
        import clean_memory

        found = clean_memory.records(cfg)
    except Exception as err:  # a missing permission must not stop the rehearsal
        print(f"   (could not read the memory records: {type(err).__name__})")
        return
    if len(found) > 3:
        print(f"⚠️  The memory holds {len(found)} records; stray ones can make the guardrail refuse a scene.")
        print("   List them: python setup/clean_memory.py   Tidy: python setup/clean_memory.py --keep vegetarian --keep cold")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenes", nargs="*", help="scene names (default: all)")
    parser.add_argument("--list", action="store_true", help="list the scenes and exit")
    args = parser.parse_args()
    if args.list:
        for name, what, *_ in SCENES:
            print(f"  {name:10} {what}")
        return

    cfg = load_config()
    warn_stray_memory(cfg)
    env = {**os.environ, "LUNA_DATA_DIR": tempfile.mkdtemp(prefix="luna-rehearsal-"), "PYTHONUNBUFFERED": "1"}
    chosen = [s for s in SCENES if not args.scenes or s[0] in args.scenes]
    results = []
    for name, what, luna_args, question, must, must_not in chosen:
        print(f"\n━━ {name}: {what}\n   ❯ {question}")
        if reason := needs(name, cfg):
            print(f"   ⏭  skipped: {reason}")
            results.append((name, "skip", 0.0, ""))
            continue
        start = time.time()
        try:
            output = run(luna_args, question, env)
        except subprocess.TimeoutExpired:
            output = "TIMEOUT after 300 s"
        took = time.time() - start
        ok = bool(re.search(must, output)) and not (must_not and re.search(must_not, output))
        if name == "briefing":
            saved = [f for f in (Path(HERE) / "business" / "winery" / "reports").glob("*.md") if f.stat().st_mtime >= start]
            print(f"   report: {saved[0].relative_to(HERE) if saved else 'none saved'}")
            ok = ok and bool(saved)
        cost = sum(float(c) for c in re.findall(r"this answer \$([0-9.]+)", output))
        answer = [line for line in output.splitlines() if line.strip() and not line.startswith(("🌙", "   ", "💲", "Tool #", "  📨", "  ✅"))]
        print("   " + (answer[-1][:200] if answer else output[-200:]).strip())
        print(f"   {'✅ pass' if ok else '❌ FAIL'} · {took:.0f} s" + (f" · ${cost:.4f}" if cost else ""))
        if not ok:
            print("   ── output ──\n" + "\n".join("   " + line for line in output.splitlines()[-15:]))
        results.append((name, "pass" if ok else "FAIL", took, f"${cost:.4f}" if cost else ""))

    print("\n━━ Summary")
    for name, status, took, cost in results:
        print(f"   {name:10} {status:5} {took:5.0f} s  {cost}")
    failed = [r[0] for r in results if r[1] == "FAIL"]
    print(f"\n{'❌ Failed: ' + ', '.join(failed) if failed else '✅ Ready for the talk'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
