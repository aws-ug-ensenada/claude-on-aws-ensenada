"""Check a preset and the config without calling AWS or Claude:  python luna.py --preset my-business --check

Catches the mistakes people make when they copy a preset: a typo in a key, a folder that doesn't exist,
a tool or agent that isn't there, a switched-on feature with no ID. ❌ stops it from working, ⚠️ may surprise you.
"""

import difflib
import os
import pathlib
import re
import shutil

import yaml

HERE = pathlib.Path(__file__).parent


def problems(preset: str | None, overrides: list[str] = ()) -> list[tuple[str, str]]:
    """(level, message) pairs; level is 'error' or 'warn'. Empty means all good."""
    out: list[tuple[str, str]] = []
    err = lambda m: out.append(("error", m))  # noqa: E731
    warn = lambda m: out.append(("warn", m))  # noqa: E731

    base = yaml.safe_load((HERE / "config.yaml").read_text())
    raw: dict = {}
    if preset:
        path = HERE / "presets" / f"{preset}.yaml"
        if not path.exists():
            names = sorted(p.stem for p in (HERE / "presets").glob("*.yaml"))
            hint = difflib.get_close_matches(preset, names, n=1)
            err(f"presets/{preset}.yaml does not exist. Presets: {', '.join(names)}" + (f" (did you mean {hint[0]}?)" if hint else ""))
            return out
        try:
            raw = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError as e:
            err(f"presets/{preset}.yaml is not valid YAML: {str(e).splitlines()[0]}")
            return out
        if not isinstance(raw, dict):
            err(f"presets/{preset}.yaml must be a mapping of settings, not a {type(raw).__name__}")
            return out

        # Typos: a key the config has never heard of is silently ignored, which looks like "it does nothing".
        for key, value in raw.items():
            if key not in base:
                hint = difflib.get_close_matches(key, base, n=1)
                err(f"unknown setting '{key}'" + (f" (did you mean '{hint[0]}'?)" if hint else ""))
            elif isinstance(value, dict) and isinstance(base[key], dict) and key not in ("mcp_servers", "agency"):
                for sub in value:
                    if sub not in base[key]:
                        hint = difflib.get_close_matches(sub, base[key], n=1)
                        err(f"unknown setting '{key}.{sub}'" + (f" (did you mean '{key}.{hint[0]}'?)" if hint else ""))

    from core import load_config

    cfg = load_config(preset, overrides)

    if not (cfg["assistant"].get("extra_instructions") or "").strip() and preset:
        warn("assistant.extra_instructions is empty: say whose business this is and where its data lives")

    # Tools
    for name in cfg.get("tools") or []:
        if not (HERE / "tools" / f"{name}.py").exists():
            err(f"tools: '{name}' has no file tools/{name}.py")

    # MCP servers
    servers = cfg.get("mcp_servers") or {}
    for name, server in servers.items():
        if not server.get("enabled"):
            continue
        if not (server.get("command") or server.get("url")):
            err(f"mcp_servers.{name}: needs a command or a url")
        elif server.get("command") and not shutil.which(server["command"]):
            warn(f"mcp_servers.{name}: '{server['command']}' is not installed on this machine")
        for var in server.get("pass_env") or []:
            if not os.environ.get(var):
                warn(f"mcp_servers.{name}: environment variable {var} is not set")
        if name == "files":
            root = server.get("root") or ""
            folder = (HERE / root).resolve()
            if not root:
                err("mcp_servers.files.root: choose the one folder Luna may read and write")
            elif HERE.resolve() not in (folder, *folder.parents):
                err(f"mcp_servers.files.root: '{root}' is outside assistant/")
            elif not folder.is_dir():
                err(f"mcp_servers.files.root: folder '{root}' does not exist (copy business/coffee-shop/ to start)")
            elif not any(p.is_file() and p.name != ".gitkeep" for p in folder.rglob("*")):
                warn(f"mcp_servers.files.root: '{root}' has no files yet; put your CSV exports in it")

    # Documents the preset points to, and whether they can be searched
    text = (HERE / "presets" / f"{preset}.yaml").read_text() if preset else ""
    for ref in sorted(set(re.findall(r"my_documents/([\w.-]+\.\w+)", text))):
        if not (HERE / "my_documents" / ref).exists():
            err(f"my_documents/{ref} is mentioned in the preset but does not exist")
    if "documents" in (cfg.get("tools") or []) and not (cfg.get("knowledge_base") or {}).get("enabled"):
        warn("documents search is off: run python setup/create_knowledge_base.py to make my_documents/ searchable")

    # Features that are switched on but have nothing behind them
    for feature in ("guardrail", "memory", "knowledge_base"):
        section = cfg.get(feature) or {}
        if section.get("enabled") and not section.get("id"):
            err(f"{feature}.enabled is true but {feature}.id is empty (python setup/create_{feature}.py)")

    # The agency's roster
    known_servers = set(servers)
    for agent in (cfg.get("agency") or {}).get("agents") or []:
        for tool in agent.get("tools") or []:
            if not (HERE / "tools" / f"{tool}.py").exists():
                err(f"agency agent '{agent.get('name')}': tool '{tool}' has no file tools/{tool}.py")
        for server in agent.get("mcp") or []:
            if server not in known_servers:
                err(f"agency agent '{agent.get('name')}': mcp server '{server}' is not defined in mcp_servers")

    # The brain
    model = cfg["model"]
    if model.get("provider", "bedrock") == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        warn("model.provider is anthropic but ANTHROPIC_API_KEY is not set")
    return out


def run(preset: str | None, overrides: list[str] = ()) -> int:
    """Print the findings; return the exit code (1 if anything would stop it working)."""
    found = problems(preset, overrides)
    label = f"preset '{preset}'" if preset else "config.yaml"
    for level, message in found:
        print(f"{'❌' if level == 'error' else '⚠️ '} {message}")
    errors = sum(level == "error" for level, _ in found)
    if not found:
        print(f"✅ {label} looks good")
    else:
        print(f"\n{errors} error(s), {len(found) - errors} warning(s) in {label}")
    return 1 if errors else 0
