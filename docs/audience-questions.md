# Questions the audience may ask

Short answers you can say in about 20 seconds, with where the detail lives. They only claim what the repo has measured or documented; for anything else, say "I haven't tested that" and point to the doc. Each answer ends with the doc to open if they want more.

## Cost and access

**How much does this cost to run?**
Cents per answer: about $0.005 with tools and $0.10 for the six-agent Monday briefing, measured on Claude 4.x on Bedrock on 2026-11-15. A full rehearsal of every scene is about $0.25. There is no monthly fee for guardrails, memory, the knowledge base or the gateway; you pay per use. Set an AWS Budget alarm first. → [costs.md](costs.md)

**Which model are you using tonight?**
Say the one you actually run (check the banner line that `luna.py` prints). Claude Haiku 4.5 with a Sonnet 4.6 Director on Bedrock is what works on any new account; Claude 5.5 through the Claude API is the newer option. → [bedrock-access.md](bedrock-access.md)

**Why not Claude 5.5 on Bedrock?**
New accounts often start with a quota of 0 for the 5.5 models, and AWS can decline to raise it until the account has more history. On the personal account used for this talk, the quota requests were closed automatically and the quota stayed 0 on 2026-11-15. The Claude API doesn't have that gate, so Luna supports both. → [bedrock-access.md](bedrock-access.md)

**Bedrock or the Claude API: which should I use?**
Bedrock if your data and billing already live in AWS and you want IAM, CloudWatch and the AgentCore services around it. The Claude API if you want the newest models right away. With the API, the model calls are billed by Anthropic (an AWS Budget doesn't see them), while memory, documents and the guardrail still run in AWS. → [bedrock-access.md](bedrock-access.md#the-claude-api-instead-of-bedrock)

**Can I try it for free?**
PartyRock needs no code and no AWS account. For Luna you need an AWS account and a few cents of Claude usage; see the cost slide. → [README](../README.md)

## How agents work

**What is the difference between a chatbot and an agent?**
A chatbot only answers from what it learned in training. An agent is the same model plus tools (it can look things up and do things) and rules (what it may do). Slide 5; demo scenes 1 and 2. → [plain-words.md](plain-words.md)

**Does the model remember me?**
No. Each call starts empty; the agent sends the model the conversation so far, and AgentCore Memory adds the facts worth keeping across sessions (here, up to five relevant preferences). Memory is not the same as your documents. Slides 10 and 30. → [levels.md](levels.md)

**What is the difference between memory and RAG?**
Memory holds what Luna learned about *you* from conversations. RAG searches *your documents* and puts the matching chunks in front of the model. Different stores, different questions. → [levels.md](levels.md)

**Why does it get counts and sums right?**
Because it doesn't do the arithmetic: a Python tool counts and sums the CSV exactly, and the model reads the result. Models are good with text, not calculators. → [extend.md](extend.md)

**What is MCP, and what is A2A?**
MCP is how an agent gets tools (time, web pages, files, AWS docs). A2A is how agents talk to other agents (the fleet level). Both are open standards. Slide 33. → [plain-words.md](plain-words.md)

**Why a Director and specialists instead of one agent?**
Each specialist gets a narrow job and its own tools, and can use a cheaper model; the Director only gives orders and combines answers. The price is time and cost: the briefing takes about 20 seconds and $0.10. For simple questions, one agent is better. → [comparison.md](comparison.md)

**Can it hallucinate?**
Yes. What lowers the risk is giving it real sources (tools, your documents) and telling it to say when it doesn't know. The Monday briefing reports a data gap instead of inventing numbers; that behaviour is checked in `rehearse.py`. → [plain-words.md](plain-words.md)

## Safety and production

**Is it safe to point at real data?**
Not by default. Use least privilege (the files server sees one folder), keep the guardrail, require human approval for anything that deletes or sends, and review which MCP servers you trust. The demo asks `[y/N]` before it deletes a task. → [production.md](production.md)

**What does the guardrail actually do?**
Bedrock Guardrails check what the user types against the rules you set, such as denied topics, and refuse before the model answers. In the demo a denied topic gets a refusal and costs $0.00. → [levels.md](levels.md)

**Where is my data stored?**
Memory and documents live in your AWS account, in the region you chose (us-east-1 here). With the Claude API, the questions and the context sent for each call go to Anthropic. Decide this before putting customer data in; check the current terms of whichever you use. → [production.md](production.md)

**How would I put this in front of customers?**
Level 8 deploys it to AgentCore Runtime. For real users add a login (Cognito or your identity provider), secrets in AgentCore Identity, a published guardrail version, dev and prod targets, CI/CD, dashboards and budget alarms. → [production.md](production.md)

**Can I use my own business data?**
Yes: copy a preset and a folder under `assistant/business/`, put your CSV files in it and your policy documents in `my_documents/`. A new business takes about a minute with `python setup/new_preset.py <name>`, then fill in the data. → [extend.md](extend.md)

## Tooling

**Why Strands Agents and not something else?**
It's open source from AWS, small enough to read, works with Bedrock and the Claude API, and supports MCP and A2A. Other frameworks would do the same job; the ideas in the talk carry over. → [extend.md](extend.md)

**What is Claude Code, and did it write this?**
Claude Code is Anthropic's coding agent for the terminal. It wrote the code, docs, setup scripts and the deck generator with me, and every step was reviewed, tested and committed. Slide 38.

**What would you do next?**
Run it on your own data, add one MCP server you care about (Gmail, Drive, Slack), and put a human approval step in front of anything that changes something. → [extend.md](extend.md)

## If you don't know

Say "I haven't tested that, so I won't guess", write the question down, and answer it in the repo later (the checklist's last step is to note what the audience asked for).
