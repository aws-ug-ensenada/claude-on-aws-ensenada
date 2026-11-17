"""Level 7 — run agency specialists as separate services that speak A2A (agent-to-agent protocol).

  python fleet_server.py planner     # one specialist, on the port in its config url
  python fleet_server.py --all       # every specialist, each in its own process

Then, in another terminal:  python luna.py --mode fleet
"""

import argparse
import subprocess
import sys
from urllib.parse import urlparse

from core import active_agents, build_specialist, load_config


def main() -> None:
    """Serve one specialist over A2A on the port in its url, or with --all start one process per specialist (level 7)."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", nargs="?", help="specialist name from config.yaml agency.agents")
    parser.add_argument("--all", action="store_true", help="start every specialist")
    parser.add_argument("--preset")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    args = parser.parse_args()
    cfg = load_config(args.preset, args.set)
    specs = {s["name"]: s for s in active_agents(cfg)}

    if args.all:
        passthrough = (["--preset", args.preset] if args.preset else []) + [f"--set={s}" for s in args.set]
        procs = [subprocess.Popen([sys.executable, __file__, name, *passthrough]) for name in specs]
        try:
            for p in procs:
                p.wait()
        except KeyboardInterrupt:
            for p in procs:
                p.terminate()
        return

    if args.name not in specs:
        parser.error(f"choose one of: {', '.join(specs)} (or --all)")
    spec = specs[args.name]

    from strands.multiagent.a2a import A2AServer

    url = urlparse(spec["url"])
    print(f"🛰️  {spec['name']} listening on {spec['url']}", flush=True)
    A2AServer(agent=build_specialist(cfg, spec), host=url.hostname, port=url.port, http_url=spec["url"]).serve()


if __name__ == "__main__":
    main()
