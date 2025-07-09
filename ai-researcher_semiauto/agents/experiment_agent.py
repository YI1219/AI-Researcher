import requests
import os
from ..config import GEMINI_API_KEY
from ..llm_utils import get_llm_responses

class ExperimentAgent:
    """
    Given a method/code design, generate an experimental plan, execute the experiment in the code workspace, and collect results.
    """
    def __init__(self, tool_server_url="http://localhost:8001/api/tool/execute", task_id_prefix="experiment_task", workspace_dir="code_workspace", model="gemini-2.5-flash-latest"):
        self.tool_server_url = tool_server_url
        self.task_id_prefix = task_id_prefix
        self.workspace_dir = workspace_dir
        self.model = model
        self.client = None  # Replace with actual LLM client if needed
        self.system_message = (
            "You are an expert research assistant. Your job is to design and execute experiments for a given research method/codebase. "
            "You should generate a clear experimental plan (including datasets, metrics, and steps), then run the experiment in the provided code workspace, and collect the results."
        )

    def run(self, method_design, print_debug=False, message_history=None):
        """
        Args:
            method_design (str): The method/code design description.
        Returns:
            dict: Experiment plan and execution results.
        """
        if message_history is None:
            message_history = []
        # 1. Generate experiment plan using LLM
        plan_prompt = (
            f"Given the following method/code design, please design a detailed experimental plan.\n"
            f"Describe the datasets, evaluation metrics, and step-by-step experimental procedure.\n"
            f"Do NOT write any code, just output the plan.\n"
            f"\nMethod/Code Design:\n{method_design}\n"
        )
        plan_content, _ = get_llm_responses(
            prompt=plan_prompt,
            client=self.client,
            model=self.model,
            system_message=self.system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        experiment_plan = plan_content[0].strip() if plan_content else ""
        # 2. Try to find the main script to run (assume main.py or app.py or user-specified)
        main_script = self._find_main_script()
        if not main_script:
            return {"plan": experiment_plan, "error": "No main script found in workspace."}
        # 3. Execute the main script using execute_code
        exec_result = self._execute_code(main_script)
        return {"plan": experiment_plan, "main_script": main_script, "execution_result": exec_result}

    def _find_main_script(self):
        # List files in workspace_dir, look for main.py, app.py, or the first .py file
        payload = {
            "task_id": f"{self.task_id_prefix}_listdir",
            "tool_name": "dir_list",
            "params": {
                "dir_path": self.workspace_dir,
                "recursive": True
            }
        }
        response = requests.post(self.tool_server_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                files = self._extract_py_files(result.get("data", {}))
                for candidate in ["main.py", "app.py"]:
                    for f in files:
                        if f.endswith(candidate):
                            return f
                return files[0] if files else None
        return None

    def _extract_py_files(self, dir_data):
        # Recursively extract .py files from dir_list output
        files = []
        def _walk(d, prefix=""):
            for item in d.get("files", []):
                if item.endswith(".py"):
                    files.append(os.path.join(prefix, item))
            for subdir, subdata in d.get("dirs", {}).items():
                _walk(subdata, os.path.join(prefix, subdir))
        _walk(dir_data)
        return files

    def _execute_code(self, script_path):
        payload = {
            "task_id": f"{self.task_id_prefix}_exec",
            "tool_name": "execute_code",
            "params": {
                "file_path": script_path
            }
        }
        response = requests.post(self.tool_server_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("data", {})
            else:
                return {"error": result.get("error")}
        else:
            return {"error": f"HTTP error: {response.status_code}, {response.text}"} 