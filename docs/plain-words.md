# The concepts in plain words

A cheat sheet for explaining this talk to people who don't work in tech: business owners, students, family. Each concept has a one-line explanation, an everyday comparison, and how it shows up in Luna. The speaker notes in [the slides](slides/claude-on-aws-ensenada.pptx) use the same wording.

## The big idea

| Concept | In plain words | Like… | In Luna |
|---|---|---|---|
| **Chatbot** | A program you talk to that answers from what it learned. | A very well-read person on the phone who can't see outside or look anything up. | `python luna.py --no-tools`: it guesses today's weather |
| **Agent** | A chatbot that can also *do things*: look things up, use apps, take steps on its own. | The same person, now with a phone, a calculator and your notebook. | `python luna.py`: real weather, real exchange rate, your to-do list |
| **Model (Claude)** | The "brain" that reads your request and decides what to do. | The person's judgment. | Claude Haiku (fast and cheap) or Sonnet (stronger) |
| **Tool** | One thing the agent is allowed to do, like "get the weather". | An app on the assistant's phone. | `tools/weather.py`, `tools/currency.py`, `tools/todo.py` |
| **Tokens** | How AI usage is measured and billed: roughly pieces of words. | Paying by the word for a translator. | The 💲 line after every answer |
| **Context window** | The most the model can read in one call. It starts empty every call: instructions, tool descriptions, memory, documents, the conversation and your question all have to fit. | A desk of a fixed size: whatever isn't on it, the model can't see. | `"Reply with the single word ok."` was 1,633 tokens in: almost all of it Luna's own instructions and tools |
| **System prompt** (instructions) | The standing instructions sent with every call: who it works for and its rules. | The employee handbook, handed over before each shift. | `assistant.extra_instructions` and a preset |
| **Hallucination and grounding** | A model can sound sure and be wrong. Grounding means putting a real source in front of it (a tool, a document) so it answers from that. | A person guessing the weather vs reading the forecast. | The plain chatbot guesses; the agent calls `get_weather` |

## Giving it more

| Concept | In plain words | Like… | In Luna |
|---|---|---|---|
| **MCP** (Model Context Protocol) | A standard plug for connecting an AI to other apps and data. | USB-C: one kind of cable for many devices. Anyone can make a "device" that plugs in. | `mcp_servers` in `config.yaml`: time, web pages, your files, AWS docs, Gmail |
| **MCP server** | One connector: it gives the agent a set of tools for one app. | A charger for one device. | `files` lets Luna read and save files in one folder, and only that folder |
| **RAG** (your documents) | The agent searches your documents before it answers, and says where the answer came from. | An open-book exam: it may look in *your* binder. | The lease, the café's price list, the winery's handbook |
| **Knowledge base / vectors** | Your documents, prepared so they can be searched by meaning, not only by exact words. | A librarian who knows which page talks about "rent" even if you asked about "monthly payment". | Bedrock Knowledge Bases on S3 Vectors |
| **Embedding / vector** | A list of numbers that captures the *meaning* of a piece of text, so similar meanings sit close together. | A map where "rent" and "monthly payment" are neighbours. | Titan Embeddings V2 |
| **Chunk** | A piece of a document (a few paragraphs). Documents are cut into chunks so the search can return just the relevant bits. | Index cards cut from a long binder. | The knowledge base splits `my_documents/` before indexing |
| **Vector database** | A store that finds the chunks closest in meaning to your question. | A librarian who answers "which pages are about this?" | Amazon S3 Vectors |
| **Short-term memory** | The conversation so far, re-sent to the model on every call. It lives in the context window and is gone when the session ends. | The notes on the table during one meeting. | Any Luna session |
| **Long-term memory** | The model has none: the app stores facts about you outside it and puts the relevant ones back in the prompt next session. | A good waiter who remembers you don't eat meat. | AgentCore Memory: "I'm vegetarian" told yesterday, used today |

## Keeping it safe

| Concept | In plain words | Like… | In Luna |
|---|---|---|---|
| **Guardrails** | Rules checked *outside* the AI, so it can't be talked out of them. | A bouncer at the door, not a polite request. | Investment advice and medical diagnosis are refused; card numbers are hidden |
| **Prompt injection** | Someone tries to trick the AI with text like "ignore your instructions". | A forged note from the boss. | "Ignore all previous instructions…" is blocked |
| **Human in the loop** | The agent asks before doing something risky. | An assistant who checks with you before throwing anything away. | Deleting a task asks for your OK first |
| **Least privilege** | Each agent can only touch what its job needs. | The cashier has the till key, not the safe. | The finance agent can't open the files; the files server can't leave its folder |

## Teams of agents

| Concept | In plain words | Like… | In Luna |
|---|---|---|---|
| **Agency** (multi-agent) | One manager agent splits a job and hands the pieces to specialist agents. | A restaurant: the head chef calls the orders, each station cooks its part. | The Director sends orders to the planner, finance, office and librarian |
| **A2A** (Agent-to-Agent) | A standard way for agents to call each other over the network. | Departments phoning each other with a shared phone book. | `--mode fleet`: each specialist is its own service |

## In the cloud

| Concept | In plain words | Like… | In Luna |
|---|---|---|---|
| **AgentCore Runtime** | Runs your agent on AWS so it works without your laptop, for many people at once. | Moving from cooking at home to a rented commercial kitchen. | `agentcore deploy` |
| **AgentCore Gateway** | One shared entrance to your tools for all your agents, with security at the door. | A company switchboard: one number, it connects you to the right department. | Weather and currency served to every agent from the Gateway |
| **IAM / SigV4** | AWS's way of checking who is asking and what they're allowed to do. | A staff badge that opens only certain doors. | The runtime's badge lets it call the Gateway and nothing else |
| **Observability / traces** | A record of every step the agent took, to see what happened and why. | A flight recorder. | CloudWatch traces of every order between agents |

## Three sentences for the whole talk

1. A chatbot only talks. An agent also **acts**, with tools you choose.
2. You decide what it can reach (**MCP**, your documents) and what it must never do (**guardrails**).
3. It can start on your laptop for a few cents and move to the **cloud** when other people need it.
