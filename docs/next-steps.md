# Status and next steps

Where the work stands and how to pick it up on another machine. Last updated **2026-10-31**.

## Where things stand

| Level | Built | Tested | Notes |
|---|---|---|---|
| 1 · Solo assistant | ✅ | ✅ On Claude 4.x | Plain chatbot and tool agent pass on Haiku 4.5; 5.5 declined for now (step 2) |
| 2 · Guardrails | ✅ | ✅ On Claude 4.x | Guardrail created; refuses "Should I buy bitcoin?", normal questions still work |
| 3 · Memory | ✅ | ✅ On Claude 4.x | Memory created; a new session recalled "vegetarian, hates cold" told 2 minutes earlier |
| 4 · MCP servers | ✅ | ✅ | `time`, `fetch`, `files` and `aws_docs` start and answer (`setup/check_mcp.py`); `gmail` is opt-in and untested; business scenes use several servers in one answer |
| 5 · RAG (Knowledge Base) | ✅ | ✅ On Claude 4.x | Knowledge base created, 3 files indexed; rent question answered correctly (English question, Spanish document) |
| 6 · Agency | ✅ | ✅ On Claude 4.x | Director (Sonnet 4.6) briefs planner, finance and organizer in parallel |
| 7 · Fleet (A2A) | ✅ | ✅ On Claude 4.x | `fleet_server.py --all` + `--mode fleet`: same answer as agency mode over A2A |
| 8 · Cloud (AgentCore) | ✅ | ✅ Deployed | Runtime answers with tools from the Gateway, the knowledge base, the guardrail and memory |

"Offline only" means the code was run without calling AWS. Every request it would send was checked against the real API definitions, but nothing reached AWS.

**AWS resources that exist** (the presenter's account, us-east-1, created 2026-10-31; `python setup/cleanup.py` deletes all of them):

| Level | Resource | ID or name |
|---|---|---|
| 2 | Bedrock guardrail | `luna-assistant` |
| 3 | AgentCore Memory | `luna_assistant-<suffix>` |
| 5 | Knowledge base | created by `setup/create_knowledge_base.py` |
| 5 | S3 bucket (documents) | `luna-docs-<account-id>-us-east-1` |
| 5 | S3 vector bucket and index | `luna-docs-vectors-<account-id>` / `luna-docs` |
| 5 | IAM role | `luna-docs-knowledge-base` |
| 8 | AgentCore Runtime (stack `AgentCore-luna-default`) | `luna_default_luna-<suffix>`, with its role and log group; remove with `agentcore remove all --yes && agentcore deploy --yes` |
| 8 | AgentCore Gateway (same stack) | `luna-default-lunatools`, targets `weather` and `currency` |
| 8 | AgentCore Identity API key (same stack) | `luna_default_publicapis`, a placeholder; a Secrets Manager secret, ~$0.40/month |
| 8 | CDK bootstrap (stack `CDKToolkit`) | one-time; asset bucket and deploy roles; free while idle |

Also in place: the Haiku 5.5 Marketplace agreement (the 5.5 quota requests were declined; see [bedrock-access.md](bedrock-access.md)), and an AWS Budget of **$20** a month for Claude 4.x (alerts at 85% and 100% actual, 100% forecast).

These IDs live in `config.local.yaml`, which is git-ignored. On another machine, copy that file across or the setup scripts and Luna won't find the resources.

## Set up a new machine

You need Python 3.11 or newer, [uv](https://docs.astral.sh/uv/) (for the MCP servers), Git, and AWS credentials for your account. Node.js 20.12 or newer is needed for the MCP servers (level 4) and level 8. The full list is in [prerequisites.md](prerequisites.md).

```bash
git clone git@github.com:aws-ug-ensenada/claude-on-aws-ensenada.git
cd claude-on-aws-ensenada/assistant
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AWS_PROFILE=<your-profile> AWS_REGION=us-east-1   # or however you load your credentials
aws sts get-caller-identity                              # confirm it's the right account
```

`config.local.yaml` (the IDs written by the setup scripts) and `data/todo.json` are git-ignored, so a new machine starts clean. If the resources already exist, copy `config.local.yaml` across by hand, or the new machine won't know their IDs.

## Next steps, in order

### 1. Check MCP on the new machine (free, no AWS)

```bash
python setup/check_mcp.py
```

The first run downloads the servers' packages from PyPI, and `fetch` also runs `npm install`. That used to hit the MCP client's 30-second start limit on a fresh machine; the limit is now 300 seconds (set `startup_timeout` on a server in `config.yaml` to change it).

Passed on the second machine on 2026-10-31.

### 2. Claude access (done; 5.5 declined for now)

Details, quota codes and commands are in [bedrock-access.md](bedrock-access.md). In short, as of 2026-10-31:

- Use-case form submitted; Haiku 5.5 agreement accepted.
- The account's tokens-per-minute quota for every Claude 5.5 model is **0**. AWS declined the increase requests for Haiku and Sonnet 5.5 automatically, citing account history.
- Claude Haiku 4.5 and Sonnet 4.6 work, so **they are now Luna's defaults** (`config.yaml`, `presets/professional.yaml`), with their prices in `pricing.yaml`.

Decided 2026-11-01: **the presenter uses Claude 5.5 through the Claude API** (`model` and `agency.director.model` in `config.local.yaml`). The guardrail still checks what you type, through ApplyGuardrail. Attendees' default stays Claude 4.x on Bedrock, which works without an API key.

Still to do:

- Re-check the 5.5 quotas every week or two; AWS says access can change on its own as the account builds history.
- Ask the AWS User Group's AWS community contact whether they can escalate the 5.5 quota.
- Claude 5.5 already works through the **Claude API** with your own key (every level; the guardrail checks what you type); see [bedrock-access.md § The Claude API](bedrock-access.md#the-claude-api-instead-of-bedrock). Load the key into `ANTHROPIC_API_KEY` from a secrets manager or with `read -rs`, never from a file in the repo.
- When 5.5 opens up, re-run step 3 with the `--set` lines in [bedrock-access.md § Switching to Claude 5.5](bedrock-access.md#switching-to-claude-55) and decide whether to switch the defaults back.

### 3. Live tests (Claude calls only, a few cents in total)

All five passed on 2026-10-31 on Claude 4.x, which is now the default, so the commands below need no extra flags.

- Claude 5.x models reject `temperature` (*"temperature is deprecated for this model"*). Luna now sends it only to older models.
- Haiku 4.5 once reported 85 USD as 1,360.61 MXN when the tool had returned 1,607.19. The tool now returns `converted_amount` and `rate` instead of Frankfurter's ambiguous `rates`, and two re-runs gave the right number.

```bash
python luna.py --no-tools --ask "What should I wear today?"
python luna.py --ask "What should I wear today, and how much is 85 dollars in pesos?"
python luna.py --mode agency --ask "Plan my Saturday at the beach, budget 50 USD, add sunscreen to my list"
python luna.py --set mcp_servers.time.enabled=true --set mcp_servers.fetch.enabled=true --ask "What time is it in Madrid?"
python fleet_server.py --all          # terminal 1
python luna.py --mode fleet           # terminal 2
```

Check that the cost line after each answer looks right compared with [costs.md](costs.md).

### 4. Create AWS resources (only when you decide to; pay per use)

Each script is independent, and `setup/cleanup.py` deletes everything they created.

```bash
python setup/create_guardrail.py        # level 2
python setup/create_memory.py           # level 3, 2–3 minutes
python setup/create_knowledge_base.py   # level 5, ~2 minutes; --sync after changing my_documents/
python setup/cleanup.py                 # when done
```

Set an **AWS Budget alarm at $10** on the account before you create anything.

Done on 2026-10-31: budget created, then all three scripts run and tested on Claude 4.x (see the table at the top).

### 5. Level 8: cloud

**Phase A, the runtime (deployed 2026-10-31):**

- `agentcore deploy` bootstrapped CDK and created stack `AgentCore-luna-default`. `agentcore invoke --runtime luna` answered with tools, the knowledge base, the guardrail and memory.
- The CLI also **turned on CloudWatch Transaction Search** for the account; its default indexing rule is at 100% of spans (1% is free). Left as is for rehearsals; lower it after the talk with `aws xray update-indexing-rule --name Default --rule '{"Probabilistic":{"DesiredSamplingPercentage":1}}'`.
- Testing it found a guardrail and memory conflict: the prompt-attack filter at HIGH blocked memory's preferences block. It's now MEDIUM (see [levels.md § 2](levels.md#2--rules-amazon-bedrock-guardrails)).

Built and tested locally first:

- The repo root is an AgentCore CLI project (`agentcore/agentcore.json`). The `luna` runtime points at `assistant/` with `app.py` as the entrypoint; nothing is copied into `app/agent/`.
- `assistant/pyproject.toml` lists the dependencies for the runtime; `requirements.txt` stays for laptops.
- `setup/cloud_policy.py` writes the IAM policy for the guardrail, memory and knowledge base.
- `agentcore build` packages it: a 52 MB zip with ARM64 wheels; the synthesized stack includes the three extra permissions.
- `agentcore dev` served it locally and passed: tools, knowledge base, guardrail, and agency mode with memory.

Commands are in [levels.md § 8](levels.md#8--cloud-agentcore-runtime-gateway-and-observability). `agentcore deploy` creates the runtime, its role and log group, and bootstraps CDK in the account the first time. Cost: see [costs.md](costs.md), under $1 for a week of light use.

**Phase B, the Gateway (deployed 2026-10-31):**

- Gateway `lunatools` (`AWS_IAM` inbound) with OpenAPI targets `weather` (Open-Meteo) and `currency` (Frankfurter). In the cloud, Luna loads those tool groups from it; checked in the runtime logs (`weather___getForecast`, `currency___convertCurrency`) and in agency mode.
- Workarounds for CLI 1.0.1, the header redirect, the `daily=daily` bug and the UTC date are in [levels.md § The Gateway](levels.md#the-gateway-tools-as-a-shared-service).

**Claude API in the cloud (optional):** store the key with `agentcore add credentials api-key` and read it through AgentCore Identity (`@requires_api_key`), never as an environment variable.

### 6. Talk prep

Added 2026-11-01: two sample businesses (winery, coffee shop) with presets, business files and documents; scenes for many MCP sources, files + RAG, and an agency "Monday briefing" that saves a report; [plain-words.md](plain-words.md) and [production.md](production.md). `rehearse.py` covers 11 scenes, all passing.

The demo is rehearsed and scripted: [demo-runbook.md](demo-runbook.md) and `python rehearse.py` (all 9 scenes pass, 2026-10-31).

Still open (see [agenda.md](agenda.md)):
- set the date and venue
- review the deck ([slides/](slides/), English, built by `build.js`) and add the recorded clips to the demo slides
- record the demo, one clip per scene; decide whether the talk runs live or from the recording
- if anything runs live, rehearse on the venue network

## Things to know

- **Rules followed so far:** one sandbox AWS account, **us-east-1** only. No AWS resource is created without an explicit decision. Read-only checks are fine.
- **Models:** Claude Haiku 4.5 for Luna and the specialists, Sonnet 4.6 for the Director, through the `global.` profiles (the `us.` ones cost 10% more). The 5.5 models are one setting away once the account has quota; see [bedrock-access.md](bedrock-access.md).
- **Embeddings:** Amazon Titan Text Embeddings V2 (Amazon's own model, so no Marketplace agreement is needed).
- **Vector store:** S3 Vectors. Avoid OpenSearch Serverless, which costs about $175–350 a month even when idle.
- **Agency roster:** a specialist whose tools are off sits out. `researcher` needs at least one of its MCP servers enabled, and `librarian` needs the knowledge base.
- **Diagrams:**
  - Mermaid blocks live in the docs. Render them one at a time with `mmdc` to validate; batch runs failed on the original machine.
  - The AWS-icon PNGs are generated from `docs/diagrams/*.py` with the Python `diagrams` package (`pip install diagrams`, plus graphviz).
  - The Knowledge Base, S3 Vectors and AgentCore Gateway have no official icon yet, so the closest official icon is used and labelled.
- **Prices** were taken from the AWS Price List API on 2026-10-31. Re-check them before the talk.
