import openai
from ..llm_utils import get_llm_responses
from ..config import GEMINI_API_KEY

class ExperimentEvaluationAgent:
    """
    Evaluate whether the experiment results are satisfactory, and provide analysis and suggestions.
    """
    def __init__(self, model="gemini-2.5-flash-latest"):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.system_message = (
            "You are an expert research evaluator. Your job is to assess whether the experiment results are satisfactory based on the experiment plan and output. "
            "Provide a clear English analysis: Are the results ideal? Why or why not? Suggest possible improvements or next steps."
        )

    def run(self, experiment_plan, experiment_result, print_debug=False, message_history=None):
        """
        Args:
            experiment_plan (str): The experiment plan/description.
            experiment_result (str or dict): The output/result of the experiment.
        Returns:
            str: LLM-generated evaluation and suggestions.
        """
        if message_history is None:
            message_history = []
        # Format experiment result as string if dict
        if isinstance(experiment_result, dict):
            import json
            result_str = json.dumps(experiment_result, indent=2)
        else:
            result_str = str(experiment_result)
        user_prompt = (
            f"Experiment Plan:\n{experiment_plan}\n"
            f"\nExperiment Result/Output:\n{result_str}\n"
            f"\nBased on the above, is the experiment result satisfactory? Why or why not? Provide a clear English analysis and suggest possible improvements or next steps."
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else "" 