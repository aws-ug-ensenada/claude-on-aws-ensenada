# Talk checklist

Tick each box when the check passes; write the date next to it. Commands run from `assistant/` with the personal AWS account's credentials loaded (us-east-1). Details for each scene are in [demo-runbook.md](demo-runbook.md).

**The talk:** Tuesday 17 November 2026, 5:00 PM PST (UTC−8). "The day before" below means Monday 16 November, except the sample-dates step, which belongs on Tuesday (see below). Do the "ten minutes before" step around 4:30 PM.

## 1. A week before

- [ ] **Date, venue and language of the room decided** (the slides are in English, the first slide is in Spanish).
- [ ] **Models.** Decide which model runs on the day and rehearse that exact path on the presenting laptop.
  - Claude 4.x on Bedrock: tested. `python luna.py --no-tools --ask "ok"` answers.
  - Claude 5.5 through the Claude API: set `ANTHROPIC_API_KEY`, then `python luna.py --set model.provider=anthropic --set model.id=claude-haiku-5-5 --ask "ok"`. Not yet rehearsed on any machine in this repo's notes; rehearse it before relying on it.
  - Claude 5.5 on Bedrock: quota was 0 on 2026-11-14. Re-check with the commands in [bedrock-access.md](bedrock-access.md).
- [ ] **Offline tests green:** `python -m pytest tests -q` (31 tests) and the `smoke` check on the pull request.
- [ ] **A full rehearsal passes:** `python rehearse.py` ends with `✅ Ready for the talk`. Note the time and cost. The exact steps, from a fresh terminal, are in [demo-runbook.md](demo-runbook.md#run-the-demo-yourself-step-by-step).
- [ ] **The AWS diagrams match what is deployed.** `docs/diagrams/local.py` and `cloud.py` (regenerate with `pip install diagrams`, graphviz, then `python local.py && python cloud.py`) were redrawn on 2026-11-15 against `agentcore/agentcore.json` and the presets; slides 8 and 34 are drawn in `docs/slides/build.js`. Redraw all of them after any architecture change.
- [ ] **The deck checks pass:** `cd docs/slides && python3 check_deck.py` (text size, colour contrast, a timed speaker note on every slide). `node build.js` prints the planned time: 59 minutes with every slide, 41.5 without the optional ones, so plan to skip the optional ones in the order the [presenter script](presenter-script.md#if-you-are-running-long) gives.
- [ ] **PDF backup regenerated** after any slide change: `cd docs/slides && npm run pdf`, and open it once. The PDF is committed next to the deck.
- [ ] **The QR code opens the repo** when scanned with a phone (it decodes correctly from the rendered slide).
- [ ] **Time the talk once**, out loud, with the real slides and the demo. Write the total here: ____ min. If it is over 40 minutes, drop scenes from the "if time allows" list in [demo-runbook.md](demo-runbook.md#time-budget).
- [ ] **Clips recorded**, one per scene that is live, named as on the slides (`clips/01-chatbot` … `clips/07b-clinic` …), and they play from the presenting laptop with no network.
- [ ] **Prices re-checked** ([costs.md](costs.md)) and the budget alarm is set.
- [ ] **A person outside the project followed the README quickstart** and reached the first answer.

## 2. The day before

- [ ] `python setup/clean_memory.py` lists only the preferences the memory scene needs (*vegetarian*, *hates cold*). Tidy with `--keep vegetarian --keep cold --yes`.
- [ ] Seed the memory scene at least 5 minutes before you test it: `python luna.py --ask "Remember this about me: I'm vegetarian and I hate cold weather."`
- [ ] `python setup/refresh_sample_dates.py` **on the day of the talk** (not on a Sunday: it anchors to the previous Sunday), so the winery briefing has data for "last weekend" and "next Saturday" (undo with `git checkout -- assistant/business/winery`; never commit the shifted files).
- [ ] `rm -f data/todo.json business/*/reports/*.md` so the audience sees the files appear.
- [ ] Documents are synced: `python setup/create_knowledge_base.py --sync`, and the rent, clinic-fee and supplier questions all answer.
- [ ] The presenting laptop: dark terminal theme, font 20 or larger, notifications off, charger plugged in, slides open from a local file, the `.pptx` also exported to PDF as a backup.
- [ ] **Backup of everything:** the repo on a USB stick or second device, with `config.local.yaml` (it is git-ignored and holds the resource IDs).
- [ ] Prepare **two spare presets** for the audience-built business (see [demo-runbook.md](demo-runbook.md#audience-builds-a-business)), for example a bakery and a repair shop, in case the audience's idea doesn't work out on stage.

## 3. Ten minutes before (warm everything)

- [ ] `python setup/prewarm.py` ends with `✅ Warm and ready`. It checks the three business presets, the model, the MCP servers (the first run downloads packages and can take 3 minutes), the guardrail, the memory records and the AgentCore runtime.
- [ ] Network: open one web page; if the venue Wi-Fi blocks anything, switch to the phone's hotspot now, not during the demo.
- [ ] Terminal in the right folder, virtual environment active, `AWS_PROFILE=personal AWS_REGION=us-east-1`.
- [ ] AWS console tabs open and logged in (see [demo-runbook.md](demo-runbook.md#aws-console-tour)).
- [ ] Clips open in a player, one tab or playlist entry per scene.

## 4. During the talk

- [ ] Each live scene has a clip ready; if an answer takes more than 20 seconds more than the plan, say what it is doing and switch to the clip.
- [ ] If the guardrail refuses a scene it shouldn't (memory is the usual cause), rerun it with `--set memory.enabled=false`.
- [ ] Keep one minute of slack for the audience's question.
- [ ] Follow [presenter-script.md](presenter-script.md); if you run long, skip in the order it gives.
- [ ] Leave the final slide (the repo QR code and the first command) on screen during Q&A.

## 5. After the talk

- [ ] `python setup/cleanup.py --dry-run`, then `python setup/cleanup.py` and `agentcore remove all --yes && agentcore deploy --yes` if you don't need the AWS resources.
- [ ] Lower the CloudWatch Transaction Search indexing to 1% (command in the [README](../README.md#clean-up)).
- [ ] Publish the clips and the slides to the repo or a link, and write down what the audience asked for.

## 6. Validation log

| Date | Where | What was checked | Result |
|---|---|---|---|
| 2026-11-14 | Low-power Linux machine, Claude 4.x on Bedrock | `rehearse.py` (11 scenes plus the new Spanish one), `setup/prewarm.py` (all steps, MCP first run 125 s), clean checkout, clinic, tests, CI | all passed after the memory cleanup; first MCP run takes about 3 minutes; the Claude 5.5 path was not run |
| 2026-11-15 | Same machine, Claude 4.x on Bedrock | full `rehearse.py` after the counting tool, deck checks, QR decode; `clinic`, `spanish` and `cloud` repeated 3 times | first full run failed 3 scenes (date-dependent question, a misread policy, no deployment state for the CLI); all fixed, then 9 of 9 passed |
| 2026-11-15 | Same machine | model prices vs the AWS Price List API; cost slide and `costs.md`; winery sample dates; diagrams redrawn | prices unchanged; slide 36 corrected to measured Claude 4.x numbers; the briefing reported a data gap on today's date, now fixed with `refresh_sample_dates.py` and a stricter rehearsal check |
| 2026-11-15 | Personal AWS account, us-east-1 | Claude 5.5 quota requests for Haiku, Sonnet and Opus (cases 179469848300860, 179469848500530, 179469848900918) | all closed automatically in about 20 seconds, quotas still 0; escalate through an AWS contact, and plan the talk on Claude 4.x on Bedrock or the Claude API |
| 2026-11-15 | Personal AWS account, us-east-1, Claude 4.x on Bedrock (Haiku 4.5, Director Sonnet 4.6), winery dates shifted as for Tuesday 17 | `setup/prewarm.py`, then full `rehearse.py` (13 scenes) | prewarm passed except memory (4 records; stray ones deleted with `clean_memory.py`); all 13 scenes passed, about 5 minutes and about $0.25 in total; the Claude 5.5 path through the Claude API was not run (no `ANTHROPIC_API_KEY` in this session); scene 3 (approval) and the fleet level are not in `rehearse.py` |
| 2026-11-15 | Claude 5.5 through the Claude API (Haiku 5.5, Director Sonnet 5.5), AWS in us-east-1, winery dates shifted with `--today 2026-11-17` | `luna.py --ask ok`, then full `rehearse.py` (13 scenes), then `memory` and `briefing` again after two fixes | first run 11 of 13: `memory` failed the check (the answer was vegetarian but never said so; the question now asks which preferences it used) and `briefing` reported a data gap (stale sample dates; fixed by refreshing); both then passed. The approval scene and the fleet level are not in `rehearse.py` and have not been checked yet |
| 2026-11-15 | Claude 5.5 through the Claude API (Haiku 5.5), AWS in us-east-1, run by hand | the two scenes `rehearse.py` can't run: approval (`luna.py`: add a task, delete it) and the fleet (`fleet_server.py --all`, then `luna.py --mode fleet` with a weather and currency question) | both passed: the delete asked `[y/N]` before it ran, and the Director sent orders to `planner` and `finance` over A2A and combined their answers (about $0.0095) |
| 2026-11-15 | Fresh clone in a temp folder, then this machine; Claude 4.x on Bedrock | README quickstart from a clean clone (venv, `pip install`, `luna.py --no-tools --ask ok` answered); `new_preset.py bakery` + data + a live question (215 conchas, bolillos busiest: correct, $0.024, 4 tool calls); `--check` on a bad key, bad YAML and a missing folder (each gave a clear message); `cleanup.py --dry-run` (guardrail, memory, knowledge base found by name); `rehearse.py clinic spanish memory briefing rag cloud` 3 times | all passed, 3 of 3 runs `Ready for the talk`; the Claude 5.5 path was not repeated (no key in this session) |
| 2026-11-15 | This machine, Claude 4.x on Bedrock | doc sweep (slide numbers in the presenter script, every `python …` command in the docs checked against the scripts' flags, presets and config keys); failure drills: memory off, fake AWS credentials, bad model id, bad Claude API key, no network | commands all consistent; stale README lines (slide count, CI) and a scene count fixed; the drills used to end in a stack trace, now `luna.py` prints a one-line reason and fix (`LUNA_DEBUG=1` shows the trace); 33 tests pass |
| | | | |
