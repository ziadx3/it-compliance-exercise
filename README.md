# IT Compliance Agent

An AI agent that answers IT policy questions, shows which policy it used, and sends serious problems to the right team, only after the employee approves.

Built for the ARIS AI Specialist case study.

## What it does

| Situation | What the agent does |
|---|---|
| **Policy question** ("What are the rules for updating my password?") | Searches the policies, answers, and cites the SOP ID (e.g. `SOP-IT-003`) |
| **Incident or exception** ("My laptop was stolen", "Can I install Cursor AI?") | Drafts an escalation ticket. The employee approves it before it is sent |
| **No policy covers it** ("Can I work from Bali on the VPN?") | Escalates to the IT Governance & Compliance Team as a policy gap |
| **Vague message** ("Help me fix this fast!!") | Asks the employee to explain the problem. No ticket is created |

The agent never guesses. It answers from the retrieved policy, or it escalates.

## How it works

```
Employee  →  Streamlit chat  →  Agent (LangChain, GPT-4o-mini, temp 0)
                                      │
                    ┌─────────────────┴──────────────────┐
                    ▼                                    ▼
        search_policy_database               propose_escalation_ticket
        (ChromaDB + LLM rerank)              (draft → employee approval → IT queue)
```

1. **Interface** (`main.py`): Streamlit chat for the employee, an approval card for tickets, and an admin view that shows the IT queue.
2. **Agent** (`layers/agent_layer.py`): a LangChain tool-calling agent with two tools. It decides whether to answer, ask a question, or escalate.
3. **Knowledge** (`layers/knowledge_layer.py`): 50 IT policies (SOP-IT-001 to SOP-IT-050) stored in ChromaDB. Retrieval has two stages: vector search returns the 10 closest clauses, then an LLM reranker keeps the best 3. If nothing matches, the tool returns `NO_MATCHING_POLICY_FOUND` and the agent escalates.

All model calls (chat, embeddings, reranking) go through [OpenRouter](https://openrouter.ai).

## Project structure

```
.
├── main.py                  # Streamlit app (employee chat + admin queue)
├── layers/
│   ├── __init__.py
│   ├── agent_layer.py       # Agent, system prompt, escalation tool
│   └── knowledge_layer.py   # 50 policies, ChromaDB, retrieval + rerank
├── promptfoo_provider.py    # Connects the agent to Promptfoo
├── promptfooconfig.yaml     # Evaluation test suite (10 tests)
├── requirements.txt
└── .env                     # Your API key (create this, do not commit it)
```

## Setup

**Requirements:** Python 3.10+ and an OpenRouter API key.

```bash
# 1. (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
echo "OPENROUTER_API_KEY=your_key_here" > .env
```

If you skip step 3, the app asks for the key in the sidebar.

## Run the app

```bash
streamlit run main.py
```

Then open the local URL that Streamlit prints (usually http://localhost:8501).

**Things to try**

- `What are the rules for updating my company password?` → answer with `SOP-IT-003`
- `My work laptop was stolen from my car 30 minutes ago.` → approval card for a ticket
- `I need to install Cursor AI on my work laptop.` → escalation with `SOP-IT-001`
- `Help me fix this fast please!!` → the agent asks for details

After you approve a ticket, switch the sidebar toggle to **IT / InfoSec Admin View** to see it in the queue.

## Evaluation

The agent is tested with [Promptfoo](https://www.promptfoo.dev). Promptfoo is a Node.js tool, so it is not in `requirements.txt`.

```bash
npx promptfoo eval          # run the 10 tests
npx promptfoo view          # open the results in the browser
```

Run these from the project folder. Make sure `OPENROUTER_API_KEY` is set in your environment or `.env`.

### What is tested

Each test checks three things:

| Criterion | Question | How it is checked |
|---|---|---|
| **Answer quality** | Is the answer correct and complete? | `llm-rubric` (an LLM judges the answer) |
| **Right tools** | Did it pick search or ticket correctly? | `contains` on the tool list the provider appends to every reply |
| **Right sources** | Did it cite the correct SOP? | `contains` / `contains-all` on SOP IDs |

### Test cases

| Category | Tests |
|---|---|
| Policy inquiries | Password policy, confidential document storage |
| Critical incidents | Stolen laptop, phishing click |
| Exception requests | Install unapproved AI tool, personal cloud storage, credential sharing |
| Edge cases | Working from abroad (policy gap), vague input |
| Multi-intent | One question covering four policies |

### Latest results

9 of 10 tests passed (18 of 19 checks). The failing test is the multi-intent question: the agent missed `SOP-IT-043` when one message asked about four topics.

## Known limitations

- **Questions with several topics:** one part can get the wrong policy, because the search runs once for the whole message.
- **Speed:** replies take 17–33 seconds, because the agent searches, reranks, and then answers.
- **Tickets are stored in the session only.** They are not sent to a real system.

## Next steps

- Search each topic of a question separately.
- Make replies faster: stream the answer and skip the rerank step when the match is clear.
- Create tickets directly in Jira or ServiceNow.