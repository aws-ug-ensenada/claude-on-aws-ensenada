"""Builds agents from config.yaml. Everything the agent does is decided here from parameters."""

import copy
import datetime
import importlib
import os
import pathlib
import re

import yaml
from strands import Agent, tool

HERE = pathlib.Path(__file__).parent

LENGTHS = {
    "short": "Answer in 1-3 sentences unless the user asks for more.",
    "medium": "Answer in a short paragraph or a brief list.",
    "detailed": "Give complete, well-structured answers.",
}


# ── Configuration ────────────────────────────────────────────


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        out[key] = _merge(out[key], value) if isinstance(value, dict) and isinstance(out.get(key), dict) else value
    return out


def load_config(preset: str | None = None, overrides: list[str] = ()) -> dict:
    """config.yaml, then config.local.yaml (written by setup/), then presets/<preset>.yaml, then each --set key.path=value."""
    cfg = yaml.safe_load((HERE / "config.yaml").read_text())
    local = HERE / "config.local.yaml"
    if local.exists():
        cfg = _merge(cfg, yaml.safe_load(local.read_text()) or {})
    if preset:
        cfg = _merge(cfg, yaml.safe_load((HERE / "presets" / f"{preset}.yaml").read_text()))
    for item in overrides:
        path, _, raw = item.partition("=")
        *parents, leaf = path.split(".")
        node = cfg
        for key in parents:
            node = node.setdefault(key, {})
        node[leaf] = yaml.safe_load(raw)
    return cfg


def system_prompt(cfg: dict, role: str = "", instructions: str = "") -> str:
    a, u = cfg["assistant"], cfg["user"]
    language = (
        "Reply in the same language the user writes in."
        if a["language"] == "auto"
        else f'Always reply in {a["language"]}.'
    )
    lines = [
        f'You are {a["name"]}, a personal assistant. Personality: {a["personality"]}.',
        role,
        language,
        LENGTHS.get(a["answer_length"], a["answer_length"]),
        f'The user is {u["name"]}, based in {u["city"]}. Their currency is {u["currency"]}. {u.get("about") or ""}',
        f"Today is {datetime.date.today():%A, %Y-%m-%d}.",
        "Use your tools to get real data instead of guessing. If you can't find out, say so.",
        a.get("extra_instructions") or "",
        instructions,
    ]
    return "\n".join(line.strip() for line in lines if line and line.strip())


# ── Model (the brain) ────────────────────────────────────────


def build_model(cfg: dict, model_id: str | None = None):
    m = cfg["model"]
    model_id = model_id or m["id"]
    # Claude 5.x models reject `temperature`, so it's only sent to older ones.
    sampling = {} if re.search(r"claude-[a-z]+-5", model_id) else {"temperature": m["temperature"]}
    if m.get("provider", "bedrock") == "anthropic":
        from strands.models.anthropic import AnthropicModel

        return AnthropicModel(
            client_args={"api_key": os.environ["ANTHROPIC_API_KEY"]},
            model_id=short_model_name(model_id),
            max_tokens=m["max_tokens"],
            params=sampling,
        )

    from strands.models import BedrockModel

    kwargs = dict(model_id=model_id, region_name=m["region"], max_tokens=m["max_tokens"], **sampling)
    g = cfg.get("guardrail") or {}
    if g.get("enabled"):
        kwargs.update(guardrail_id=g["id"], guardrail_version=str(g["version"]), guardrail_trace="enabled")
    return BedrockModel(**kwargs)


def short_model_name(model_id: str) -> str:
    """global.anthropic.claude-haiku-5-5 → claude-haiku-5-5; …claude-haiku-4-5-20251001-v1:0 → claude-haiku-4-5-20251001"""
    return re.sub(r"-v\d+:\d+$", "", re.sub(r"^((global|us|eu|apac)\.)?anthropic\.", "", model_id))


# ── Tools (the hands) ────────────────────────────────────────


def load_tools(cfg: dict, names: list[str], mcp: list[str] | None = None) -> list:
    """Python tool groups from tools/, plus MCP servers. mcp=None means every enabled server."""
    tools = []
    gateway = gateway_url(cfg)
    for name in names:
        if gateway and name in cfg["gateway"]["tools"]:
            tools.append(_gateway_client(gateway, name, cfg["model"]["region"]))
        else:
            tools += python_tools(cfg, name)
    for name, server in (cfg.get("mcp_servers") or {}).items():
        if server.get("enabled") and (mcp is None or name in mcp):
            tools.append(_mcp_client(server))
    return tools


def python_tools(cfg: dict, name: str) -> list:
    """A tool module exports TOOLS, or tools(cfg) when it needs settings (it returns [] until its level is set up)."""
    module = importlib.import_module(f"tools.{name}")
    return module.tools(cfg) if hasattr(module, "tools") else module.TOOLS


def gateway_url(cfg: dict) -> str | None:
    """The Gateway's MCP endpoint, which AgentCore Runtime passes in an environment variable (level 8)."""
    name = re.sub(r"[^A-Za-z0-9]", "_", (cfg.get("gateway") or {}).get("name", "")).upper()
    url = os.environ.get(f"AGENTCORE_GATEWAY_{name}_URL") if name else None
    if not url:
        return None
    # A gateway created without an MCP-only protocol type gets a bare origin; MCP lives under /mcp.
    return url if url.rstrip("/").endswith("/mcp") else url.rstrip("/") + "/mcp"


def _gateway_client(url: str, target: str, region: str):
    """One Gateway target's tools over MCP, signed with the caller's AWS credentials (SigV4)."""
    from mcp_proxy_for_aws.sigv4_helper import create_sigv4_auth
    from strands.tools.mcp import MCPClient

    return MCPClient(
        url=url,
        auth_provider=create_sigv4_auth("bedrock-agentcore", region),
        tool_filters={"allowed": [re.compile(f"^{re.escape(target)}___")]},  # Gateway names tools <target>___<operationId>
        startup_timeout=60,
    )


def _mcp_client(server: dict):
    from mcp import StdioServerParameters, stdio_client
    from mcp.client.stdio import get_default_environment
    from strands.tools.mcp import MCPClient

    if server.get("url"):  # a remote server
        headers = {h: os.environ[var] for h, var in (server.get("headers_env") or {}).items() if var in os.environ}
        return MCPClient(url=server["url"], headers=headers or None, startup_timeout=server.get("startup_timeout", 60))
    # Only PATH, HOME and the like, the server's own env, and the variables it is allowed to see.
    env = {**get_default_environment(), **(server.get("env") or {})}
    env |= {var: os.environ[var] for var in server.get("pass_env", []) if var in os.environ}
    args = list(server.get("args", []))
    if server.get("root"):  # the one folder a files server may use
        root = (HERE / server["root"]).resolve()
        root.mkdir(parents=True, exist_ok=True)
        args.append(str(root))
    params = StdioServerParameters(command=server["command"], args=args, env=env)
    # The first start downloads the server's packages, which can take minutes on a slow network.
    return MCPClient(lambda: stdio_client(params), startup_timeout=server.get("startup_timeout", 300))


# ── Guardrail without Bedrock (level 2) ──────────────────────


def input_guardrail(cfg: dict) -> list:
    """On Bedrock the guardrail is attached to the model. With the Claude API it isn't, so this hook
    checks what the user typed with Bedrock's standalone ApplyGuardrail API before Claude sees it."""
    g = cfg.get("guardrail") or {}
    if not g.get("enabled") or cfg["model"].get("provider", "bedrock") == "bedrock":
        return []
    import boto3
    from strands.hooks import BeforeInvocationEvent, HookProvider

    client = boto3.client("bedrock-runtime", region_name=cfg["model"]["region"])

    class InputGuardrail(HookProvider):
        def register_hooks(self, registry, **kwargs):
            registry.add_callback(BeforeInvocationEvent, self.check)

        def check(self, event):
            typed = " ".join(c["text"] for m in event.messages or [] if m["role"] == "user" for c in m["content"] if "text" in c)
            if not typed.strip():
                return
            resp = client.apply_guardrail(guardrailIdentifier=g["id"], guardrailVersion=str(g["version"]),
                                          source="INPUT", content=[{"text": {"text": typed}}])
            if resp["action"] == "GUARDRAIL_INTERVENED":
                event.cancel = resp["outputs"][0]["text"] if resp.get("outputs") else "Blocked by the guardrail."

    return [InputGuardrail()]


# ── Memory (level 3) ─────────────────────────────────────────


def memory_session(cfg: dict, session_id: str):
    mem = cfg.get("memory") or {}
    if not mem.get("enabled"):
        return None
    from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
    from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

    actor = re.sub(r"[^a-zA-Z0-9-]", "-", cfg["user"]["name"]).lower()
    config = AgentCoreMemoryConfig(
        memory_id=mem["id"],
        session_id=session_id,
        actor_id=actor,
        retrieval_config={f"/preferences/{actor}": RetrievalConfig(top_k=5)},
    )
    return AgentCoreMemorySessionManager(config, region_name=cfg["model"]["region"])


# ── Agents ───────────────────────────────────────────────────


def build_solo(cfg: dict, use_tools: bool = True, session_id: str = "cli", quiet: bool = False) -> Agent:
    return Agent(
        name=cfg["assistant"]["name"],
        model=build_model(cfg),
        system_prompt=system_prompt(cfg),
        tools=load_tools(cfg, cfg["tools"]) if use_tools else [],
        session_manager=memory_session(cfg, session_id),
        hooks=input_guardrail(cfg),
        callback_handler=None if quiet else _default_handler(),
    )


def active_agents(cfg: dict) -> list[dict]:
    """The agency roster, minus specialists whose tools aren't switched on yet (e.g. no MCP servers enabled)."""

    def ready(spec: dict) -> bool:
        if not (spec.get("tools") or spec.get("mcp")):
            return True  # a thinking-only agent needs no tools
        servers = cfg.get("mcp_servers") or {}
        return any((servers.get(name) or {}).get("enabled") for name in spec.get("mcp", [])) or any(
            python_tools(cfg, name) for name in spec.get("tools", [])
        )

    return [spec for spec in cfg["agency"]["agents"] if ready(spec)]


def build_specialist(cfg: dict, spec: dict) -> Agent:
    """One member of the agency. Works silently; the Director relays its answer."""
    return Agent(
        name=spec["name"],
        description=spec["role"],
        model=build_model(cfg, spec.get("model")),
        system_prompt=system_prompt(cfg, role=f'Your job on the team: {spec["role"]}', instructions=spec.get("instructions", "")),
        tools=load_tools(cfg, spec.get("tools", []), mcp=spec.get("mcp", [])),
        callback_handler=None,
    )


def order_tool(name: str, role: str, member):
    """Wrap a team member (local Agent or remote A2AAgent) as a tool the Director can give orders to."""

    @tool(name=name, description=f"Give an order to {name}: {role}")
    def give_order(order: str) -> str:
        """Args:
        order: A clear, self-contained instruction for this team member.
        """
        print(f"\n  📨 Director → {name}: {order}", flush=True)
        answer = str(member(order)).strip()
        print(f"  ✅ {name} → Director: {answer[:160]}{'…' if len(answer) > 160 else ''}", flush=True)
        return answer

    return give_order


def build_agency(cfg: dict, session_id: str = "cli", remote: bool = False, quiet: bool = False):
    """Director (master agent) + specialists. remote=True talks to each specialist over A2A (fleet mode).

    Returns (director, specialists) — specialists are local Agents, or A2AAgents when remote.
    """
    agency = cfg["agency"]
    team = active_agents(cfg)
    members = {}
    for spec in team:
        if remote:
            from strands.agent.a2a_agent import A2AAgent

            members[spec["name"]] = A2AAgent(endpoint=spec["url"], name=spec["name"], description=spec["role"])
        else:
            members[spec["name"]] = build_specialist(cfg, spec)

    roster = "\n".join(f'- {s["name"]}: {s["role"]}' for s in team)
    director = Agent(
        name="director",
        model=build_model(cfg, agency["director"].get("model")),
        system_prompt=system_prompt(
            cfg,
            role="You are the Director of a team of specialist agents. You never do the work yourself: "
            "break the request into orders, send each order to the right specialist (in parallel when "
            "independent), then combine their answers into one reply for the user.",
            instructions=f"Your team:\n{roster}\n{agency['director'].get('instructions', '')}",
        ),
        tools=[order_tool(s["name"], s["role"], members[s["name"]]) for s in team],
        session_manager=memory_session(cfg, session_id),
        hooks=input_guardrail(cfg),
        callback_handler=None if quiet else _default_handler(),
    )
    return director, members


def _default_handler():
    from strands.handlers.callback_handler import PrintingCallbackHandler

    return PrintingCallbackHandler()


# ── Cost ─────────────────────────────────────────────────────


def usage_of(agent) -> tuple[int, int]:
    metrics = getattr(agent, "event_loop_metrics", None)
    if not metrics:
        return 0, 0
    u = metrics.accumulated_usage
    return u.get("inputTokens", 0), u.get("outputTokens", 0)


def cost(cfg: dict, model_id: str, tokens_in: int, tokens_out: int) -> float:
    prices = yaml.safe_load((HERE / "pricing.yaml").read_text())["models"].get(short_model_name(model_id))
    if not prices:
        return 0.0
    provider = cfg["model"].get("provider", "bedrock")
    tier = "anthropic" if provider == "anthropic" else ("global" if model_id.startswith("global.") else "regional")
    p = prices[tier]
    return (tokens_in * p["input"] + tokens_out * p["output"]) / 1_000_000
