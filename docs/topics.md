# Topic shortlist — AWS + Claude + AI

Researched on 2026-10-31. Items marked **(verify)** come only from secondary sources; confirm against AWS or Anthropic docs before putting them on a slide. Re-check everything the week of the talk — re:Invent (Nov 30 – Dec 4, 2026) will change this list.

Audience key: 🟢 non-technical · 🎓 students · 🛠️ engineers

## 1. From chatbots to agents 🟢🎓🛠️

The framing for the whole talk. A chatbot answers; an agent plans, calls tools, checks the result and keeps going. The concepts the rest of the talk builds on:

- **Tools / MCP (Model Context Protocol)** — the open standard for plugging an AI model into systems (databases, APIs, AWS itself). "USB-C for AI."
- **Agent Skills** — packaged instructions + scripts an agent loads only when a task needs them.
- **Guardrails and human-in-the-loop** — how you stop an agent from doing something it shouldn't.

## 2. Two ways to use Claude on AWS 🛠️

- **Amazon Bedrock** — AWS runs inference; IAM, VPC endpoints, CloudTrail, data stays in your account boundary.
- **Claude Platform on AWS** — Anthropic-operated, billed through AWS Marketplace; gets the full Anthropic feature set first (Agent Skills, code execution, MCP connector, betas). **(verify GA status and feature list)**

Good slide: a decision tree — compliance/data residency → Bedrock; newest Anthropic features → Claude Platform on AWS.

Sources: [Claude Platform on AWS docs](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) · [Decision tree](https://kane.mx/posts/2026/claude-platform-on-aws-vs-bedrock/) · [Cost comparison](https://www.cloudzero.com/blog/claude-on-aws-bedrock/)

## 3. Claude models on Bedrock in 2026 🟢🛠️

- Feb — Claude Opus 4.6 + structured outputs. [AWS roundup](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-claude-opus-4-6-in-amazon-bedrock-aws-builder-id-sign-in-with-apple-and-more-february-9-2026/)
- Apr — Claude Opus 4.7, 1M-token context. [AWS blog](https://aws.amazon.com/blogs/aws/introducing-anthropics-claude-opus-4-7-model-in-amazon-bedrock/)
- Apr — **Claude Mythos Preview**, gated research preview (Project Glasswing), us-east-1 only. Good story for "AI and cybersecurity." [What's New](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-bedrock-claude-mythos/)
- Sep — Opus 5 / Sonnet 5 expand to India, South Korea, Singapore with in-country inference. [What's New](https://aws.amazon.com/about-aws/whats-new/2026/09/claude-region-expansion-in-sk/)
- Sep — Opus 5.5 / Sonnet 5.5 on GovCloud. **(verify)** [Unite.ai](https://www.unite.ai/aws-details-claude-code-deployment-on-amazon-bedrock-in-govcloud-us/)
- **To check for this talk:** which Claude models are callable from **mx-central-1** (Mexico) or via cross-region inference — a local angle the audience will care about.

## 4. Claude Code, Desktop and Cowork on Bedrock 🟢🛠️

Since June 2026 Claude Desktop (chat, **Cowork**, Claude Code) can run against Amazon Bedrock directly or through an LLM gateway. Cowork is the non-technical hook: an agent that works on documents and files for knowledge workers, not just code.

Sources: [AWS ML blog](https://aws.amazon.com/blogs/machine-learning/from-developer-desks-to-the-whole-organization-running-claude-cowork-in-amazon-bedrock/) · [Claude Code + Desktop on Bedrock](https://dev.to/haowen_huang/running-claude-code-and-claude-desktop-on-amazon-bedrock-1ed2)

## 5. Agent Toolkit for AWS (AWS MCP server + skills) 🛠️🎓

An AWS MCP server plus agent skills that install into Claude Code / Claude Desktop, so you can ask in plain language to build, deploy and inspect AWS resources. Strong live-demo candidate.

Sources: [AWS roundup, May 11](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-amazon-bedrock-agentcore-payments-agent-toolkit-for-aws-and-more-may-11-2026/) · [re:Post guide](https://repost.aws/articles/ARv3qnC_gLTQKJb9-YUlwsrw/use-claude-desktop-and-claude-code-with-agent-toolkit-for-aws-to-build-deploy-and-manage-your-aws-environment)

## 6. Amazon Bedrock AgentCore — running agents in production 🛠️

The "where does my agent live" answer. 2026 timeline:

| When | What |
|---|---|
| Apr | Managed harness (preview): define model + prompt + tools, no orchestration code; AgentCore CLI; skills for coding assistants |
| May | Payments (preview) with Coinbase / Stripe wallets and spend limits |
| Jun | Optimization: clusters production traces to find recurring failures |
| Jul 30 | Original Bedrock Agents renamed **Bedrock Agents Classic**, closed to new customers |
| Aug | Runtime instances GA — agents on EC2, sessions up to 14 days |
| Sep | Runtime V2 — ~2 s cold starts regardless of image size; Identity consent portal for OAuth (GitHub, Slack, Salesforce) |
| Oct 28 | **AgentCore CLI 1.0** GA |

Sources: [Apr features](https://aws.amazon.com/about-aws/whats-new/2026/04/agentcore-new-features-to-build-agents-faster/) · [Jun optimization](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-agentcore-new-optimization-capabilities/) · [Aug instances](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-bedrock-agentcore-runtime-instances-generally-available/) · [Runtime V2](https://aws-news.com/article/2026-09-18-the-new-agentcore-runtime-is-now-available-in-amazon-bedrock-agentcore) · [CLI 1.0](https://aws-news.com/article/2026-10-28-amazon-bedrock-agentcore-cli-version-10-is-now-available) · [Evaluations + policy](https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/)

## 7. Strands Agents — open-source agent SDK 🎓🛠️

Apache 2.0 SDK from AWS (used internally by Kiro, Amazon Q, Glue). MCP support built in, A2A (agent-to-agent) for multi-agent setups. A working agent is ~10 lines of Python — good for students.

Sources: [Open protocols with Strands](https://aws.amazon.com/blogs/opensource/open-protocols-with-the-strands-agents-sdk/) · [Technical deep dive](https://aws.amazon.com/blogs/machine-learning/amazon-strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability)

Alternative: [Claude Agent SDK with Skills on Bedrock](https://builder.aws.com/content/3AC38DtkrFlNL0p076gVNPzSHuw/running-claude-agent-sdk-with-skills-on-amazon-bedrock) and [deployed on AgentCore](https://pub.towardsai.net/deploying-claude-agent-on-amazon-bedrock-agentcore-dfcf04c29f27).

## 8. Kiro replaces Amazon Q Developer 🎓🛠️

Spec-driven agentic IDE. Q Developer: new sign-ups blocked from May 15, 2026; IDE plugins end support Apr 30, 2027. Code-modernization work moves to **AWS Transform**. Interesting debate topic: "spec-first vs vibe coding." **(verify dates — third-party sources)**

Sources: [Kiro developer guide](https://www.developersdigest.tech/blog/aws-kiro-developer-guide-2026) · [Q → Kiro migration](https://www.digitalapplied.com/blog/amazon-q-to-kiro-migration-playbook) · [DZone comparison](https://dzone.com/articles/amazon-kiro-vs-amazon-q-developer-which-ai-coding)

## 9. AWS DevOps Agent (callback to April) 🛠️

GA on March 31, 2026 as its own service. Use it as a callback to the April session: "last time an agent fixed our cluster; today we build our own."

## 10. Cost and governance 🛠️🟢

- Bedrock now attributes inference cost to the IAM principal that made the call (Apr 2026) — answers "who spent the money."
- Bedrock RPM quotas removed (May 2026).
- Talking point for non-technical folks: agents are billed per token, so a runaway agent is a runaway bill — budgets, guardrails, human approval.

Source: [AWS roundup, Apr 13](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-claude-mythos-preview-in-amazon-bedrock-aws-agent-registry-and-more-april-13-2026/) · [AWS roundup, Apr 20](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-claude-opus-4-7-in-amazon-bedrock-aws-interconnect-ga-and-more-april-20-2026/)

## 11. How students start for free 🎓

- Verified students: 1 year of AWS Skill Builder at no cost; "Generative AI essentials" covers prompting and Bedrock. [Builder Center — students](https://builder.aws.com/learn/students)
- **PartyRock** — no-code generative AI app builder, no AWS account needed. The usual on-ramp before Bedrock and Kiro. [AWS blog](https://aws.amazon.com/blogs/aws/build-ai-apps-with-partyrock-and-amazon-bedrock)
- Free Tier credits ($200) are the reliable credit source; AWS Educate has no guaranteed credits. Set a $1 billing alarm before touching Bedrock. [What's actually available in 2026](https://builder.aws.com/content/3J0F6sCj6NWuOC3jqP6ZYMRyxrc/aws-educate-and-free-credit-programs-for-students-whats-actually-available-in-2026) · [Free Tier projects](https://builder.aws.com/learn/topics/free-tier-projects)

## 12. What's next: re:Invent 2026 🟢🎓🛠️

Nov 30 – Dec 4, Las Vegas. CEO keynote Tue Dec 1, 8:30 PT — "the agentic era." Close the talk with "what to watch for," or hold a recap session afterwards.

Source: [APN — know before you go](https://aws.amazon.com/blogs/apn/know-before-you-go-an-aws-partners-guide-to-reinvent-2026/)
