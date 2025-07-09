import openai
from ..llm_utils import get_llm_responses
from ..config import GEMINI_API_KEY

class PaperWriterAgent:
    """
    Generate the Methods and Experiments/Results sections of a research paper based on method design and experiment results.
    """
    def __init__(self, model="gemini-2.5-flash-latest", latex_style=True):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.latex_style = latex_style
        self.methods_system_message = (
            "You are an expert academic writer. Your job is to write the Methods section of a research paper based on the provided method design. "
            "Write in clear, formal academic English. If latex_style is True, use LaTeX formatting."
        )
        self.experiments_system_message = (
            "You are an expert academic writer. Your job is to write the Experiments/Results section of a research paper based on the provided experiment plan and results. "
            "Write in clear, formal academic English. If latex_style is True, use LaTeX formatting."
        )

    def write_methods(self, method_design, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        user_prompt = (
            f"Please write the Methods section of a research paper based on the following method design.\n"
            f"{'Use LaTeX format.' if self.latex_style else ''}\n"
            f"\nMethod Design:\n{method_design}\n"
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.methods_system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else ""

    def write_experiments(self, experiment_plan, experiment_result, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        # Format experiment result as string if dict
        if isinstance(experiment_result, dict):
            import json
            result_str = json.dumps(experiment_result, indent=2)
        else:
            result_str = str(experiment_result)
        user_prompt = (
            f"Please write the Experiments/Results section of a research paper based on the following experiment plan and results.\n"
            f"{'Use LaTeX format.' if self.latex_style else ''}\n"
            f"\nExperiment Plan:\n{experiment_plan}\n"
            f"\nExperiment Result/Output:\n{result_str}\n"
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.experiments_system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else "" 