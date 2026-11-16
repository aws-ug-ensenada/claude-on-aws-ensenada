# Kahoot quiz: five questions

For the optional quiz near the end of the talk (slides 43 and 44 are the same questions, as a fallback). Create a **Quiz** in Kahoot, add these five questions with four answers each, mark the correct one, and set **20 seconds** per question. Kahoot limits: a question up to 120 characters, an answer up to 75; all of these fit.

The prize is a surprise: announce it at the event and give it to the top of the leaderboard.

| # | Question | A | B | C | D | Correct |
|---|---|---|---|---|---|---|
| 1 | Between two separate chats, what does the model remember by itself? | Your preferences | Last week's chat | Nothing | Everything you typed | **C** |
| 2 | How can Luna know today's weather? | Its training data | A tool fetches it | The guardrail | Memory | **B** |
| 3 | You need an exact count from a CSV. What do you use? | A tool that counts | The model estimates | A bigger context window | A longer prompt | **A** |
| 4 | What is A2A for? | Giving an agent tools | Storing memory | Agents asking agents | Blocking topics | **C** |
| 5 | What does RAG do? | Retrains Claude | Finds matching chunks for the prompt | Makes answers faster | Deletes memory | **B** |

## Why each answer is right (say it after Kahoot shows the result)

1. **Nothing.** The model is stateless; memory is something the agent adds (slide 30).
2. **A tool.** The model decides to use the tool; the Python function does the fetching.
3. **A tool.** Models read text, they are not calculators, so exact sums belong in code.
4. **Agents asking agents.** MCP is for tools; A2A is for agent to agent.
5. **RAG finds the chunks closest in meaning** and puts them in front of the model; it doesn't retrain anything.

## Before the talk

- Create the quiz on your Kahoot account and play it once from a phone, so you know where the join PIN appears and how to show the leaderboard.
- Open it on the presenting laptop in a second browser tab; you start the game when you reach slide 43, share the screen with the PIN, then come back to the deck.
- If Kahoot or the Wi-Fi fails, run the same questions from slide 43 as a show of hands, and give the answers from slide 44.
