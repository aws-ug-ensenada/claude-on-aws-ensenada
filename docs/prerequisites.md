# Prerequisites

What you need before you start, per level. Level 1 needs only the first block. Add the rest as you go up.

## Software on your machine

| Tool | Version | Needed for | Install |
|---|---|---|---|
| Git | any | Cloning the repo | [git-scm.com](https://git-scm.com/downloads) |
| Python | 3.11 or newer | Everything (Luna, the setup scripts, `rehearse.py`) | [python.org](https://www.python.org/downloads/), or your package manager |
| AWS CLI | v2 | Signing in (`aws configure` / `aws sso login`) and checking which account you're in | [AWS CLI install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| [uv](https://docs.astral.sh/uv/) | any recent | Level 4 and up: runs the Python MCP servers (`uvx`) and builds the level 8 package | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 20.12 or newer | Level 4 and up: the `files` MCP server (`npx`), and `fetch` uses it to clean up web pages. Level 8: the AgentCore CLI and CDK | [nodejs.org](https://nodejs.org/) (LTS) |
| AgentCore CLI | 1.0.1 (tested) | Level 8: deploys to AgentCore Runtime | `npm install -g @aws/agentcore` |

Tested on 2026-11-01 on Linux (WSL2) with Python 3.15, uv 0.13, Node.js 24, AWS CLI 2.34 and AgentCore CLI 1.0.1. macOS works the same way. On Windows, use WSL.

Only to rebuild the slides or diagrams, not to run Luna:

| Tool | For |
|---|---|
| Node.js | `docs/slides/build.js` (`npm install && node build.js`) |
| LibreOffice Impress, poppler-utils, `fonts-crosextra-carlito`, `fonts-crosextra-caladea` | Previewing the deck as PDF or PNG with the same text metrics as PowerPoint |
| Python `diagrams` package and Graphviz | Regenerating the AWS-icon PNGs in `docs/diagrams/` |

## An AWS account

- **An account you're allowed to experiment in.** A personal or sandbox account is best: levels 2, 3, 5 and 8 create resources.
- **Credentials on your machine**, from `aws configure` (access keys) or `aws sso login` (IAM Identity Center). Check with `aws sts get-caller-identity`.
- **Region us-east-1** by default (`aws.region` in `config.yaml`). Another region works if it offers the models and services below.
- **Permissions:** level 1 only needs to call Bedrock models (`bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`). The setup scripts and level 8 create guardrails, AgentCore resources, S3 buckets, S3 Vectors indexes, IAM roles and CloudFormation stacks, so use an administrator role in a sandbox account for those.
- **An AWS Budget with an alert**, for example $20 a month. The whole talk costs about $10 ([costs.md](costs.md)).

### Models in Amazon Bedrock

| Model | For | How to get it |
|---|---|---|
| Claude Haiku 4.5 | Luna's default brain | One time per account: open it in the Bedrock playground and submit Anthropic's use-case form ([bedrock-access.md](bedrock-access.md)) |
| Claude Sonnet 4.6 | The Director in agency mode (level 6), and the `professional` preset | Same form; nothing more to do |
| Amazon Titan Text Embeddings V2 | Level 5, your documents (RAG) | Available by default |
| Claude 5.5 (optional) | Newer and cheaper | Many accounts start with a quota of 0. See [bedrock-access.md](bedrock-access.md) for the quotas to request |

## Optional

| What | For | Where |
|---|---|---|
| A Claude API key | Using Claude 5.5 right away, without Bedrock quotas (`model.provider=anthropic`) | [Claude Console](https://platform.claude.com) → API keys. A Claude.ai subscription doesn't include one. Keep it in an environment variable, never in a file in the repo |
| A Google OAuth client (Desktop app) | The `gmail` MCP server | [customize.md § 7](customize.md#gmail) |
| Internet access | Weather, exchange rates, the `fetch` server and every model call | — |

## Check your machine

From the repo root:

```bash
git --version && python3 --version && aws --version   # level 1
uv --version && node --version                        # level 4 and up
agentcore --version                                   # level 8
aws sts get-caller-identity                           # the account you're signed in to
```

Then follow the [Quickstart](../README.md#quickstart-level-1-about-15-minutes). Once Luna is installed, `python setup/check_mcp.py` starts every MCP server without calling Claude (level 4), and `python rehearse.py` runs the whole demo with checks. A scene whose setup is missing is skipped and the reason is printed, so you can see what's still to do.
