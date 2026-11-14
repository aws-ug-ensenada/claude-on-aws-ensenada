# Strands Agents, and making Luna work for your own business

Luna is not a winery bot or a coffee-shop bot. It is one small agent with three things you can change: **who it works for**, **what it can see**, and **what it can do**. The winery in Valle de Guadalupe and the café on the Ensenada malecón are two examples of filling those in. A clinic, a law office, a school, a farm, a repair shop, a logistics team or a one-person consultancy fills them in the same way, without changing any code in the agent itself.

This page explains the framework underneath (Strands Agents), then walks through the five things you change to make Luna yours.

## What Strands Agents is

[Strands Agents](https://strandsagents.com) is an open-source Python framework from AWS for building agents. It runs the loop that turns a model into an agent:

1. You send a request.
2. The model decides whether it needs a tool and which one.
3. Strands calls your Python function (or MCP server) and gives the result back to the model.
4. This repeats until the model can answer.

You don't write that loop. You give Strands four things:

| You provide | In Strands | In Luna |
|---|---|---|
| A **model** | `BedrockModel(...)`, or the Anthropic, OpenAI and other providers | `build_model()` in [`assistant/core.py`](../assistant/core.py), set by `model:` in `config.yaml` |
| A **system prompt** | `system_prompt="..."` | Built from the `assistant:` and `user:` sections of the config and the preset |
| **Tools** | Python functions marked `@tool`, or tools from an MCP server | [`assistant/tools/`](../assistant/tools/) and `mcp_servers:` |
| Optional **session, memory and hooks** | `session_manager=`, `hooks=` | AgentCore Memory (level 3) and the guardrail hook (level 2) |

The whole agent is one call. This is Luna's solo agent, trimmed to the essentials:

```python
from strands import Agent, tool
from strands.models import BedrockModel

@tool
def get_stock(item: str) -> dict:
    """Return how many units of an item are on the shelf.

    Args:
        item: The product name, e.g. "espresso beans".
    """
    return {"item": item, "units": 12}      # read your database or CSV here

agent = Agent(
    model=BedrockModel(model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0", region_name="us-east-1"),
    system_prompt="You help run a small shop. Be brief and concrete.",
    tools=[get_stock],
)

agent("Do we need to reorder espresso beans?")
```

Three things to notice:

- **The docstring is the instruction.** The model reads it to decide when to call the tool, so write it for the model: what it does, what each argument means.
- **A tool is just a function.** Anything you can do in Python (call an API, query a database, send an email, read a file) can be a tool.
- **Strands is not tied to one model.** The same agent runs on Claude through Bedrock or through the Claude API. Luna switches with `model.provider` in the config.

Where to go next: the [Strands Agents documentation](https://strandsagents.com), and [`assistant/core.py`](../assistant/core.py), about 300 lines, which is the real thing.

## Make Luna work for your use case

Five changes, from easiest to most involved. Do the first three and you already have an agent for your business.

### 1. Say who it works for (a preset, no code)

Copy `presets/coffee-shop.yaml` to `presets/my-business.yaml` and rewrite the text. A third, non-demo example ships ready to try: `python luna.py --preset clinic` (a small dental clinic with fictional appointments, supplies, policies and prices). It was built by changing only the preset and the data, with no change to the agent.

The rewrite looks like this:

```yaml
assistant:
  name: Luna
  personality: calm and precise; brief
  extra_instructions: |
    You help run Northside Dental, a two-dentist clinic.
    Appointment data is in the files folder; policies and price lists are in the documents.
user:
  about: Owns the clinic. Busiest on Mondays; some patients pay in US dollars.
mcp_servers:
  files: {enabled: true, root: business/my-business}
```

Run it with `python luna.py --preset my-business`. Nothing else is required to try it.

### 2. Give it your data (a folder, no code)

Copy `business/coffee-shop/` to `business/my-business/` and replace the CSV files with exports from the systems you already use: bookings, sales, stock, tickets, inventory, timesheets. The agent can read these through the `files` MCP server, and it can only open that one folder. Reports it writes go to `reports/`.

### 3. Give it your documents (RAG, no code)

Put what people keep asking about in `my_documents/`: policies, price lists, menus, contracts, procedures. Then run `python setup/create_knowledge_base.py` the first time (it creates the knowledge base, about 2 minutes), and `python setup/create_knowledge_base.py --sync` after each later change. It costs cents; `python setup/cleanup.py` removes it. Luna searches them before answering and says where the answer came from. Documents can be in any language the model reads: an English question can be answered from a Spanish contract.

**Files or documents?** Use the folder for data that changes and that Luna may update (sales, stock, reports). Use `my_documents/` for reference text it should search and quote.

### 4. Give it new abilities (a little Python, or an MCP server)

Two ways, depending on whether someone already built it:

- **Someone built it: plug in an MCP server.** MCP (Model Context Protocol) is an open standard for connecting an agent to a service. There are servers for the web, files, time, GitHub, Slack, Google Drive, Gmail, databases and many CRMs. Add one under `mcp_servers:` in `config.yaml`. The server gets only what you hand it: one folder, read-only mail, its own key. See [customize.md § 7](customize.md#7-connect-more-mcp-servers).
- **Nobody built it: write a tool.** Copy [`assistant/tools/currency.py`](../assistant/tools/currency.py) to `tools/mytool.py`, write one function with `@tool` and a clear docstring, list it in `TOOLS`, and add its name to `tools:` in the config. A coding assistant can do this for you: *"Add a tool in tools/ that looks up a patient's next appointment in our booking API, following the pattern in tools/currency.py."*

### 5. Give it rules and a team

- **Rules.** Ask a person before anything risky (see how `tools/todo.py` asks before deleting), and add a Bedrock Guardrail for topics it must refuse ([levels.md § 2](levels.md#2--rules-amazon-bedrock-guardrails)). Rules that live outside the prompt can't be talked around.
- **A team.** When one agent has too many jobs, split them: a Director that gives orders and specialists that each have a short prompt and only their own tools ([customize.md § 5](customize.md#5-add-an-agent-to-the-agency-no-code)). It is configuration, not code.

## Ideas by kind of business

| Business | Files it reads | Documents it searches | A tool or connector worth adding |
|---|---|---|---|
| Winery or restaurant (the demo) | sales, reservations | handbook, supplier prices | web for guest questions |
| Coffee shop (the demo) | sales, inventory | recipes, supplier prices | exchange rates for tourists |
| Dental or medical clinic (`--preset clinic`, tested with files, documents and the agency) | appointments, supplies | policies, price list | calendar, reminders |
| Law or accounting office | matter or invoice list | templates, client terms | email drafts, deadline calendar |
| School or academy | attendance, grades export | handbook, syllabi | messaging to parents |
| Farm or food producer | harvest and orders | certifications, buyer terms | weather, market prices |
| Repair or field-service shop | job list, parts stock | manuals, warranty terms | parts supplier lookup |
| Logistics or delivery team | shipments export | carrier rules, customs guides | carrier tracking API |

These are starting points, not tested presets. Take the one closest to yours and change the three things in steps 1 to 3.

## Before real customers or real data

Luna on a laptop is a prototype. For anything that touches customers, read [production.md](production.md) first: separate accounts, least-privilege access, budget alarms, logging, and what to review before turning on write access.

## Checked from a clean checkout (2026-11-14)

On a fresh clone, with a new virtual environment and no `config.local.yaml`: the README quickstart commands (`luna.py --no-tools`, then the tool agent) worked, copying `coffee-shop` to a new preset and folder worked, and the Strands example above ran as written. The install took about 4 minutes on a Raspberry Pi 5. Small models can miscount rows in a CSV: on one run Luna reported 3 unconfirmed appointments where the file has 4, so for numbers that matter, give the agent a tool that counts instead of asking it to read and add up.
