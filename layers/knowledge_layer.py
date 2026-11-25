# layers/knowledge_layer.py
import os
import json
from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.tools import tool

def init_vector_database(persist_directory: str = "./chroma_db"):
    """
    Initializes the ChromaDB vector store with corporate IT and InfoSec policies,
    using OpenRouter embeddings.
    """
    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"
    )
    policy_docs = [
    # --- مجموعة 1: سياسات البرمجيات وحسابات المستخدمين (SOP-IT-001 إلى 012) ---
    Document(
        page_content="Software & AI Tools Installation Policy: Unauthorized external software and unapproved AI tools are strictly prohibited on company devices. Approved standard software includes: Microsoft 365, VS Code, Slack, and Google Chrome. Specialized tool or AI application requests require escalation to InfoSec and IT teams.",
        metadata={"policy_id": "SOP-IT-001", "section": "Section 1", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Lost or Stolen Company Devices Policy (Lost, stolen, missing laptop or mobile device): Employees must report lost or stolen devices immediately within 2 hours. Classified as a Critical Security Incident, mandating immediate escalation to InfoSec for remote data wipe and account freezing.",
        metadata={"policy_id": "SOP-IT-002", "section": "Section 2", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="Password & MFA Policy: Passwords must be updated every 90 days, at least 12 characters with mixed case, numbers, and symbols. MFA via Microsoft Authenticator is mandatory. Reset via password.company.com. Account lockouts or lost MFA devices must be escalated to IT Support.",
        metadata={"policy_id": "SOP-IT-003", "section": "Section 3", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Remote Access & VPN Policy: Connecting to internal systems from outside the office is permitted solely via Corporate VPN from within KSA. Public Wi-Fi without VPN is forbidden. Access from outside KSA requires prior approval and escalation to whitelist IP.",
        metadata={"policy_id": "SOP-IT-004", "section": "Section 4", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Admin Privileges & Data Access Policy: Accounts are provisioned with Standard User privileges only (Least Privilege Principle). Permanent Local Admin or direct production DB access is not granted. Elevated privileges require escalation and admin approval.",
        metadata={"policy_id": "SOP-IT-005", "section": "Section 5", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="External Storage & USB Media Policy: USB data transfer ports are disabled by default across endpoints. Use OneDrive or SharePoint for sharing. Physical USB drives or external HDDs require an escalation request to temporarily and securely unlock the port.",
        metadata={"policy_id": "SOP-IT-006", "section": "Section 6", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Hardware Replacement & Upgrade Policy: Laptops are replaced every 3 years. Hardware failure or physical damage is inspected by IT Support with a temporary replacement within 24 hours. Spec upgrades (RAM, monitors) require escalation for budget approval.",
        metadata={"policy_id": "SOP-IT-007", "section": "Section 7", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Email Security & Phishing Policy: Company emails must not be used for personal website registration or attachments over 25 MB. Suspected phishing emails or clicked malicious links must not be deleted; immediately escalate to InfoSec for threat isolation.",
        metadata={"policy_id": "SOP-IT-008", "section": "Section 8", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="Printer & Hardware Scanning Policy: Network printers require badge authentication to release physical paper print jobs. Scanning hardcopy pages is handled via local hardware scanner units.",
        metadata={"policy_id": "SOP-IT-009", "section": "Section 9", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Mobile Device Management (MDM) Policy: Personal smartphones accessing corporate email or Slack must have enterprise MDM profiles installed. Rooted or jailbroken mobile devices are automatically quarantined by the gateway.",
        metadata={"policy_id": "SOP-IT-010", "section": "Section 10", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Browser Extension & Add-on Policy: Installing unauthorized browser extensions, ad-blockers with external telemetry, or unverified developer toolbars on corporate Chrome is prohibited. IT maintains an approved extension whitelist.",
        metadata={"policy_id": "SOP-IT-011", "section": "Section 11", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Wi-Fi Guest Network & Personal Device Isolation Policy: Personal phones and visitor laptops must connect exclusively to the 'Company-Guest' Wi-Fi network. Accessing internal servers from guest Wi-Fi is strictly blocked.",
        metadata={"policy_id": "SOP-IT-012", "section": "Section 12", "rule_type": "STANDARD_APPROVAL"}
    ),

    # --- مجموعة 2: أمن الأجهزة والأمن الفيزيائي (SOP-IT-013 إلى 025) ---
    Document(
        page_content="Clean Desk & Screen Locking Policy: Employees must lock their workstation screens (Win+L) whenever leaving their desk. Physical ID badges must be worn visibly within office premises at all times.",
        metadata={"policy_id": "SOP-IT-013", "section": "Section 13", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Server Room & Data Center Access Policy: Entry to the main server room requires biometric authorization and prior security clearance. Escort is mandatory for external contractors visiting rack infrastructure.",
        metadata={"policy_id": "SOP-IT-014", "section": "Section 14", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="Peripherals & Home Office Equipment Policy: Monitors, docks, and keyboards issued for home offices remain company property. Relocating peripherals permanently requires updating asset inventory records via the IT portal.",
        metadata={"policy_id": "SOP-IT-015", "section": "Section 15", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Network Bandwidth & P2P Torrent Prohibition Policy: Using office internet connections for torrenting, P2P file sharing, or unauthorized media streaming is monitored by firewalls and triggers automated IT warnings.",
        metadata={"policy_id": "SOP-IT-016", "section": "Section 16", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="Audio and Video Recording Policy: Recording internal meetings, board discussions, or client calls on personal devices without participant consent or approved enterprise software is prohibited.",
        metadata={"policy_id": "SOP-IT-017", "section": "Section 17", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Biometric Attendance & Turnstile Policy: Sharing physical access cards, tailgating through turnstiles, or tampering with office biometric scanners constitutes a severe security breach requiring immediate escalation.",
        metadata={"policy_id": "SOP-IT-018", "section": "Section 18", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="Office Power Outage & UPS Battery Backup Policy: Workstations and critical desk hubs are backed up by uninterruptible power supplies (UPS). In case of grid failure, save active files immediately and shut down safely.",
        metadata={"policy_id": "SOP-IT-019", "section": "Section 19", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Conference Room Display & Casting Policy: Wireless screen casting in conference rooms must use secure PIN verification. Connecting personal unverified streaming dongles to boardroom displays is forbidden.",
        metadata={"policy_id": "SOP-IT-020", "section": "Section 20", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Physical Asset Disposal & E-Waste Policy: Broken hard drives, dead batteries, and obsolete IT hardware must be handed over to IT for certified secure shredding and green e-waste recycling. Throwing electronics in regular trash is banned.",
        metadata={"policy_id": "SOP-IT-021", "section": "Section 21", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Desk Phone & VoIP Extension Policy: Corporate VoIP desk phones are assigned to individual extensions. Transferring extensions or moving physical desk handsets across floors requires an IT support ticket.",
        metadata={"policy_id": "SOP-IT-022", "section": "Section 22", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Visitor IT Voucher Policy: External guests requiring temporary internet access must receive a restricted 24-hour Wi-Fi voucher generated through the reception IT portal.",
        metadata={"policy_id": "SOP-IT-023", "section": "Section 23", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Laptop Anti-Theft Lock Policy: Laptops left overnight in open office desks must be secured using physical Kensington security cables attached to desk anchors.",
        metadata={"policy_id": "SOP-IT-024", "section": "Section 24", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="External Vendor Maintenance Policy: Third-party technicians servicing office air conditioning or electrical units near server racks must be supervised by IT operations staff at all times.",
        metadata={"policy_id": "SOP-IT-025", "section": "Section 25", "rule_type": "ESCALATION_REQUIRED"}
    ),

    # --- مجموعة 3: سياسات الدعم الفني وإدارة التذاكر (SOP-IT-026 إلى 038) ---
    Document(
        page_content="IT Helpdesk SLA & Ticket Response Policy: Standard IT support requests have a 2-hour response target and 24-hour resolution window. Critical outages (network down, security alert) are addressed immediately 24/7.",
        metadata={"policy_id": "SOP-IT-026", "section": "Section 26", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Emergency IT Support Contact Policy: For urgent after-hours technical emergencies outside regular working hours, employees must contact the on-call IT escalation hotline rather than submitting standard web tickets.",
        metadata={"policy_id": "SOP-IT-027", "section": "Section 27", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Software License Procurement Policy: Department managers can approve standard software licenses up to 5,000 SAR. Higher software expenditures or enterprise subscriptions require executive IT procurement sign-off.",
        metadata={"policy_id": "SOP-IT-028", "section": "Section 28", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Workstation Operating System Patch Policy: OS security updates (Windows Patch Tuesday / macOS updates) must be installed within 7 days of release. Auto-reboots are scheduled during off-hours.",
        metadata={"policy_id": "SOP-IT-029", "section": "Section 29", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Antivirus & Endpoint Protection Policy: Corporate antivirus and EDR agents (CrowdStrike/Defender) must remain active and updated. Disabling or tampering with endpoint security agents triggers an immediate InfoSec alert.",
        metadata={"policy_id": "SOP-IT-030", "section": "Section 30", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="Email Alias and Distribution List Policy: Creating new company email distribution lists or shared mailboxes requires approval from department heads and IT administration to prevent spam and organizational clutter.",
        metadata={"policy_id": "SOP-IT-031", "section": "Section 31", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="VPN Certificate Renewal Policy: Corporate VPN user certificates expire annually and must be renewed through the IT self-service portal two weeks prior to expiration to prevent access interruption.",
        metadata={"policy_id": "SOP-IT-032", "section": "Section 32", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Internal File Share & Confidential Document Storage Policy: Where should I store company confidential documents? Company confidential documents, reports, and files must be stored exclusively in managed shared folders on the network attached storage (NAS) or approved secure repositories like OneDrive and SharePoint. Storing confidential documents on personal cloud drives or public folders is strictly prohibited.",
        metadata={"policy_id": "SOP-IT-033", "section": "Section 33", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="IT Loaner Laptop Policy: Employees whose laptops are under repair can request a temporary loaner device from IT Helpdesk for up to 14 business days, subject to availability.",
        metadata={"policy_id": "SOP-IT-034", "section": "Section 34", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Video Conferencing Equipment Policy: Meeting room cameras, microphones, and speakers must be tested weekly. Reporting hardware malfunctions requires logging an urgent IT maintenance ticket.",
        metadata={"policy_id": "SOP-IT-035", "section": "Section 35", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Shared Workstation & Kiosk Policy: Shared reception or factory floor kiosks must be locked with generic operator credentials. Personal files must never be stored on multi-user public workstations.",
        metadata={"policy_id": "SOP-IT-036", "section": "Section 36", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="IT Equipment Relocation Policy: Moving desktop setups or office phone units between desks or offices independently is prohibited; IT personnel must perform physical relocations to update asset registry maps.",
        metadata={"policy_id": "SOP-IT-037", "section": "Section 37", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Software Demo & Sandbox Environment Policy: Setting up temporary sandbox environments for testing third-party software requires IT approval and must be decommissioned within 30 days.",
        metadata={"policy_id": "SOP-IT-038", "section": "Section 38", "rule_type": "ESCALATION_REQUIRED"}
    ),

    # --- مجموعة 4: سياسات الامتثال، الطوارئ، ونهاية الخدمة (SOP-IT-039 إلى 050) ---
    Document(
        page_content="Employee Offboarding & Asset Return Policy: Resigning or terminated employees must return all company laptops, access cards, tokens, and peripherals to HR and IT on their final working day. Accounts are disabled at 5:00 PM.",
        metadata={"policy_id": "SOP-IT-039", "section": "Section 39", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="New Hire IT Onboarding Policy: New employees receive standardized hardware, credentials, and mandatory cybersecurity awareness training within their first 3 days of employment via the learning portal.",
        metadata={"policy_id": "SOP-IT-040", "section": "Section 40", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Corporate Email Legal Hold Policy: When an employee is involved in legal audits or investigations, their mailbox is placed on permanent legal hold preventing deletion of any incoming or outgoing messages.",
        metadata={"policy_id": "SOP-IT-041", "section": "Section 41", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="International Travel IT Security Policy: Taking corporate laptops outside Saudi Arabia requires notifying IT Security 48 hours prior to travel to ensure compliance with regional firewall geofencing and export rules.",
        metadata={"policy_id": "SOP-IT-042", "section": "Section 42", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Corporate Password Sharing Prohibition Policy: Sharing password credentials, admin keys, or MFA verification codes with colleagues, supervisors, or external parties is a severe disciplinary offense.",
        metadata={"policy_id": "SOP-IT-043", "section": "Section 43", "rule_type": "CRITICAL_ESCALATION"}
    ),
    Document(
        page_content="IT Disaster Recovery Backup Policy: End-user documents stored in corporate OneDrive undergo automated daily cloud backups with 30-day versioning and point-in-time recovery capabilities.",
        metadata={"policy_id": "SOP-IT-044", "section": "Section 44", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Shadow IT & Unapproved Cloud Storage Policy: Subscribing to consumer cloud storage (Dropbox, Mega) or unauthorized SaaS tools using corporate credit cards without IT review constitutes a policy violation.",
        metadata={"policy_id": "SOP-IT-045", "section": "Section 45", "rule_type": "ESCALATION_REQUIRED"}
    ),
    Document(
        page_content="Internal Messaging & Collaboration Security Policy: Official business communications must occur via Microsoft Teams or Slack Enterprise. Using unencrypted consumer apps for sensitive data is banned.",
        metadata={"policy_id": "SOP-IT-046", "section": "Section 46", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Cybersecurity Awareness Training Policy: All staff must complete annual cybersecurity training modules and simulated phishing tests within 14 days of assignment. Non-compliance results in network access restriction.",
        metadata={"policy_id": "SOP-IT-047", "section": "Section 47", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="IT System Maintenance Window Policy: Routine server maintenance, network upgrades, and firewall reboots must be executed strictly during approved weekend maintenance windows (Friday 12:00 AM to 4:00 AM).",
        metadata={"policy_id": "SOP-IT-048", "section": "Section 48", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="Green IT & Power Management Policy: Workstations and office monitors must be configured to enter sleep mode after 15 minutes of user inactivity to optimize energy consumption and enterprise sustainability.",
        metadata={"policy_id": "SOP-IT-049", "section": "Section 49", "rule_type": "STANDARD_APPROVAL"}
    ),
    Document(
        page_content="IT Policy Review & Audit Compliance Policy: All IT standard operating procedures are reviewed annually by the IT Steering Committee and audited by internal compliance teams to ensure alignment with Saudi standards.",
        metadata={"policy_id": "SOP-IT-050", "section": "Section 50", "rule_type": "STANDARD_APPROVAL"}
    )
]
    vectorstore = Chroma.from_documents(
        documents=policy_docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vectorstore

def openrouter_rerank(query: str, candidates: list, top_n: int = 2) -> list:
    """
    Reranks candidate policy clauses using openai/gpt-4o-mini via OpenRouter API 
    to act as a semantic Cross-Encoder.
    """
    if not candidates:
        return []

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )

    passages_str = "\n".join([f"ID: {c['id']} | Content: {c['text']}" for c in candidates])
    
    prompt = f"""You are a precise IT Compliance Reranker. 
Given the user query: "{query}"
Rank the following candidate policy clauses based on their exact semantic relevance to the query.
Return ONLY a JSON object with a key "ranked_ids" containing a list of the top {top_n} most relevant IDs ordered from highest relevance to lowest, like this: {{"ranked_ids": [id1, id2]}}

Candidates:
{passages_str}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        ranked_ids = data.get("ranked_ids", data.get("ids", []))
        
        id_to_candidate = {c['id']: c for c in candidates}
        reranked = [id_to_candidate[i] for i in ranked_ids if i in id_to_candidate]
        
        return reranked[:top_n] if reranked else candidates[:top_n]
    except Exception as e:
        print(f"OpenRouter Rerank Error: {e}")
        return candidates[:top_n]

def get_retriever_tool(vectorstore):
    """Creates a two-stage retrieval tool: Vector Search (Recall) + OpenRouter LLM Reranking (Precision)."""
    @tool
    def search_policy_database(query: str) -> str:
        """Searches the corporate IT policy vector database using OpenRouter and reranks results for maximum precision.
        Always call this tool first before making any compliance decision."""
        
        results = vectorstore.similarity_search_with_relevance_scores(query, k=10)
        
        candidates = []
        for idx, (doc, score) in enumerate(results):
            if score >= 0.15:
                candidates.append({
                    "id": idx,
                    "text": doc.page_content,
                    "meta": doc.metadata
                })

        if not candidates:
            return "NO_MATCHING_POLICY_FOUND"

        reranked_candidates = openrouter_rerank(query, candidates, top_n=3)

        valid_clauses = []
        for item in reranked_candidates:
            meta = item["meta"]
            valid_clauses.append(
                f"POLICY_ID: {meta['policy_id']} | SECTION: {meta['section']} | TYPE: {meta['rule_type']}\nCONTENT: {item['text']}"
            )
        
        if not valid_clauses:
            return "NO_MATCHING_POLICY_FOUND"
            
        return "\n---\n".join(valid_clauses)

    return search_policy_database