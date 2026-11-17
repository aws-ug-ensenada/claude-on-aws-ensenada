# Code tour

Where each idea from the talk lives in the code, for answering "where is that defined?". Functions are named rather than line numbers, so this stays true when lines move: in VS Code, `Cmd/Ctrl+Shift+O` jumps to a function by name. Every function has a one-line docstring saying what it does.

Three answers cover almost every question: **the model and the agents are in [`core.py`](../assistant/core.py), the tools are in [`tools/`](../assistant/tools), and the cloud wrapper is [`app.py`](../assistant/app.py).**

## An agent is a model, a prompt and tools (levels 1–2)

| Where | What it does | What to say |
|---|---|---|
| `core.py` → `load_config` | Reads `config.yaml`, then the preset, then `config.local.yaml`, then `--set` values; each one overrides the one before | "Everything you saw change on stage is configuration, not code." |
| `core.py` → `system_prompt` | Builds Luna's instructions: name, personality, answer length, today's date, the reply language | The language rule goes last on purpose: the larger models otherwise follow the city's language |
| `core.py` → `build_model` | Picks the brain: `AnthropicModel` (Claude API) when `provider: anthropic`, otherwise `BedrockModel`. On Bedrock the guardrail is attached right here | Same agent, any provider |
| `core.py` → `build_solo` | One `Agent(model, system_prompt, tools, hooks, session_manager)` call | Strands runs the loop: think, call a tool, read the result, answer |

## Tools: the agent's hands (level 2, scene 2)

| Where | What it does | What to say |
|---|---|---|
| [`tools/weather.py`](../assistant/tools/weather.py) → `get_weather`, [`tools/currency.py`](../assistant/tools/currency.py) → `convert_currency` | Plain Python functions marked `@tool` | "The docstring isn't a comment for humans: Claude reads it to decide when to call the tool." |
| [`tools/todo.py`](../assistant/tools/todo.py) → `delete_task`, `ask_human` | The tool asks `[y/N]` before deleting | Human in the loop. In the cloud ([`app.py`](../assistant/app.py), top) nobody can approve, so the answer is always no |
| `core.py` → `load_tools`, `python_tools` | Turn the tool names in the config into tool objects | |

## MCP: ready-made tools (level 4, scenes 6–7)

| Where | What it does | What to say |
|---|---|---|
| `core.py` → `_mcp_client` | Starts an MCP server: a local process over stdio (`uvx`, `npx`) or a remote one by URL | "No code was written for the time, fetch or files tools." |
| [`tools/tables.py`](../assistant/tools/tables.py) → `count_rows`, `sum_column` | Exact counts and sums over the business CSV files, only inside the business folder | "We don't let the model do arithmetic in its head." |

## A team of agents (levels 6–7, scenes 5 and 8)

| Where | What it does | What to say |
|---|---|---|
| `core.py` → `build_specialist` | Each specialist is the same kind of `Agent`, with its own role and tools | |
| `core.py` → `order_tool` | Wraps each specialist as a `give_order` tool | The key trick: the Director only calls tools, and those tools happen to be other agents. These are the 📨 and ✅ lines |
| `core.py` → `build_agency` | The Director plus the specialists; with `remote=True` (fleet mode) each specialist is an `A2AAgent` reached over HTTP | |
| [`fleet_server.py`](../assistant/fleet_server.py) → `main` | The other side of fleet mode: `A2AServer(agent=build_specialist(...)).serve()`, one port per specialist (9001–9005) | Agents talking to agents over a standard protocol (A2A) |

## AWS services (levels 2, 3, 5 and 8)

| Where | Service | What it does |
|---|---|---|
| `core.py` → `input_guardrail` | Bedrock Guardrails (scene 9) | With the Claude API, a hook sends what the user typed to `ApplyGuardrail` before the model runs. A block sets `event.cancel`: no model runs, so the cost is $0. On Bedrock, `build_model` attaches the guardrail instead |
| `core.py` → `memory_session` | AgentCore Memory (scene 10) | An `AgentCoreMemorySessionManager` saves the conversation and brings back the extracted preferences for the same user |
| [`tools/documents.py`](../assistant/tools/documents.py) → `search_my_documents` | Knowledge Bases + S3 Vectors (scene 11) | `retrieve` returns the closest chunks of your documents, with the file name to cite |
| [`app.py`](../assistant/app.py) → `invoke` | AgentCore Runtime (scene 12) | `BedrockAgentCoreApp` plus `@app.entrypoint`: the same `core.py`, wrapped in about 30 lines |
| `core.py` → `gateway_url`, `_gateway_client` | AgentCore Gateway | In the cloud, weather and currency come through the Gateway as MCP tools, signed with SigV4 (the `mcp_proxy_for_aws.sigv4_helper` lines in the runtime logs) |

## The chat and the cost line

| Where | What it does |
|---|---|
| [`luna.py`](../assistant/luna.py) → `main` | The chat loop: read a question, call the agent, stream the answer, print the cost |
| `core.py` → `usage_of`, `cost` and [`pricing.yaml`](../assistant/pricing.yaml) | Tokens in and out, times the price per million tokens |
| `luna.py` → `print_cost` | Prints the 💲 line: this answer per agent, and the session total. How to read it: [clip-notes.md](clip-notes.md#reading-the-cost-line) |
| `luna.py` → `explain` | Turns common errors (expired credentials, no model access) into plain advice |

## Setup and rehearsal scripts

| Where | What it does |
|---|---|
| [`setup/`](../assistant/setup) `create_guardrail.py`, `create_memory.py`, `create_knowledge_base.py` | Create the AWS pieces for levels 2, 3 and 5 and record them in `config.local.yaml` |
| `setup/_discover.py` | Finds those pieces by name and rebuilds `config.local.yaml` on a new machine |
| `setup/prewarm.py` | Warm-up before the talk: presets, sample data, model, MCP, guardrail, memory, cloud runtime |
| [`rehearse.py`](../assistant/rehearse.py) | Runs every scene as on stage and checks each output |
