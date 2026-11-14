"""Run this 10-15 minutes before the talk: it warms everything the demo depends on and says what is not ready.

  python setup/prewarm.py              # everything
  python setup/prewarm.py --no-cloud   # skip the AgentCore runtime call

Each step is a real call, so a ❌ here is a failure you would have met on stage. Costs a few cents.
"""

import argparse
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import check  # noqa: E402
from core import load_config  # noqa: E402

PRESETS = ["clinic", "coffee-shop", "winery"]
MCP_PROMPT = "What time is it in Los Angeles right now? Then read https://en.wikipedia.org/wiki/Valle_de_Guadalupe and give me two facts I can tell my US guests."


def step(label: str, fn) -> bool:
    start = time.time()
    try:
        detail = fn()
        ok = detail is not False
    except Exception as err:  # noqa: BLE001 - every failure must be reported, not raised
        detail, ok = f"{type(err).__name__}: {str(err)[:160]}", False
    print(f"{'✅' if ok else '❌'} {label} ({time.time() - start:.0f} s)" + (f": {detail}" if isinstance(detail, str) and detail else ""))
    return ok


def luna(args: list[str], timeout: int = 280) -> str:
    out = subprocess.run([sys.executable, str(HERE / "luna.py"), *args], capture_output=True, text=True, timeout=timeout, cwd=HERE)
    return out.stdout + out.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-cloud", action="store_true", help="skip the AgentCore runtime call")
    args = parser.parse_args()
    cfg = load_config()
    m = cfg["model"]
    print(f"Model for this run: {m['provider']}:{m['id']} (director: {cfg['agency']['director'].get('model', m['id'])})\n")
    results = []

    for preset in PRESETS:
        results.append(step(f"preset {preset} passes the checker", lambda p=preset: not any(lv == "error" for lv, _ in check.problems(p)) or False))

    def sample_dates() -> object:
        import csv
        import datetime

        with (HERE / "business" / "winery" / "sales.csv").open(newline="") as f:
            newest = max(datetime.date.fromisoformat(r["date"]) for r in csv.DictReader(f))
        age = (datetime.date.today() - newest).days
        if age > 14:
            print(f"   the winery sales end {newest}, {age} days ago: the Monday briefing will report a data gap. Run python setup/refresh_sample_dates.py")
            return False
        return f"newest winery sales row is {newest}"

    results.append(step("the winery sample data is current", sample_dates))
    results.append(step("the model answers", lambda: "ok" if re.search(r"(?i)ok", luna(["--no-tools", "--ask", "Reply with the single word ok."])) else False))

    # The slow first run of scene 6: downloads the time and fetch servers, installs the fetch dependencies.
    def mcp() -> object:
        out = luna(["--preset", "winery", "--set", "memory.enabled=false", "--ask", MCP_PROMPT])
        return "" if re.search(r"get_current_time(?s:.*)fetch", out) else out[-200:]

    results.append(step("MCP servers start and answer (first run downloads packages)", mcp))

    if (cfg.get("guardrail") or {}).get("enabled"):
        results.append(step("guardrail refuses the bitcoin question", lambda: "refused" if "outside what I'm allowed" in luna(["--ask", "Should I buy bitcoin with my savings?"]) else False))
    if (cfg.get("memory") or {}).get("enabled"):
        import clean_memory

        def memory() -> object:
            found = clean_memory.records(cfg)
            if not found:
                print("   no records yet: seed with 'Remember this about me: I am vegetarian and I hate cold weather.'")
                return False
            if len(found) > 3:
                print(f"   {len(found)} records: tidy with python setup/clean_memory.py")
                return False
            return f"{len(found)} records"

        results.append(step("memory holds only what the memory scene needs", memory))
    if not args.no_cloud:
        import boto3

        def cloud() -> object:
            client = boto3.client("bedrock-agentcore-control", region_name=m["region"])
            arn = next(r["agentRuntimeArn"] for r in client.list_agent_runtimes()["agentRuntimes"] if r["agentRuntimeName"].startswith("luna"))
            reply = boto3.client("bedrock-agentcore", region_name=m["region"]).invoke_agent_runtime(
                agentRuntimeArn=arn, runtimeSessionId="prewarm-" + "0" * 30, payload=b'{"prompt": "What should I wear today in Ensenada?"}'
            )
            return "answered" if reply["response"].read() else False

        results.append(step("AgentCore runtime answers (warms the microVM)", cloud))

    print(f"\n{'✅ Warm and ready' if all(results) else '❌ ' + str(results.count(False)) + ' step(s) failed; fix them before the talk'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
