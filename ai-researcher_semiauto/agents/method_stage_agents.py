from .base_agent import BaseAgent
from .paper_stage_agents import PaperAssemblerAgent

class MethodDesignAgent(BaseAgent):
    def design(self, idea, paper_structure=None, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are a research method designer. The paper will follow this structure: {structure}. "
            f"Given the following research idea, design a detailed method that fits this structure (no code, just description):\n{idea}"
        )
        return self.call_llm(prompt, pre_advice=pre_advice)

class CodeGenerationAgent(BaseAgent):
    def generate_code(self, method_description, paper_structure=None, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are a code generation assistant. The paper will follow this structure: {structure}. "
            f"Write Python code to implement the following method, ensuring the code supports the paper's structure. Only output code.\nMethod: {method_description}"
        )
        return self.call_llm(prompt, pre_advice=pre_advice)

class ExperimentAgent(BaseAgent):
    def run_experiment(self, method_description, workspace_dir="code_workspace", paper_structure=None, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        # 1. Generate experiment plan
        plan_prompt = (
            f"{steps_str}"
            f"You are an experiment planner. The paper will follow this structure: {structure}. "
            f"Design an experiment for the following method. List datasets, metrics, and steps. No code.\nMethod: {method_description}"
        )
        plan = self.call_llm(plan_prompt, pre_advice=pre_advice)
        # 2. Find main script
        dir_data = self.call_tool("dir_list", {"dir_path": workspace_dir, "recursive": True})
        main_script = self._find_main_script(dir_data)
        if not main_script:
            return {"plan": plan, "error": "No main script found."}
        # 3. Execute code
        exec_result = self.call_tool("execute_code", {"file_path": main_script})
        return {"plan": plan, "main_script": main_script, "execution_result": exec_result}
    def _find_main_script(self, dir_data):
        files = []
        def _walk(d, prefix=""):
            for item in d.get("files", []):
                if item.endswith(".py"): files.append(f"{prefix}{item}")
            for subdir, subdata in d.get("dirs", {}).items():
                _walk(subdata, f"{prefix}{subdir}/")
        _walk(dir_data)
        for candidate in ["main.py", "app.py"]:
            for f in files:
                if f.endswith(candidate): return f
        return files[0] if files else None

class ExperimentEvaluationAgent(BaseAgent):
    def evaluate(self, experiment_result, paper_structure=None, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are an experiment evaluation expert. The paper will follow this structure: {structure}. "
            f"Evaluate the following experiment result and provide a concise analysis that fits the paper's structure.\nResult: {str(experiment_result)[:1000]}"
        )
        return self.call_llm(prompt, pre_advice=pre_advice) 