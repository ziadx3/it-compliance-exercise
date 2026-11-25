# promptfoo_provider.py
import os
import json
from dotenv import load_dotenv
from layers.knowledge_layer import init_vector_database, get_retriever_tool
from layers.agent_layer import build_compliance_agent

load_dotenv()

# تهيئة النظام مرة واحدة عند بدء الاختبار
_vectorstore = init_vector_database()
_retriever_tool = get_retriever_tool(_vectorstore)
_agent_executor = build_compliance_agent(_retriever_tool)

def call_api(prompt, options, context):
    """دالة الربط القياسية التي يستدعيها Promptfoo لكل حالة اختبار"""
    try:
        response = _agent_executor.invoke({
            "input": prompt,
            "chat_history": []
        })
        
        output_text = response.get("output", "")
        tools_called = []
        
        for action, _ in response.get("intermediate_steps", []):
            tools_called.append(action.tool)
            
        # ندمج الرد النصي مع قائمة الأدوات التي تم استدعاؤها لكي يتحقق منها Promptfoo
        formatted_output = (
            f"{output_text}\n\n"
            f"[TOOLS_CALLED]: {', '.join(tools_called) if tools_called else 'NONE'}"
        )
        
        return {"output": formatted_output}
    except Exception as e:
        return {"error": str(e)}