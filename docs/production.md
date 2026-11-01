# From the laptop to production

Luna runs on your laptop in 15 minutes. This guide covers what changes when other people depend on it: customers, staff, or a whole company. Level 8 already deploys it to AWS ([levels.md § 8](levels.md#8--cloud-agentcore-runtime-gateway-and-observability)); this is the checklist for turning that deployment into a service you'd trust.

In plain words: the laptop is a home kitchen. Production is a restaurant: same recipes, but now you need a front door, a lock on the pantry, health inspections, and someone watching the bills.

## Where to run it

| Option | Good for | You manage | Notes |
|---|---|---|---|
| **AgentCore Runtime** (what level 8 uses) | Agents, especially long or multi-step ones | Your code and config | Built for agents: one isolated microVM per session, sessions up to 8 hours, pay per second while working, Memory/Gateway/Identity/Observability next to it. **Recommended.** |
| AWS Lambda | Short, simple agents (one or two tool calls) | Code, packaging, timeouts | 15-minute limit; cold starts; MCP servers that run as local processes don't fit well |
| Amazon ECS on Fargate | Teams already running containers | Containers, scaling, networking, load balancer | Most control and most work; always-on cost |
| A managed chat product (Claude for Work, Amazon Q Business) | Internal Q&A over company documents, no custom code | Configuration | Less flexible, nothing to operate |

The rest of this guide assumes AgentCore Runtime.

## What level 8 already gives you

- The agent deployed from the same code (`agentcore deploy`), with its infrastructure in CDK (`agentcore/`)
- Tools shared through the Gateway, called with IAM (no passwords in code)
- The guardrail, memory and knowledge base in your account
- Logs and OpenTelemetry traces in CloudWatch
- Least-privilege IAM for the runtime (`setup/cloud_policy.py`)

## What to add for real users

### 1. A front door

- **Login:** today the runtime accepts only AWS-signed calls, which is right for testing. For people, add a login with Amazon Cognito or your company's identity provider, and configure the runtime's inbound authorizer for JWT (`agentcore add runtime --authorizer-type CUSTOM_JWT`).
- **Where people talk to it:** a web chat, Slack or Microsoft Teams, WhatsApp, or your own app. Each one calls the runtime's endpoint with the user's token. Use the user's ID as the memory actor ID, so each person gets their own memory.

### 2. Secrets and connections

- API keys (the Claude API, a CRM, Gmail) go in **AgentCore Identity** (`agentcore add credentials`), never in environment variables or the code folder.
- Connections that act *for a user*, like reading their Gmail, need OAuth on behalf of that user (AgentCore Identity supports this), not one shared key.

### 3. Rules and safety

- Keep the guardrail, and version it: publish a guardrail version instead of using `DRAFT`, so a change is deliberate.
- Human approval for anything that spends money, sends messages or deletes data.
- Least privilege per agent and per MCP server. The files server, for example, should only see one folder.
- Review which MCP servers you trust: a server runs code and sees what the agent sends it.

### 4. Environments and releases

- At least two targets: `dev` and `prod` (`agentcore/aws-targets.json`), ideally in separate AWS accounts.
- Deploy from CI/CD (GitHub Actions with OIDC into AWS), not from a laptop. Run `rehearse.py`-style checks before each release: they are your regression tests.
- Use runtime endpoints (versions) so you can roll back.

### 5. Watching it

- CloudWatch dashboards and alarms on errors, latency and token usage.
- Traces to see which agent did what when an answer is wrong.
- An AWS Budget with alerts, and per-feature cost tracking (the cost line Luna prints is the same idea).
- Evaluations: AgentCore Evaluations, or a set of real questions with expected answers, run on every change.

### 6. Data

- Decide where data lives (region) and how long memory keeps it (`event_expiry_days`).
- Personal data: the guardrail masks some of it; also review what the knowledge base contains and who can query it.

## A realistic path

| Stage | Who uses it | What you add |
|---|---|---|
| 1. Laptop | You | Nothing: `python luna.py` |
| 2. Cloud, private | You, from anywhere | `agentcore deploy` (level 8) |
| 3. Pilot | Your team or a few customers | Login, a chat front end, AgentCore Identity for keys, a published guardrail version, budget alarms |
| 4. Production | Everyone | Separate prod account, CI/CD, dashboards and alarms, evaluations, runbooks, on-call |

For the sample businesses, stage 3 is already useful: the winery's shift leads ask Luna in Slack for tonight's reservations and allergies; the café's owner gets the Monday briefing by email.
