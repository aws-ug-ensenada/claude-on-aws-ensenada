# Presenter script

What to say and do, slide by slide, with the transitions. Slide numbers are for the 38-slide deck; the timing for each slide is in its speaker notes (`⏱`), and the ones marked *optional* are the first to skip. Demo commands and fallbacks are in [demo-runbook.md](demo-runbook.md). The slides are in English; speak in whichever language the room prefers.

**The one sentence to land:** *An agent is a brain, hands and rules, and the same small agent works for any business: you change who it works for, what it can see and what it can do.*

## Opening (slides 1 to 3)

- **1 Title.** Welcome. "Tonight we build one assistant on stage and grow it from a chatbot into a team of agents on AWS."
- **2 Bienvenidos.** Say it in Spanish, one sentence per card: one assistant and eight levels; works for any business; everything is in the repo.
- **3 Show of hands.** Ask both questions and count hands. *Transition:* "An agent is just a chatbot that can act. Let me show what that means."

## Part 1: the idea (slides 4 to 9)

- **5 Brain + hands + rules.** The one idea. Use the analogy: a well-read person on the phone who can't look anything up, then give them a phone, a notebook and house rules.
- **6 How an agent answers.** Walk the loop: ask, plan, call a tool, read, answer. "The model never touches the internet; our code runs the tool."
- **7 Strands Agents.** "This is the whole framework in ten lines. The docstring is the instruction the model reads." *Transition:* "Here is how all the pieces fit."
- **8 The whole picture.** Point left to right: you, Luna, AWS. Say you will light up one box in each demo.
- **9 Words (optional).** Only if the room is non-technical.

## Part 2: meet Luna (slides 10 to 16)

- **11 Chatbot (live).** Run `--no-tools`. "It sounds sure and it's guessing."
- **12 Agent (live).** Same question, now with tools. Point at `Tool #` lines and the cost line. Show the delete approval if time allows.
- **13 Make it yours (optional).** Take a suggestion from the room for a personality.
- **14 Director and specialists (live).** Narrate the orders (📨) while it works; about 20 seconds.
- **15 Who is the orchestrator? (optional) and 16 chat vs fleet.** One sentence each. *Transition:* "So far a personal assistant. Now the part most of you will copy: a business."

## Part 3: any business (slides 17 to 25)

- **18 Two examples, yours is the third.** The central message: "A winery and a coffee shop because they are from here. Nothing in the agent is about wine or coffee."
- **19 Many sources (optional).** The time and a web page through MCP.
- **20 Files and documents (live).** Coffee shop: reorder list from the CSV and the cheaper supplier from the documents.
- **21 A third business (live).** The clinic. "Same agent. Only the preset and the data changed." Point at the exact count from the counting tool.
- **Audience builds a business (live, optional but the best moment).** Ask for a business; follow [the steps in the runbook](demo-runbook.md#audience-builds-a-business). *If it goes wrong:* "This is why there is a checker", then switch to a spare preset.
- **22 Monday briefing (optional, clip is fine).** About 45 seconds; narrate the orders and open the saved report.
- **23 Connect your world (optional), 24 Not just wineries, 25 Five steps.** *Transition:* "That's the work. Now what keeps it safe and what it looks like on AWS."

## Part 4: rules, memory, documents, cloud (slides 26 to 34)

- **27 Guardrails (live).** The bitcoin question; the refusal comes before Claude sees it.
- **28 Memory, 29 Your documents (optional, live or clip).** "It knows you're vegetarian from an earlier session"; the lease answered from a Spanish contract.
- **30 MCP and A2A (optional).**
- **31 The cloud (live).** `agentcore invoke` or the direct call in the runbook. Option: the 3-minute AWS console tour.
- **32 Laptop to production, 33 Safe with real data.** "Start read-only; give write access one tool at a time."
- **34 What broke.** The honest slide. Tell the memory story: leftover memory made the guardrail refuse a fair question.

## Closing (slides 35 to 38)

- **35 Built with Claude Code (optional), 36 What it costs.** "Cents per answer; about $5 for the whole talk."
- **37 Your turn.** Three steps: PartyRock, Skill Builder, this repo.
- **38 Questions.** Leave it up. The QR opens the repo; the first command is `python luna.py`; the one-page handout is [cheatsheet.md](cheatsheet.md).

## If you are running long

Skip in this order: 9, 15, 35, 23, 30, 19, 28, 13, 22. Everything else is the story.
