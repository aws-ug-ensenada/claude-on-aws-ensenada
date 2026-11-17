"""Level 4 — check that the MCP servers in config.yaml start and answer, without calling Claude.

  python setup/check_mcp.py

Starts each server with uvx (the first run downloads its packages from PyPI), lists its tools,
and makes one real call to `time` and `fetch`. Costs nothing and creates no AWS resources.
"""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from core import load_config, load_tools  # noqa: E402

CALLS = {
    "time": ("get_current_time", {"timezone": "America/Tijuana"}),
    "fetch": ("fetch", {"url": "https://aws.amazon.com/bedrock/agentcore/", "max_length": 300}),
}


def main() -> None:
    """Start every MCP server in config.yaml, list its tools, and make one real call to time and fetch (level 4)."""
    servers = list(load_config()["mcp_servers"])
    # Switch every server on for this check, whatever config.yaml says.
    cfg = load_config(overrides=[f"mcp_servers.{name}.enabled=true" for name in servers])
    for name in servers:
        missing = [var for var in cfg["mcp_servers"][name].get("pass_env", []) if var not in os.environ]
        if missing:
            print(f"{name} → skipped: set {', '.join(missing)} first")
            continue
        (client,) = load_tools(cfg, [], mcp=[name])
        with client:
            print(f"{name} → {[t.tool_name for t in client.list_tools_sync()]}")
            if name in CALLS:
                tool, args = CALLS[name]
                result = client.call_tool_sync(f"check-{name}", tool, args)
                print(f'  {tool}: {result["status"]} · {str(result["content"])[:150]}')


if __name__ == "__main__":
    main()
