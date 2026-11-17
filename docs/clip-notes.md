# Clip notes

What to say over each scene, live or while a fallback clip plays. The commands and questions are in [demo-runbook.md](demo-runbook.md#record-the-clips-on-a-mac-step-by-step); recording steps are there too.

## Reading the cost line

Explain it once, at scene 2, then just point at it.

```
💲 assistant 4,152→583 tok $0.0007  |  this answer $0.0007 · session $0.0014
```

- **Tokens** are the pieces of text a model reads and writes, roughly ¾ of an English word each.
- **4,152 →** is what Claude *read*: its instructions, the tool descriptions, the conversation so far and the tool results. Most of it is that setup, not the question.
- **→ 583** is what Claude *wrote*: the answer and the tool calls it decided to make.
- **$0.0007** is the price from [pricing.yaml](../assistant/pricing.yaml). Haiku 5.5 is $0.10 per million tokens read and $0.50 per million written: 4,152 × 0.10/M + 583 × 0.50/M ≈ $0.0007.
- **this answer** is the cost of this turn across every agent; **session** is the running total since `luna.py` started.
- **Agency mode** prints one entry per agent (`director … · planner … · finance …`). The Director runs the stronger, pricier model, so it dominates the total.
- **Fleet mode** adds *(specialists bill on their own servers)*: they are separate processes, so their cost is not counted here.
- **A refused question costs $0.0000:** the guardrail stops it before any model runs, so the line shows no agent.

A line for the room: *"The whole demo costs a few cents; a thousand questions like this one cost well under a dollar on the small model."*

## Scene by scene

| Clip | What is happening | Point at |
|---|---|---|
| `01-chatbot` | Same model, no tools. It can only guess the weather from what it learned: a plain chatbot. | "I can't check today's live weather" |
| `02-agent` | Same brain, now with hands: it decides by itself to call three tools and answers with real numbers. Then a risky action (delete) has to be approved: a human in the loop. | the `Tool #` lines; the ⚠️ `[y/N]` |
| `04-make-it-yours` | Same code; one small preset file gives it another personality and language (here a warm family helper in Spanish). Other presets also change the name or the model. | the tone and language, with the same tools |
| `05-agency` | One agent becomes a team. The Director never does the work: it splits the request into orders (📨), specialists work in parallel and reply (✅), and it combines the answers. | 📨 and ✅ lines; the cost per agent |
| `06-many-sources` | MCP is like USB for AI: ready-made servers plug in. One tells the time, another reads a web page; no code was written for either. | `get_current_time`, `fetch`, the `HTTP 200` lines |
| `07-your-business` | A real business question answered from two kinds of data: a spreadsheet read through the files server, and supplier documents searched with RAG. | `read_text_file` and `search_my_documents` |
| `07b-clinic` | A completely different business with no code change, only a preset and its data. It applies the policy's 20% rule and finds the allergy in the appointments. | the fee worked out from the policy; the patient ID |
| `08-monday-briefing` | A weekly report done by a team: weather for the patio, sales from a spreadsheet, reservations and allergies, an exchange rate and a supplier choice from the documents, then saved as a file. It says which figures were checked against the files. | the orders; then open `business/winery/reports/` |
| `09-guardrail` | A rule kept in AWS (Bedrock Guardrails) blocks investment advice before Claude sees the question, so nothing is spent. | the refusal and `$0.0000` |
| `10-memory` | Preferences told in an earlier session (vegetarian, hates the cold) come back in a new one: AgentCore Memory. | the list of preferences it used |
| `11-documents` | A Spanish contract, an English question: it searches the document and cites it. | `search_my_documents` and the file name |
| `12-cloud` | The same agent running on AgentCore Runtime instead of the laptop; tools go through the Gateway and memory still applies. | `statusCode: 200` and the answer |

## If the answer surprises you

- **It answers in Spanish to an English question:** with `language: auto` it follows your message, but a city in a Spanish-speaking country can pull the larger models toward Spanish. Say so; it is a nice moment, not a failure.
- **A tool times out** (weather, rates, a web page): the agent says it couldn't get the data instead of guessing. Point that out, then play the clip.
