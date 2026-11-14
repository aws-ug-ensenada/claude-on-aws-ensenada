# Session outline (~45 min + Q&A, 10–20 people)

**Title:** De chatbot a agente: construimos un agente de IA en AWS con Claude
*(From chatbot to agent: building an AI agent on AWS with Claude)*

**Principle:** simple but effective. One idea, **agent = brain + hands + rules**, shown with one assistant that grows on stage. The audience asks the questions out loud.

| Min | Block | On screen | Repo |
|---|---|---|---|
| 0–5 | Hook | Callback to April's DevOps Agent session. "Who has used ChatGPT or Claude? Who has used an *agent*?" | — |
| 5–10 | Concept | Brain + hands + rules; how an agent answers (the loop) | [levels.md](levels.md), [plain-words.md](plain-words.md) |
| 10–14 | **Chatbot** | `luna.py --no-tools`: "What should I wear today?" → it guesses | Level 1 |
| 14–20 | **Agent** | `luna.py`: same question → real weather, USD→MXN, adds to the to-do list; deleting asks first. Cost per answer on screen | Level 1 |
| 20–23 | **Make it yours** | `--preset family` / `--set assistant.personality=…` with an audience suggestion | [customize.md](customize.md) |
| 23–27 | **Agency** | `--mode agency`: "Plan my Saturday at the beach". The Director gives orders; cost per agent | Level 6 |
| 27–35 | **Luna for your business** | A winery and a coffee shop. Many sources through MCP (time + a web page); the café's files + price list in one answer; the winery's Monday briefing by six agents, saved as a report. "Connect your world": Gmail, Drive, Slack… The point: any business, not just wine or coffee; Strands Agents explained; five steps to make it yours | [extend.md](extend.md), [customize.md § 6–7](customize.md#6-make-it-your-business) |
| 35–38 | Chat vs fleet | Pros and cons; "when to use which" | [comparison.md](comparison.md) |
| 38–42 | Rules, memory, documents, cloud | Guardrail, memory, "ask your own lease", the same agent on AgentCore with tools through the Gateway. "What broke while building it" | Levels 2–5, 8 |
| 42–44 | **To production** | Laptop → cloud → pilot → production; what to add for real users | [production.md](production.md) |
| 44–45 | Your turn | Free path: PartyRock → Skill Builder → this repo. Cost: about $10 for the whole talk | [costs.md](costs.md) |
| 45–60 | Q&A | | |

**Slides:** [slides/claude-on-aws-ensenada.pptx](slides/claude-on-aws-ensenada.pptx), in English, one demo slide per scene that works live or with recorded clips. Edit [slides/build.js](slides/build.js) and rebuild rather than editing the .pptx by hand, so the deck stays in step with the code.
To preview without PowerPoint: `soffice --headless --convert-to pdf claude-on-aws-ensenada.pptx`. Install `fonts-crosextra-carlito` and `fonts-crosextra-caladea` first: they have Calibri's and Cambria's metrics, so text fits exactly as it will in PowerPoint.

## Prep

Step by step in [demo-runbook.md](demo-runbook.md).

- [x] Claude access: the presenter runs Claude 5.5 through the Claude API (Bedrock holds 5.x back on the presenter's account); attendees' default is Claude 4.x on Bedrock ([bedrock-access.md](bedrock-access.md))
- [x] AWS Budget alarm ($20, for Claude 4.x)
- [x] Guardrail, memory and knowledge base created; level 8 runtime and gateway deployed (2026-10-31)
- [x] `python rehearse.py`: all 11 scenes pass on Claude 5.5 via the Claude API (2026-11-01)
- [ ] Record the demo, one clip per scene. The clips can *be* the demo (narrated), or the fallback for a live run
- [ ] Rehearse once on the venue network, if any part runs live
- [ ] The day before: `rehearse.py`, seed the memory scene, clear the to-do list

## Open decisions

- [ ] Date and venue
- [ ] Live or recorded demo (recorded is fine; live needs a rehearsal on the venue network)
- [ ] Slide language (title drafted in Spanish; the agent answers in whatever language it's spoken to)
