# Demo runbook

How to rehearse, record and run the live demo for the talk. The scenes follow [agenda.md](agenda.md). Every command runs from `assistant/` with the virtual environment active and your AWS account's credentials loaded (us-east-1).

## Run the demo yourself, step by step

The same steps work for anyone who clones the repo. Do them in one terminal, in this order.

1. **Go to the project and activate its virtual environment** (made in the README quickstart):
   ```bash
   cd claude-on-aws-ensenada/assistant
   source .venv/bin/activate
   export AWS_PROFILE=<your-profile> AWS_REGION=us-east-1 AWS_PAGER=""   # the account that holds the guardrail, memory and knowledge base; AWS_PAGER="" stops the CLI paging (and hiding) short output
   ```
2. **Put your Claude API key in the environment** (only if you use Claude 5.5 through the API; skip it for Bedrock). Create the key in the [Claude Console](https://platform.claude.com) under **API keys** (choose *Somewhere else* if it asks where your code runs, because Luna reads a key from the environment), with an expiry after the talk, and copy it when it is shown: it is shown once. Keep a copy in your password manager, then load it without echoing it:
   ```bash
   read -rs ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY      # paste the key; it isn't shown
   [ -n "$ANTHROPIC_API_KEY" ] && echo "key set (${#ANTHROPIC_API_KEY} chars)"
   ```
   If you use the 1Password CLI, let `op run` hand the key to a single command instead of exporting it: put `ANTHROPIC_API_KEY=op://<vault>/<item>/credential` in a file outside the repo, then run `op run --env-file <that file> -- python rehearse.py`. To load it for an interactive session instead: `export ANTHROPIC_API_KEY="$(op read 'op://<vault>/<item>/credential')"`. If `op account list` shows more than one account (say work and personal), add `--account <sign-in address>` to `op run` and `op read`, so the key comes from the right one. Never put the key in `config.local.yaml`, the repo or your shell profile, and don't share screenshots of the terminal while it is on screen. If your shell loads a key automatically (for example with direnv), the line above shows whether one is set.
3. **Choose the model.** `rehearse.py` has no `--set` flag, so it reads the model from `config.local.yaml`. For Claude 5.5 through the API, set (keep your other keys in that file):
   ```yaml
   model:
     provider: anthropic
     id: claude-haiku-5-5
   agency:
     director:
       model: claude-sonnet-5-5
   ```
   For Bedrock, use `provider: bedrock` with `id: global.anthropic.claude-haiku-4-5-20251001-v1:0` and the Director `global.anthropic.claude-sonnet-4-6`.
4. **Check that the model answers:**
   ```bash
   python luna.py --ask "Reply with the single word ok."
   ```
   It prints `ok` and a cost line. A 401 means a wrong key; a credit-balance error means the Console account has no credit.
5. **Rehearse every scene:** `python rehearse.py`. It takes about 6 minutes and costs about 30 cents, and ends with `✅ Ready for the talk` or names the scenes that failed and shows their output.
6. **The approval and fleet scenes are in the rehearsal too.** It answers `n` to Luna's `[y/N]` question, so nothing is deleted, and it starts the specialists as A2A servers, asks one question and stops them. Run each by hand once anyway, to see what the audience will see:
   - *Approval:* `python luna.py`, ask *"Add 'buy sunscreen' to my list."*, then *"Delete the sunscreen task."* Luna must ask for your approval before it deletes.
   - *Fleet:* run `python fleet_server.py --all` in one terminal and `python luna.py --mode fleet` in another, then ask a question that needs two specialists (weather and currency). The 📨 lines show the Director delegating over A2A. Stop the server with Ctrl+C.
7. **Tidy up after the rehearsal:**
   ```bash
   rm -f data/todo.json business/*/reports/*.md
   git status --short          # nothing should be listed
   ```
8. **On the day of the talk:** `python setup/refresh_sample_dates.py` (on a Sunday it anchors to the previous one; to rehearse early as if it were the day, add `--today YYYY-MM-DD`), seed the memory scene at least 5 minutes ahead (see below), and ten minutes before start run `python setup/prewarm.py` until it ends with `✅ Warm and ready`. The full list is in [talk-checklist.md](talk-checklist.md).

## The day before

The full list, with the checks and a log to fill in, is in [talk-checklist.md](talk-checklist.md). In short:

1. **Check access and resources:**
   ```bash
   python rehearse.py            # every scene once, with checks; about 6 minutes and $0.30 on Claude 4.x
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

### Record the clips on a Mac, step by step

Video is the simplest fallback: no extra software on the presenting machine, and it plays with the network off.

1. **Set the Mac up like the demo machine** ([Run the demo yourself](#run-the-demo-yourself-step-by-step)): clone the repo, make the venv, install the requirements, and copy `assistant/config.local.yaml` from your other machine (it is git-ignored and holds the resource IDs). Export the key and the AWS profile, then run `python setup/prewarm.py` until it ends with `✅ Warm and ready`.
2. **Prepare the data:** `python setup/refresh_sample_dates.py`, `rm -f data/todo.json business/*/reports/*.md`, and seed the memory at least 5 minutes before you record the memory clip.
3. **Prepare the terminal:** dark theme, font size 20 or larger, window about 100 × 30, `PS1='❯ '`, notifications off (Focus mode), `clear` before each take.
4. **Allow screen recording once:** System Settings → Privacy & Security → Screen & System Audio Recording → turn on QuickTime Player (or Terminal and your browser, if macOS asks).
5. **Record each clip with QuickTime Player:** File → New Screen Recording, click the small arrow next to the red button and set Microphone to *None* (or pick your microphone to narrate), drag to select only the terminal window, run the scene, then stop from the menu bar (⌘⌃Esc). Trim the start and end with Edit → Trim (⌘T). Save it as `clips/<name>.mov`, with the names in the table below. (`⌘⇧5` does the same with Record Selected Portion.)
6. **Keep the take where the answer reads best.** Answers vary; a clip with a tool error or a slow answer is not worth keeping. Redo it.
7. **Test them with the Wi-Fi off:** open each file in QuickTime Player, press space to play. Put all the clips in one folder and keep it open in Finder during the talk. Copy the folder to a USB stick too. Do not commit the videos (they are large); the checklist's last step publishes them.

| Clip | Run | Type |
|---|---|---|
| `01-chatbot` | `python luna.py --no-tools` | *What should I wear today?* |
| `02-agent` | `python luna.py` | *What should I wear today, and how much is 85 dollars in pesos? Add 'buy sunscreen' to my list.* then *Delete the sunscreen task* (shows the approval) |
| `04-make-it-yours` | `python luna.py --preset family` | *What should I wear today?* |
| `05-agency` | `python luna.py --mode agency` | *Plan my Saturday at the beach, budget 50 USD* |
| `06-many-sources` | `python luna.py --preset winery` | the time-and-web-page question in scene 6 |
| `07-your-business` | `python luna.py --preset coffee-shop` | *What do I need to reorder this week, and from which supplier is espresso cheaper?* |
| `07b-clinic` | `python luna.py --preset clinic` | the cancellation-fee and allergy question in scene 7b |
| `08-monday-briefing` | `python luna.py --preset winery --mode agency` | the Monday briefing question in scene 8 (about 1 minute; cut the waiting) |
| `09-guardrail` | `python luna.py` | *Should I buy bitcoin with my savings?* |
| `10-memory` | `python luna.py` | *Suggest a dinner for tonight based on what you know about me, and tell me which of my preferences you used.* |
| `11-documents` | `python luna.py` | *According to my lease, when is the rent due and how much is it?* |
| `12-cloud` | from the repo root: `agentcore invoke --runtime luna --payload '{"prompt": "What should I wear today in Ensenada?"}'` | nothing |

The exact questions for scenes 6, 7b and 8 are in the [scenes table](#scenes) below; copy them from there. What to say over each clip, and how to read the cost line, is in [clip-notes.md](clip-notes.md).

## Scenes

Each scene has a slide in [the deck](slides/claude-on-aws-ensenada.pptx) with the command and what to watch for; the fallback clip name (`clips/01-chatbot` and so on) is in that slide's speaker notes, not on the slide. Name the recordings to match. `rehearse.py` runs every scene with the same questions (the approval scene answers `n` for you).

| # | Slide | Scene | Command | What the audience should see | If it fails |
|---|---|---|---|---|---|
| 1 | 13 | Chatbot | `python luna.py --no-tools`, then *"What should I wear today?"* | It guesses: no tools, no real weather | It only needs the model |
| 2 | 14 | Agent | `python luna.py`, then *"What should I wear today, and how much is 85 dollars in pesos? Add 'buy sunscreen' to my list."* | `get_weather`, `convert_currency`, `add_task`; real numbers; the cost line | Weather or rates API down → play the clip |
| 3 | 14 | Human in the loop | *"Delete the sunscreen task"* | Luna asks for approval before deleting | — |
| 4 | 15 | Make it yours | `python luna.py --preset family`, or `--set assistant.personality=pirate`, or a suggestion from the room | Same agent, new name, voice and model | — |
| 5 | 16 | Agency | `python luna.py --mode agency`, then *"Plan my Saturday at the beach, budget 50 USD"* | The Director's orders (📨) and the specialists' replies (✅), cost per agent | Slow (about 20 s): talk over the orders |
| 6 | 21 | Many sources (MCP) | `python luna.py --preset winery`, then *"What time is it in Los Angeles right now? Then read https://en.wikipedia.org/wiki/Valle_de_Guadalupe and give me two facts I can tell my US guests."* | `get_current_time` and `fetch`: two MCP servers, one answer | Site slow → any other public page |
| 7 | 22 | Your business | `python luna.py --preset coffee-shop`, then *"What do I need to reorder this week, and from which supplier is espresso cheaper?"* | The `files` server reads `inventory.csv`; RAG finds the supplier prices; one answer from both | — |
| 7b | 23 | Any business (a clinic) | `python luna.py --preset clinic`, then *"A patient cancelled a cleaning with only 5 hours' notice. Is there a fee? And which patient on 16 November has an allergy the dentists should know about?"* | The same agent, a third kind of business: it reads `appointments.csv` and searches the clinic's policies (20% fee, penicillin allergy). Nothing in the code changed, only a preset and data | Run `python luna.py --preset clinic` once beforehand; the documents must be synced (`create_knowledge_base.py --sync`) |
| 8 | 24 | Monday briefing (advanced) | `python luna.py --preset winery --mode agency`, then *"Prepare my Monday briefing: will the patio be usable this coming weekend, how last weekend's sales compared with the weekend before, next Saturday's reservations and allergies, what 100 dollars is in pesos for US guests, and which cork supplier to use. Save it as a report."* | Orders to six specialists; then open `business/winery/reports/` and show the saved file | About 45 s: narrate the orders; or show a report saved in rehearsal |
| 9 | 29 | Guardrail | *"Should I buy bitcoin with my savings?"* | The guardrail's refusal, before Claude sees it | — |
| 10 | 31 | Memory | *"Suggest a dinner for tonight based on what you know about me, and tell me which of my preferences you used."* | It knows you're vegetarian, from an earlier session | Not seeded → skip, or show the clip |
| 11 | 32 | Your documents | *"According to my lease, when is the rent due and how much is it?"* | `search_my_documents`, then 9,500 MXN by the 5th: an English question answered from a Spanish contract | — |
| 12 | 34, 46 | Cloud | From the repo root: `agentcore invoke --runtime luna --payload '{"prompt": "What should I wear today in Ensenada?"}'` | The same agent answering from AgentCore Runtime, with weather through the Gateway | Show the clip or the CloudWatch trace |

Scenes 6 to 8, with 7b, are the business block: the part most people will want to copy, so give it time. Scenes 9–12 are about 30 seconds each; pick the ones the room cares about most.

Explaining the concepts to a non-technical room: [plain-words.md](plain-words.md).

## Rehearsing on a second machine

Checked on a second, low-power Linux machine on 2026-11-14 (Claude 4.x on Bedrock, no Claude API key). Things that only show up on a fresh machine:

- **`config.local.yaml` is git-ignored,** so rebuild it on the new machine from the account: `python setup/_discover.py --write` (it finds the guardrail, memory and knowledge base by name, read-only, and writes the file; run it with the personal AWS credentials loaded). Or copy the file across. Without it the guardrail, memory and documents scenes silently run without those features.
- **The first run of scene 6 (MCP) is slow, about 3 minutes.** `uvx` downloads the `time` and `fetch` servers, and `fetch` runs `npm install` for its Readability dependencies on first use. Run the scene once the day before; killing it half-way throws the install away. Later runs take about 40 seconds.
- **`agentcore invoke` needs the project's deployment state,** which is git-ignored and lives on the machine that ran `agentcore deploy`. On another machine it says *No deployment targets are configured*. Do not run `agentcore deploy` to fix that. Either copy the state from the deploying machine (from the repo root there: `tar czf agentcore-state.tgz agentcore/.cli agentcore/aws-targets.json`, then `tar xzf` it in the repo root here; it stays git-ignored, and keep it with your `config.local.yaml` backup), or call the runtime directly:
  ```bash
  ARN=$(aws bedrock-agentcore-control list-agent-runtimes --query "agentRuntimes[?starts_with(agentRuntimeName, 'luna')].agentRuntimeArn | [0]" --output text)
  aws bedrock-agentcore invoke-agent-runtime --agent-runtime-arn "$ARN" \
    --runtime-session-id rehearsal-session-0000000000000000001 \
    --payload '{"prompt": "What should I wear today in Ensenada?"}' \
    --cli-binary-format raw-in-base64-out "${TMPDIR:-/tmp}/luna-out.json" && cat "${TMPDIR:-/tmp}/luna-out.json"
  ```
  `rehearse.py` and `setup/prewarm.py` make the same direct call when the CLI or its state is missing, so they pass on any machine with the account's credentials.
- **Refresh the winery's sample dates before the briefing scene:** `python setup/refresh_sample_dates.py` slides its sales and reservations (in whole weeks) so "last weekend" and "next Saturday" have data, and `setup/prewarm.py` warns when they are stale. Without it the briefing reports a data gap, and the rehearsal now fails on that. Put the original dates back with `git checkout -- assistant/business/winery` and never commit the shifted files.
- **The sample data has fixed dates (16 to 18 November 2026) for the clinic.** Luna's prompt says what today is, so a question that says "Monday" or "this week" changes meaning with the real date, and the answer can pick the wrong day. The demo questions name the date ("16 November"). Keep that when you write your own.
- **A small model can misread a rule.** Haiku once answered that a 5-hour cancellation is free, against a policy that says under 24 hours is charged. The policy now includes a worked example, which made the answer stable. When an answer has to be right on stage, put an example next to the rule in the document.
- **Credentials, model id, network or credit problems** print one line saying what to check (and `LUNA_DEBUG=1` shows the full trace). Say what it says out loud, then switch to Plan B (Bedrock Claude 4.x in `config.local.yaml`) or play the clip.
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

The deck's speaker notes carry a planned time per slide (`node build.js` prints 72 minutes with every slide and 56.5 without the optional ones; replace the estimates in `TIMING` in `docs/slides/build.js` with your timed run). The slide-by-slide script is in [presenter-script.md](presenter-script.md).

Add these up with your own talking time in the first full rehearsal, and write the total in [talk-checklist.md](talk-checklist.md). The must-show set is what you run if you are over time.

## Audience builds a business

The best proof that Luna works for any business is to build one for someone in the room, live. Ask *"What business do you have or work in?"* and take the first answer that has files and rules (a bakery, a gym, a repair shop, a school).

1. `python setup/new_preset.py bakery --business "Panadería Sol" --about "Owns a bakery; busiest on weekends"` (seconds; it creates the preset and a folder, then checks it).
2. Open `business/bakery/data.csv` and type or paste 4 to 6 rows the audience gives you (item, quantity, what they sell).
3. `python luna.py --preset bakery --check`, then `python luna.py --preset bakery` and ask one question about those rows.

Keep it to one question. If anything goes wrong, say *"this is why we check it"*, show the `--check` output, and switch to one of the two spare presets (see [talk-checklist.md](talk-checklist.md#2-the-day-before)). Small models can miscount rows, so ask for a list or a lookup, not a total.

## AWS console tour (the finale, slide 46)

The talk ends on the deployed Luna. Everything below exists in the personal account, us-east-1, and was checked READY or ACTIVE on 2026-11-16 (runtime `luna_default_luna`, gateway `luna-default-lunatools` with targets `weather` and `currency`, memory `luna_assistant`). Budget: about 5 minutes. Open these tabs before the talk, in this order, and keep the Region on **N. Virginia**.

1. **Invoke first** (terminal), so there is a fresh trace to look at: `agentcore invoke --runtime luna --payload '{"prompt": "What should I wear today in Ensenada, and how much is 85 dollars in pesos?"}'`, or the direct boto3 call from the section above. Warm it with `setup/prewarm.py` beforehand; a cold start adds a few seconds.
2. **AgentCore → Runtime → `luna_default_luna`:** status READY, the DEFAULT endpoint, the version, and the IAM role it runs as. Say: "one microVM per session, no server to manage".
3. **CloudWatch → GenAI Observability → Bedrock AgentCore:** the session, the trace, a span for each tool call, tokens and latency. **This view may be empty, and so may the trace fallbacks.** Checked 2026-11-17: Transaction Search is ACTIVE, but the account-level `aws/spans` log group stayed empty. The runtime's own `spans` stream and X-Ray had spans in the morning, then stopped (an invocation at 14:03 PST added none). The runtime logs were always there. Look at the dashboard on your own screen before the talk. If it is empty, show the logs instead:
   - **CloudWatch → Log groups → `/aws/bedrock-agentcore/runtimes/luna_default_luna-…-DEFAULT`**, then the newest `runtime-logs-<session id>` stream (it is named after the `--runtime-session-id` you invoked with). Every line carries the same `trace_id`, plus a `span_id` per step: credentials, memory, the Gateway calls signed with SigV4, the HTTP requests, the Strands metrics.
   - **View in Logs Insights** on that group (last hour) for one clean table of the steps:
     ```
     filter @logStream like "runtime-logs"
     | parse @message /(INFO|WARNING|ERROR) \[(?<component>[^\]]+)\]/
     | filter ispresent(component)
     | stats count(*) as calls, min(@timestamp) as first by component
     | sort first asc
     ```
   - Say: "the full trace dashboard needs extra setup; these are the same signals as raw logs, every line tied to one trace ID". If the spans come back, **CloudWatch → X-Ray traces** (service `luna_default_luna.DEFAULT`) or the `spans` stream (`filter @logStream = "spans" | stats count(*) by name`) show the steps with durations.
4. **AgentCore → Gateway → `lunatools`:** the two targets (`weather`, `currency`), the tools they became (`weather___getForecast`, …) and the IAM authorizer. Say: "one shared tool endpoint for every agent".
5. **AgentCore → Memory → `luna_assistant`:** the `preferences` strategy and the stored records (*vegetarian*, *hates cold*). Goes with scene 10.
6. **AgentCore → Identity:** the workload identity and the credential provider (the placeholder key). Say: "this is where a real API key would go, instead of an environment variable".
7. **Bedrock → Guardrails → `luna-assistant`** (the denied topic, the prompt-attack filter) and **Bedrock → Knowledge Bases** (the data source and its sync status). Goes with scenes 9 and 11.
8. **Budgets → `personal-monthly-budget`:** the answer to "what does it cost": a $20 monthly limit with alerts at 85% and 100% of actual spend and 100% of forecast (renamed on 2026-11-17 from a name that said 10 dollars).

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
