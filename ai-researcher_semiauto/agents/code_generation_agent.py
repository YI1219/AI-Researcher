import requests
import os
from ..config import GEMINI_API_KEY

class CodeGenerationAgent:
    """
    Analyze the method/architecture design, generate prompts for each module, call the code_task_execute tool to generate code, and save the code to the execution environment.
    """
    def __init__(self, tool_server_url="http://localhost:8001/api/tool/execute", task_id_prefix="codegen_task", api_key=None, workspace_dir="code_workspace"): 
        self.tool_server_url = tool_server_url
        self.task_id_prefix = task_id_prefix
        self.api_key = api_key or GEMINI_API_KEY
        self.workspace_dir = workspace_dir

    def run(self, method_design, max_turns=10, allowed_tools=None, system_prompt=None):
        """
        Args:
            method_design (str): Output from MethodDesignAgent (method and architecture description).
        Returns:
            dict: Mapping from module name to code generation result.
        """
        # 1. Parse the method_design into modules/components (simple split by numbered/bulleted list or section headers)
        modules = self._extract_modules(method_design)
        results = {}
        for i, module in enumerate(modules):
            prompt = self._build_prompt(module)
            payload = {
                "task_id": f"{self.task_id_prefix}_{i+1}",
                "tool_name": "code_task_execute",
                "params": {
                    "prompt": prompt,
                    "workspace_dir": self.workspace_dir,
                    "api_key": self.api_key,
                    "max_turns": max_turns
                }
            }
            if allowed_tools:
                payload["params"]["allowed_tools"] = allowed_tools
            if system_prompt:
                payload["params"]["system_prompt"] = system_prompt
            response = requests.post(self.tool_server_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    results[module] = result.get("data", result)
                else:
                    results[module] = {"error": result.get("error")}
            else:
                results[module] = {"error": f"HTTP error: {response.status_code}, {response.text}"}
        return results

    def _extract_modules(self, method_design):
        """
        Naive split: split by numbered or bulleted lines, or section headers. Can be improved for more complex structures.
        """
        import re
        # Try to split by lines starting with numbers or bullets
        lines = method_design.splitlines()
        modules = []
        current = []
        for line in lines:
            if re.match(r"^\s*(\d+\.|- |• )", line):
                if current:
                    modules.append("\n".join(current).strip())
                    current = []
                current.append(line)
            else:
                current.append(line)
        if current:
            modules.append("\n".join(current).strip())
        # If only one module, treat the whole as one
        return [m for m in modules if m.strip()] or [method_design.strip()]

    def _build_prompt(self, module):
        """
        Build a code generation prompt for a single module/component.
        """
        return (
            f"Please implement the following module/component as described below.\n"
            f"Description:\n{module}\n"
            f"Requirements:\n- Write clean, well-documented code.\n- Follow best practices.\n- Output all code files and a README if needed."
        ) 