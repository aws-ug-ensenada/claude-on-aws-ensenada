# Cost breakdown

Prices are AWS list prices for **us-east-1**, checked on **2026-10-31**. Sources are listed at the end. Prices change, so check the pricing pages before you rely on these numbers. The assistant prints the **actual** tokens and cost after every answer (`show_cost: true`).

## TL;DR

- Levels 1–7 on a laptop have **no fixed monthly cost**. You pay only for the model tokens you use, which is cents per session.
- Guardrails, Memory, the knowledge base and Gateway are **pay per use** and have no monthly fee. The documents for RAG cost cents a month to store.
- Level 8 (cloud) adds pay-per-second hosting and a few cents of storage and logs.
- **The whole talk** (rehearsals plus about 300 questions, mostly in agency mode) comes to an estimated **$7–12** on the default Claude 4.x models, and about a third of that on Claude 5.5.

## 1. Claude models on Amazon Bedrock

USD per 1 million tokens, on-demand, standard tier.

| Model | Input | Output | Best for |
|---|---|---|---|
| Claude Haiku 4.5 | $1.00 | $5.00 | **Default**: fast, good with tools |
| Claude Sonnet 4.6 | $3.00 | $15.00 | **Default Director**, harder reasoning |
| Claude Haiku 5.5 | $0.10 | $0.50 | Newest; needs quota on your account |
| Claude Sonnet 5.5 | $2.00 | $10.00 | Newest; needs quota on your account |
| Claude Opus 5.5 | $4.00 | $20.00 | Hardest problems; needs quota on your account |

Luna defaults to the 4.x models because the 5.5 models often start with a 0 quota on new accounts, and AWS may not raise it yet (see [bedrock-access.md](bedrock-access.md)). Once your account has quota for 5.5, switching is one line in `config.yaml`, and Haiku gets 10× cheaper.

- These prices are for the `global.` cross-region profiles. The `us.` profiles keep processing in the US and cost **10% more**.
- Haiku 5.5 prices apply to prompts up to 100k tokens. Longer prompts cost 5× more.
- Prompt caching, the Batch API and reserved throughput lower these prices but aren't used here.
- With your own Claude API key (`provider: anthropic`), Anthropic's list prices are the same as the `global.` column.

## 2. What one answer costs (estimates)

**Assumptions:**
- An answer that uses tools takes 2 model calls: one to decide which tool to use, one to write the answer.
- Each call sends the instructions, the tool descriptions and the conversation so far. That adds up to about **5,500 input tokens and 350 output tokens** per answer.
- In agency mode, the Director makes 2–3 calls and each specialist it orders makes about 2.

| Setup | Model calls | ≈ Cost per answer |
|---|---|---|
| Setup | Model calls | ≈ Cost on 4.x (default) | ≈ Cost on 5.5 |
|---|---|---|---|
| Solo, Haiku | 2 | **$0.007** | $0.0007 |
| Solo, Sonnet | 2 | $0.022 | $0.015 |
| Solo, Opus 5.5 | 2 | — | $0.029 |
| Agency: Sonnet Director + 2 Haiku specialists | 6–7 | **$0.045** | $0.022 |
| Agency, everything on Sonnet | 6–7 | $0.07 | $0.04 |

**1,000 answers** cost about **$7** with solo Haiku 4.5 (or $0.70 on Haiku 5.5) and about **$45** with a Sonnet-led agency on 4.x. Picking the right model per agent is the biggest cost lever.

**Measured on 2026-10-31** (Claude 4.x, the cost line Luna prints): a solo answer with two tools used 2,789 input and 256 output tokens, about **$0.004**. An agency answer with three specialists came to about **$0.022**. Both are below the estimates above, because the estimate assumes a longer conversation.

## 3. Optional AWS services

| Level | Service | Price | ≈ Per answer |
|---|---|---|---|
| 2 | **Bedrock Guardrails** | Content filters $0.15, denied topics $0.15, personal-data filter $0.10, each per 1,000 text units (1 unit = up to 1,000 characters) | ~$0.0008 (input and output each checked once) |
| 3 | **AgentCore Memory** | Short-term: ingestion $1.00/GB (12 KB minimum per event), retrieval $0.20/GB, storage $0.10/GB-month. Long-term: $0.75 per 1,000 records/month, $0.50 per 1,000 retrievals | ~$0.0006 |
| 5 | **Bedrock Knowledge Bases** | No charge for the knowledge base or searches; you pay for the parts below | $0 |
| 5 | **Titan Text Embeddings V2** | $0.02 per 1M tokens (documents once at indexing, plus each search question) | ~$0.0000002 |
| 5 | **Amazon S3 Vectors** | Storage $0.06/GB-month; uploads $0.20/GB; queries $2.50 per 1M plus $0.004/TB processed | ~$0.0000025 |
| 5 | **Retrieved passages sent to Claude** | ~1,200 extra input tokens per search (4 passages of ~300 tokens) | Haiku ~$0.00012 · Sonnet ~$0.0024 |
| 8 | **AgentCore Runtime** | $0.1276 per vCPU-hour + $0.0169 per GB-hour, billed per second. CPU isn't billed while waiting on the model | ~$0.0002 |
| 8 | **AgentCore Gateway** (MCP) | $0.005 per 1,000 tool calls; search $0.025 per 1,000; indexing $0.02 per 100 tools/month | ~$0.00001 |
| 8 | **AgentCore Identity** | $0.010 per 1,000 token requests; free when used through Runtime or Gateway. The placeholder API key for the Gateway is one Secrets Manager secret: **$0.40 a month** | $0 |
| 8 | **Observability** | CloudWatch rates (example: ~$0.35/GB of trace spans, ~$0.50/GB of logs) | pennies per month |
| 8 | **CDK bootstrap and deploy artifacts** (S3) | S3 storage | pennies per month |

**RAG in practice:** 100 pages of documents are about 50,000 tokens. Indexing them costs **$0.001** and storing their ~200 vectors costs well under **$0.01 a month**. The biggest cost of a search is the extra text Claude reads, not the search itself.

**Why not OpenSearch Serverless?** It's the vector store the console suggests by default, but it bills compute at **$0.24 per OCU-hour** even when idle. The smallest setup is 1–2 OCUs, about **$175–350 a month**. For a personal knowledge base with occasional questions, S3 Vectors costs cents.

## 4. Free and open-source parts

| Component | Cost |
|---|---|
| Strands Agents, MCP, A2A protocol, OpenTelemetry | $0 (open source) |
| Open-Meteo (weather) | $0, free for **non-commercial** use, up to 10,000 calls a day |
| Frankfurter (currency rates) | $0, no key needed |
| Bedrock model agreement / Marketplace subscription | $0; you pay only for tokens |

## 5. Budget for the talk

| Item | Assumption | ≈ Cost |
|---|---|---|
| Rehearsals | 3 full runs × 50 answers, agency mode, Claude 4.x | $3.30–6.75 |
| Live demo | ~100 questions from the room, mixed, Claude 4.x | $2–4 |
| Guardrails + Memory during demo | 250 answers | $0.35 |
| Knowledge base for one week | 3 sample files, ~100 searches | < $0.05 |
| Cloud level (Runtime, logs, S3) for one week | Light use | < $1 |
| **Total** | | **$7–12** (about a third of that on Claude 5.5) |

Before you start, **set an AWS Budget alarm** on the account: $10 is a sensible level for 5.5, $20 for 4.x. The budget counts everything in the account, not only this project. Afterwards, clean up with `python setup/cleanup.py` (guardrail, memory, knowledge base) and `agentcore remove all --yes && agentcore deploy --yes`.

## Sources

- AWS Price List API, us-east-1, queried 2026-10-31: `AmazonBedrockFoundationModels` (Claude), `AmazonBedrock` (Titan Text Embeddings V2, Knowledge Bases), `AmazonS3` (S3 Vectors), `AmazonES` (OpenSearch Serverless OCU)
- [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) (Guardrails)
- [Amazon Bedrock AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
- [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) (Anthropic API, regional vs global)
- [Open-Meteo terms](https://open-meteo.com/en/terms) · [Frankfurter](https://frankfurter.dev)
