import requests
from llm_utils.llm_client import LLMClient, ModelType, ChatMessage

class BaseAgent:
    def __init__(self, model=ModelType.GPT_4O, tool_server_url="http://localhost:8001/api/tool/execute", api_key=None, task_id_prefix="agent_task"):
        self.model = model
        self.llm_client = LLMClient(api_key=api_key)
        self.tool_server_url = tool_server_url
        self.task_id_prefix = task_id_prefix

    def call_llm(self, message, system_prompt=None, history=None, pre_advice=None, **kwargs):
        # 如果有预建议，拼接到message前
        if pre_advice and isinstance(pre_advice, str) and pre_advice.strip():
            message = f"[Proactive advice for better results]: {pre_advice.strip()}\n" + message
        chat_kwargs = dict(
            message=message,
            model=self.model,
            system_prompt=system_prompt
        )
        if history:
            chat_kwargs["history"] = [ChatMessage(**msg) if isinstance(msg, dict) else msg for msg in history]
        chat_kwargs.update(kwargs)
        response = self.llm_client.chat(**chat_kwargs)
        result_str = response.content.strip() if response and response.content else ""
        print(f"[LLM Call] result preview: {result_str[:200]}")
        return result_str

    def call_tool(self, tool_name, params, task_id=None):
        payload = {
            "task_id": task_id or f"{self.task_id_prefix}_{tool_name}",
            "tool_name": tool_name,
            "params": params
        }
        response = requests.post(self.tool_server_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            # 打印简要结果
            print(f"[Tool Call] tool: {tool_name}, success: {result.get('success')}, data preview: {str(result.get('data'))[:200]}")
            if result.get("success"):
                return result.get("data", {})
            else:
                raise RuntimeError(f"Tool server error: {result.get('error')}")
        else:
            print(f"[Tool Call] tool: {tool_name}, HTTP error: {response.status_code}")
            raise RuntimeError(f"HTTP error: {response.status_code}, {response.text}")