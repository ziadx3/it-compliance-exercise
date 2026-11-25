# streamlit_app.py
import os
import json
import uuid
from datetime import datetime
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

from layers.knowledge_layer import init_vector_database, get_retriever_tool
from layers.agent_layer import build_compliance_agent


st.set_page_config(
    page_title="IT Compliance & Governance AI",
    page_icon="🛡️",
    layout="wide"
)

if "OPENROUTER_API_KEY" not in os.environ:
    st.sidebar.header("Configuration")
    api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")
    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key
    else:
        st.warning("Please enter your OpenRouter API Key in the sidebar to start.")
        st.stop()

@st.cache_resource
def load_agent_system():
    vectorstore = init_vector_database()
    retriever_tool = get_retriever_tool(vectorstore)
    return build_compliance_agent(retriever_tool)

try:
    agent_executor = load_agent_system()
except Exception as e:
    st.error(f"Failed to initialize system: {e}")
    st.stop()

# Session States
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_ticket" not in st.session_state:
    st.session_state.pending_ticket = None
if "submitted_tickets" not in st.session_state:
    st.session_state.submitted_tickets = []

def render_policy_sources(sources_list):
    """دالة منسقة لعرض المصادر بدون تكرار وبدون خلفيات بيضاء مزعجة"""
    if not sources_list:
        return
    
    unique_clauses = {}
    for src in sources_list:
        for block in src.split("\n---\n"):
            block = block.strip()
            if not block or "POLICY_ID:" not in block:
                continue
            policy_id = block.split("|")[0].replace("POLICY_ID:", "").strip()
            unique_clauses[policy_id] = block

    if unique_clauses:
        with st.expander(f"📚 View Retrieved Policy Sources ({len(unique_clauses)} Clauses)"):
            for pid, content in unique_clauses.items():
                lines = content.split("\nCONTENT:")
                header = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
                
                st.markdown(f"""
                <div style="background-color: #1F2839; padding: 14px; border-radius: 8px; border-left: 4px solid #B69D74; margin-bottom: 10px; color: #F8FAFC;">
                    <div style="color: #B69D74; font-weight: bold; font-size: 0.9rem; margin-bottom: 6px;">
                        📌 {header}
                    </div>
                    <div style="color: #E2E8F0; font-size: 0.95rem; line-height: 1.5;">
                        {body}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🛡️ Control Panel & Roles")
    view_mode = st.toggle("🔄 Switch to IT / InfoSec Admin View", value=False)
    
    st.divider()
    st.markdown("**👤 Employee:** `Ziyad Almutairi`")
    st.markdown(f"**🎫 Submitted Queue Tickets:** `{len(st.session_state.submitted_tickets)}`")
    
    st.divider()
    if st.button("Clear Chat Session", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.session_state.pending_ticket = None
        st.rerun()

# ---------------------------------------------------------
# VIEW 1: IT / InfoSec Admin Queue Dashboard
# ---------------------------------------------------------
if view_mode:
    st.title("👨‍💻 IT & InfoSec Escalation Queue")
    st.caption("Only tickets explicitly approved by the employee appear here.")
    
    if not st.session_state.submitted_tickets:
        st.info("The queue is currently empty. Approve an escalation in the Employee view to see it here.")
    else:
        for idx, ticket in enumerate(reversed(st.session_state.submitted_tickets)):
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"### 🎫 Ticket `{ticket['ticket_id']}` — {ticket['category']}")
                    st.markdown(f"**👤 Submitted By:** {ticket['employee_name']}")
                    st.markdown(f"**📄 Policy Reference:** `{ticket['policy_reference']}`")
                    st.markdown(f"**📝 Summary:** {ticket['summary']}")
                    st.markdown(f"**🔍 Reason:** {ticket['reason']}")
                with col_b:
                    st.markdown(f"**Priority:** `{ticket['priority']}`")
                    st.markdown(f"**Time:** `{ticket['timestamp']}`")
                    st.success(f"Status: {ticket['status']}")
                    if st.button("Acknowledge & Resolve", key=f"res_{idx}", use_container_width=True):
                        st.toast(f"Ticket {ticket['ticket_id']} marked as in-progress!")

# ---------------------------------------------------------
# VIEW 2: Employee Chat & Approval Card
# ---------------------------------------------------------
else:
    st.title("Enterprise IT Compliance Agent")
    st.markdown("Ask policy questions or report IT/InfoSec incidents. Escalations require your explicit approval.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            render_policy_sources(message.get("sources"))

    # Interactive Approval Card
    if st.session_state.pending_ticket:
        t_data = st.session_state.pending_ticket
        with st.container(border=True):
            st.subheader("📋 Escalation Request Approval")
            st.info("Review the details below before sending this ticket to the assigned team:")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Target Team:** `{t_data.get('target_approver_role', 'IT Support')}`")
                st.markdown(f"**Policy Citation:** `{t_data.get('policy_citation', 'N/A')}`")
            with c2:
                st.markdown(f"**Requester:** `Ziyad Almutairi`")
                st.markdown(f"**Status:** `Awaiting Your Approval`")
                
            st.markdown(f"**Summary:** {t_data.get('summary', '')}")
            st.markdown(f"**Escalation Reason:** {t_data.get('escalation_reason', '')}")
            
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("✅ Approve & Send Ticket", type="primary", use_container_width=True):
                    final_ticket = {
                        "ticket_id": f"IT-{uuid.uuid4().hex[:6].upper()}",
                        "status": "SUBMITTED",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "employee_name": "Ziyad Almutairi",
                        "category": t_data.get('target_approver_role', 'IT Support'),
                        "priority": "Critical" if "SOP-IT-002" in t_data.get('policy_citation', '') or "SOP-IT-008" in t_data.get('policy_citation', '') else "High",
                        "policy_reference": t_data.get('policy_citation', 'N/A'),
                        "summary": t_data.get('summary', ''),
                        "reason": t_data.get('escalation_reason', '')
                    }
                    st.session_state.submitted_tickets.append(final_ticket)
                    st.session_state.pending_ticket = None
                    
                    confirm_msg = f"✅ Escalation approved and sent to **{final_ticket['category']}** (Ticket ID: `{final_ticket['ticket_id']}`). You can switch the sidebar toggle to view it in the Admin Queue."
                    st.session_state.messages.append({"role": "assistant", "content": confirm_msg, "sources": []})
                    st.rerun()
                    
            with btn2:
                if st.button("❌ Reject / Cancel", use_container_width=True):
                    st.session_state.pending_ticket = None
                    cancel_msg = "❌ Escalation cancelled. No ticket was submitted."
                    st.session_state.messages.append({"role": "assistant", "content": cancel_msg, "sources": []})
                    st.rerun()

    if user_input := st.chat_input("Type your message (e.g., 'My company laptop was stolen', 'Can I install Notion?')..."):
        st.session_state.pending_ticket = None
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Checking IT & InfoSec policies..."):
                try:
                    response = agent_executor.invoke({
                        "input": user_input,
                        "chat_history": st.session_state.chat_history
                    })
                    output_text = response["output"]
                    
                    retrieved_sources = []
                    for action, observation in response.get("intermediate_steps", []):
                        if action.tool == "propose_escalation_ticket":
                            try:
                                st.session_state.pending_ticket = json.loads(observation)
                            except Exception:
                                pass
                        elif action.tool == "search_policy_database":
                            if observation != "NO_MATCHING_POLICY_FOUND":
                                retrieved_sources.append(observation)

                    st.markdown(output_text)
                    render_policy_sources(retrieved_sources)

                    message_data = {
                        "role": "assistant", 
                        "content": output_text,
                        "sources": retrieved_sources
                    }
                    st.session_state.chat_history.extend([
                        ("human", user_input),
                        ("ai", output_text)
                    ])
                    st.session_state.messages.append(message_data)
                    
                    if st.session_state.pending_ticket:
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")