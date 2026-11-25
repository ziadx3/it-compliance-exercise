# layers/agent_layer.py
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
except ImportError:
    try:
        from langchain.agents.agent import AgentExecutor
        from langchain.agents.openai_tools.base import create_openai_tools_agent
    except ImportError:
        from langchain_classic.agents import AgentExecutor, create_openai_tools_agent

@tool
def propose_escalation_ticket(
    target_role: str,
    policy_citation: str,
    request_summary: str,
    reason: str
) -> str:
    """Drafts an escalation ticket in the background for UI user approval. 
    Call this immediately whenever a policy requires escalation, incident reporting, or when handling an uncovered policy gap."""
    payload = {
        "status": "PENDING_USER_CONFIRMATION",
        "target_approver_role": target_role,
        "policy_citation": policy_citation,
        "summary": request_summary,
        "escalation_reason": reason
    }
    return json.dumps(payload, ensure_ascii=False)

def build_compliance_agent(retrieval_tool):
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )

    tools = [retrieval_tool, propose_escalation_ticket]

    system_prompt = """You are a strict Corporate IT Compliance AI Agent.
Evaluate requests ONLY using the clauses retrieved by `search_policy_database`.

EXECUTION RULES:
1. CONTEXT-AWARE SEARCH: ALWAYS call `search_policy_database` first. If the user's message is a short follow-up, combine it with the previous `chat_history` context when forming the English search query.
2. DISTINGUISH INQUIRY VS ESCALATION:
  - If the user is ONLY asking a general informational question, answer clearly with the policy citation. Do NOT call `propose_escalation_ticket`.
  - If the user's situation requires escalation, exception approval, or incident reporting, immediately call `propose_escalation_ticket`.
3. NEVER output raw JSON or code blocks in your text reply. The UI will automatically render an interactive Approval Card from the tool output.
4. Keep your text response concise and natural.
5. EDGE CASE - NO POLICY FOUND (POLICY GAP) & UNCOVERED REQUESTS:
   IF `search_policy_database` returns `NO_MATCHING_POLICY_FOUND` OR the request involves something not explicitly permitted by existing policies:
- You MUST immediately call the tool `propose_escalation_ticket` with:
  - target_role: "IT Governance & Compliance Team"
  - policy_citation: "UNCOVERED / POLICY_GAP"
  - request_summary: A concise summary of the user's request.
  - reason: "No existing policy covers this request; formal review required."
- DO NOT just write text. You MUST execute the tool call so the approval card appears in the UI.
6. EDGE CASE - VAGUE, EMOTIONAL OR NONSENSE INPUT:
   - If the user provides an extremely vague, emotional, or unclear input (e.g., "Help me fix this fast!!") without specifying a technical problem, policy inquiry, or security incident:
   - DO NOT trigger `propose_escalation_ticket` and DO NOT guess.
   - Instead, respond politely asking the user to clarify their specific technical problem or policy question.
7. MANDATORY CITATION GROUNDING: 
   When answering general policy inquiries, you MUST explicitly mention the exact policy ID (e.g., SOP-IT-003, SOP-IT-004) retrieved from the database in your text response to ensure strict grounding and compliance auditing."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        return_intermediate_steps=True
    )
    return agent_executor