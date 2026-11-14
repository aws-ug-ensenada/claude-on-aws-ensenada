# Talk checklist

Tick each box when the check passes; write the date next to it. Commands run from `assistant/` with the personal AWS account's credentials loaded (us-east-1). Details for each scene are in [demo-runbook.md](demo-runbook.md).

## 1. A week before

- [ ] **Date, venue and language of the room decided** (the slides are in English, the first slide is in Spanish).
- [ ] **Models.** Decide which model runs on the day and rehearse that exact path on the presenting laptop.
  - Claude 4.x on Bedrock: tested. `python luna.py --no-tools --ask "ok"` answers.
  - Claude 5.5 through the Claude API: set `ANTHROPIC_API_KEY`, then `python luna.py --set model.provider=anthropic --set model.id=claude-haiku-5-5 --ask "ok"`. Not yet rehearsed on any machine in this repo's notes; rehearse it before relying on it.
  - Claude 5.5 on Bedrock: quota was 0 on 2026-11-14. Re-check with the commands in [bedrock-access.md](bedrock-access.md).
- [ ] **Offline tests green:** `python -m pytest tests -q` (29 tests) and the `smoke` check on the pull request.
- [ ] **A full rehearsal passes:** `python rehearse.py` ends with `✅ Ready for the talk`. Note the time and cost.
- [ ] **Time the talk once**, out loud, with the real slides and the demo. Write the total here: ____ min. If it is over 40 minutes, drop scenes from the "if time allows" list in [demo-runbook.md](demo-runbook.md#time-budget).
- [ ] **Clips recorded**, one per scene that is live, named as on the slides (`clips/01-chatbot` … `clips/07b-clinic` …), and they play from the presenting laptop with no network.
- [ ] **Prices re-checked** ([costs.md](costs.md)) and the budget alarm is set.
- [ ] **A person outside the project followed the README quickstart** and reached the first answer.

## 2. The day before

- [ ] `python setup/clean_memory.py` lists only the preferences the memory scene needs (*vegetarian*, *hates cold*). Tidy with `--keep vegetarian --keep cold --yes`.
- [ ] Seed the memory scene at least 5 minutes before you test it: `python luna.py --ask "Remember this about me: I'm vegetarian and I hate cold weather."`
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
- [ ] Leave the final slide (the repo QR code and the first command) on screen during Q&A.

## 5. After the talk

- [ ] `python setup/cleanup.py --dry-run`, then `python setup/cleanup.py` and `agentcore remove all --yes && agentcore deploy --yes` if you don't need the AWS resources.
- [ ] Lower the CloudWatch Transaction Search indexing to 1% (command in the [README](../README.md#clean-up)).
- [ ] Publish the clips and the slides to the repo or a link, and write down what the audience asked for.

## 6. Validation log

| Date | Where | What was checked | Result |
|---|---|---|---|
| 2026-11-14 | Raspberry Pi, Claude 4.x on Bedrock | `rehearse.py` (11 scenes plus the new Spanish one), `setup/prewarm.py` (all steps, MCP first run 125 s), clean checkout, clinic, tests, CI | all passed after the memory cleanup; first MCP run takes about 3 minutes; the Claude 5.5 path was not run |
| | | | |
