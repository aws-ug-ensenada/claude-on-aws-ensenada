# Demo runbook

How to rehearse, record and run the live demo for the talk. The scenes follow [agenda.md](agenda.md). Every command runs from `assistant/` with the virtual environment active and your AWS account's credentials loaded (us-east-1).

## The day before

The full list, with the checks and a log to fill in, is in [talk-checklist.md](talk-checklist.md). In short:

1. **Check access and resources:**
   ```bash
   python rehearse.py            # every scene once, with checks; about 6 minutes and $0.25 on Claude 4.x
   ```
   It ends with `✅ Ready for the talk`, or names the scenes that failed and shows their output. `python rehearse.py agent rag` runs only those scenes; `--list` shows them all.
2. **Seed the memory scene.** Memory needs a few minutes to learn a preference, so do this at least 5 minutes before you show it:
   ```bash
   python luna.py --ask "Remember this about me: I'm vegetarian and I hate cold weather."
   ```
3. **Clear what the audience should see appear on stage:** `rm -f data/todo.json business/*/reports/*.md`.
4. **Check the model.** The presenter's machine runs Claude 5.5 through the **Claude API** (`model` and `agency.director.model` in `config.local.yaml`, with `ANTHROPIC_API_KEY` set), because Bedrock holds Claude 5.x back on the presenter's account ([bedrock-access.md](bedrock-access.md)). The guardrail still applies to what you type. The cloud scene runs Claude 4.x on Bedrock.
5. **Check the AgentCore CLI** for the cloud scene: `agentcore --version` (install it once with `npm install -g @aws/agentcore`; everything else the demo needs is in [prerequisites.md](prerequisites.md)).
6. **Record the fallback video** (next section).

## Record the demo

A recording replaces the live demo if the venue network fails. It can also *be* the demo: play the clips and narrate over them.

- **One clip per scene,** not one long take, so a bad take only costs that scene and the clips can sit on their slides.
- **Terminal:** dark theme, font size 20 or larger, about 100 × 30 characters, a short prompt (`PS1='❯ '`). Run `clear` between scenes.
- **Tools:** [asciinema](https://asciinema.org) records the terminal as text (small files, sharp at any size, the text can be copied). OBS Studio records the screen and your voice if you want a narrated video. Either works for a fallback.
- **Answers vary** a little from run to run. Keep the take where the answer reads best.

## Scenes

Each scene has a slide in [the deck](slides/claude-on-aws-ensenada.pptx) with the command, what to watch for, and the clip name below (`clips/01-chatbot` and so on). Name the recordings to match. `rehearse.py` runs every scene except 3 (the approval needs someone at the keyboard) with the same questions.

| # | Minute | Scene | Command | What the audience should see | If it fails |
|---|---|---|---|---|---|
| 1 | 10–14 | Chatbot | `python luna.py --no-tools`, then *"What should I wear today?"* | It guesses: no tools, no real weather | It only needs the model |
| 2 | 14–20 | Agent | `python luna.py`, then *"What should I wear today, and how much is 85 dollars in pesos? Add 'buy sunscreen' to my list."* | `get_weather`, `convert_currency`, `add_task`; real numbers; the cost line | Weather or rates API down → play the clip |
| 3 | 14–20 | Human in the loop | *"Delete the sunscreen task"* | Luna asks for approval before deleting | — |
| 4 | 20–23 | Make it yours | `python luna.py --preset family`, or `--set assistant.personality=pirate`, or a suggestion from the room | Same agent, new name, voice and model | — |
| 5 | 23–27 | Agency | `python luna.py --mode agency`, then *"Plan my Saturday at the beach, budget 50 USD"* | The Director's orders (📨) and the specialists' replies (✅), cost per agent | Slow (about 20 s): talk over the orders |
| 6 | 27–30 | Many sources (MCP) | `python luna.py --preset winery`, then *"What time is it in Los Angeles right now? Then read https://en.wikipedia.org/wiki/Valle_de_Guadalupe and give me two facts I can tell my US guests."* | `get_current_time` and `fetch`: two MCP servers, one answer | Site slow → any other public page |
| 7 | 30–32 | Your business | `python luna.py --preset coffee-shop`, then *"What do I need to reorder this week, and from which supplier is espresso cheaper?"* | The `files` server reads `inventory.csv`; RAG finds the supplier prices; one answer from both | — |
| 7b | 32–33 | Any business (a clinic) | `python luna.py --preset clinic`, then *"A patient cancelled a cleaning with only 5 hours' notice. Is there a fee? And which patient on 16 November has an allergy the dentists should know about?"* | The same agent, a third kind of business: it reads `appointments.csv` and searches the clinic's policies (20% fee, penicillin allergy). Nothing in the code changed, only a preset and data | Run `python luna.py --preset clinic` once beforehand; the documents must be synced (`create_knowledge_base.py --sync`) |
| 8 | 32–35 | Monday briefing (advanced) | `python luna.py --preset winery --mode agency`, then *"Prepare my Monday briefing: will the patio be usable this coming weekend, how last weekend's sales compared with the weekend before, next Saturday's reservations and allergies, what 100 dollars is in pesos for US guests, and which cork supplier to use. Save it as a report."* | Orders to six specialists; then open `business/winery/reports/` and show the saved file | About 45 s: narrate the orders; or show a report saved in rehearsal |
| 9 | 38–42 | Guardrail | *"Should I buy bitcoin with my savings?"* | The guardrail's refusal, before Claude sees it | — |
| 10 | 38–42 | Memory | *"Suggest a dinner for tonight based on what you know about me."* | It knows you're vegetarian, from an earlier session | Not seeded → skip, or show the clip |
| 11 | 38–42 | Your documents | *"According to my lease, when is the rent due and how much is it?"* | `search_my_documents`, then 9,500 MXN by the 5th: an English question answered from a Spanish contract | — |
| 12 | 38–42 | Cloud | From the repo root: `agentcore invoke --runtime luna --payload '{"prompt": "What should I wear today in Ensenada?"}'` | The same agent answering from AgentCore Runtime, with weather through the Gateway | Show the clip or the CloudWatch trace |

Scenes 6 to 8, with 7b, are the business block: the part most people will want to copy, so give it time. Scenes 9–12 are about 30 seconds each; pick the ones the room cares about most.

Explaining the concepts to a non-technical room: [plain-words.md](plain-words.md).

## Rehearsing on a second machine

Checked on a second, low-power Linux machine on 2026-11-14 (Claude 4.x on Bedrock, no Claude API key). Things that only show up on a fresh machine:

- **`config.local.yaml` is git-ignored,** so copy it across or recreate it from the IDs in [next-steps.md](next-steps.md). Without it the guardrail, memory and documents scenes silently run without those features.
- **The first run of scene 6 (MCP) is slow, about 3 minutes.** `uvx` downloads the `time` and `fetch` servers, and `fetch` runs `npm install` for its Readability dependencies on first use. Run the scene once the day before; killing it half-way throws the install away. Later runs take about 40 seconds.
- **`agentcore invoke` needs the project's deployment state,** which is git-ignored and lives on the machine that ran `agentcore deploy`. On another machine it says *No deployment targets are configured*. Do not run `agentcore deploy` to fix that; call the runtime directly instead:
  ```bash
  ARN=$(aws bedrock-agentcore-control list-agent-runtimes --query "agentRuntimes[0].agentRuntimeArn" --output text)
  aws bedrock-agentcore invoke-agent-runtime --agent-runtime-arn $ARN \
    --runtime-session-id rehearsal-session-0000000000000000001 \
    --payload '{"prompt": "What should I wear today in Ensenada?"}' \
    --cli-binary-format raw-in-base64-out out.json && cat out.json
  ```
- **Refresh the winery's sample dates before the briefing scene:** `python setup/refresh_sample_dates.py` slides its sales and reservations (in whole weeks) so "last weekend" and "next Saturday" have data, and `setup/prewarm.py` warns when they are stale. Without it the briefing reports a data gap, and the rehearsal now fails on that. Put the original dates back with `git checkout -- assistant/business/winery` and never commit the shifted files.
- **The sample data has fixed dates (16 to 18 November 2026) for the clinic.** Luna's prompt says what today is, so a question that says "Monday" or "this week" changes meaning with the real date, and the answer can pick the wrong day. The demo questions name the date ("16 November"). Keep that when you write your own.
- **A small model can misread a rule.** Haiku once answered that a 5-hour cancellation is free, against a policy that says under 24 hours is charged. The policy now includes a worked example, which made the answer stable. When an answer has to be right on stage, put an example next to the rule in the document.
- **Memory can trip the guardrail.** With the memory switched on, scene 6's prompt was refused by the guardrail before Claude saw it (no tool calls, $0.00), after memory had collected preferences from earlier scenes. The same prompt works with memory off or the guardrail off, and the prompt alone passes `apply-guardrail`. On 2026-11-14 the fix was to delete the stray records (a budget, an email-summary rule, a briefing preference) and keep only *vegetarian* and *hates cold*; scene 6 then passed with everything on. Memory re-learns preferences from every conversation, so before the talk list the records with `python setup/clean_memory.py`, delete the extras with `python setup/clean_memory.py --keep vegetarian --keep cold --yes` (without `--yes` it only shows what would go), and run scene 6 once more. `rehearse.py` also warns at the start when the memory holds more than 3 records. If it is refused on the day, run it with `--set memory.enabled=false`.

## Time budget

The talk is 45 minutes plus questions. The demo is about 20 of them, so not every scene fits live. Machine times below were measured on 2026-11-14 on a low-power Linux machine with Claude 4.x (`python rehearse.py`); add 30 to 60 seconds of talking per scene.

| Group | Scene | Machine time | Role |
|---|---|---|---|
| **Must show** | 1 Chatbot | 9 s | the "before" |
| | 2 Agent | 12 s | tools, the main idea |
| | 5 Agency | 19 s | a team of agents |
| | 7 Business (coffee shop) | 38 s | files plus documents |
| | 7b Clinic, or **an audience-built business** | 23 s | "any business" |
| | 9 Guardrail | 5 s | rules |
| | 12 Cloud | about 15 s | the same agent on AWS |
| If time allows | 3 Approval, 4 Make it yours | 7 to 15 s | |
| | 6 MCP (time and web page) | 40 s warm | |
| | 10 Memory, 11 Your documents | 5 to 8 s | |
| | 8 Monday briefing | 58 s | the long one: clip is fine |
| | Spanish question | 50 s | shows language is not a barrier |

The deck's speaker notes carry a planned time per slide (`node build.js` prints 49.5 minutes with every slide and 37.5 without the optional ones; replace the estimates in `TIMING` in `docs/slides/build.js` with your timed run). The slide-by-slide script is in [presenter-script.md](presenter-script.md).

Add these up with your own talking time in the first full rehearsal, and write the total in [talk-checklist.md](talk-checklist.md). The must-show set is what you run if you are over time.

## Audience builds a business

The best proof that Luna works for any business is to build one for someone in the room, live. Ask *"What business do you have or work in?"* and take the first answer that has files and rules (a bakery, a gym, a repair shop, a school).

1. `python setup/new_preset.py bakery --business "Panadería Sol" --about "Owns a bakery; busiest on weekends"` (seconds; it creates the preset and a folder, then checks it).
2. Open `business/bakery/data.csv` and type or paste 4 to 6 rows the audience gives you (item, quantity, what they sell).
3. `python luna.py --preset bakery --check`, then `python luna.py --preset bakery` and ask one question about those rows.

Keep it to one question. If anything goes wrong, say *"this is why we check it"*, show the `--check` output, and switch to one of the two spare presets (see [talk-checklist.md](talk-checklist.md#2-the-day-before)). Small models can miscount rows, so ask for a list or a lookup, not a total.

## AWS console tour

If the room has time, a 3-minute tour of the console makes the cloud part concrete. All of these exist in the personal account, us-east-1, and were checked READY or ACTIVE on 2026-11-14.

1. **Bedrock → Guardrails → `luna-assistant`:** the denied topic and the prompt-attack filter. Goes with scene 9.
2. **AgentCore → Memory → `luna_assistant`:** the records it learned (*vegetarian*, *hates cold*). Goes with scene 10.
3. **Bedrock → Knowledge Bases:** the data source and its sync status. Goes with scenes 7 and 11.
4. **AgentCore → Runtime and Gateway:** the targets `weather` and `currency`, and the runtime's CloudWatch logs and traces. Goes with scene 12.
5. **Billing or Budgets:** the monthly budget, to answer "what does it cost".

## Plan B for the model

- **The Claude API is slow or failing:** run the same scene on Bedrock with `--set model.provider=bedrock --set model.id=global.anthropic.claude-haiku-4-5-20251001-v1:0 --set agency.director.model=global.anthropic.claude-sonnet-4-6`.
- **Bedrock is failing (guardrail, memory, documents):** those scenes need AWS; play their clips.
- **No network at all:** play the recorded clips.

## After the talk

```bash
python setup/cleanup.py                                  # guardrail, memory, knowledge base
cd .. && agentcore remove all --yes && agentcore deploy --yes   # runtime, gateway, placeholder key
aws xray update-indexing-rule --name Default --rule '{"Probabilistic":{"DesiredSamplingPercentage":1}}'
```
