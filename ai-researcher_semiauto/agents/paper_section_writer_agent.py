import openai
from ..llm_utils import get_llm_responses
from ..config import GEMINI_API_KEY

class PaperSectionWriterAgent:
    """
    Generate Introduction, Conclusion, and Abstract sections of a research paper based on idea, method, and experiment results.
    """
    def __init__(self, model="gemini-2.5-flash-latest", latex_style=True):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.latex_style = latex_style
        self.intro_system_message = (
            "You are an expert academic writer. Your job is to write the Introduction section of a research paper based on the provided idea, method, and experiment results. "
            "Write in clear, formal academic English. If latex_style is True, use LaTeX formatting."
        )
        self.conclusion_system_message = (
            "You are an expert academic writer. Your job is to write the Conclusion section of a research paper based on the provided idea, method, and experiment results. "
            "Write in clear, formal academic English. If latex_style is True, use LaTeX formatting."
        )
        self.abstract_system_message = (
            "You are an expert academic writer. Your job is to write the Abstract of a research paper based on the provided idea, method, and experiment results. "
            "Write in clear, formal academic English. If latex_style is True, use LaTeX formatting."
        )

    def write_introduction(self, idea, method_design, experiment_result, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        user_prompt = (
            f"Please write the Introduction section of a research paper based on the following information.\n"
            f"{'Use LaTeX format.' if self.latex_style else ''}\n"
            f"\nResearch Idea:\n{idea}\n"
            f"\nMethod Design:\n{method_design}\n"
            f"\nExperiment Result/Output:\n{experiment_result}\n"
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.intro_system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else ""

    def write_conclusion(self, idea, method_design, experiment_result, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        user_prompt = (
            f"Please write the Conclusion section of a research paper based on the following information.\n"
            f"{'Use LaTeX format.' if self.latex_style else ''}\n"
            f"\nResearch Idea:\n{idea}\n"
            f"\nMethod Design:\n{method_design}\n"
            f"\nExperiment Result/Output:\n{experiment_result}\n"
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.conclusion_system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else ""

    def write_abstract(self, idea, method_design, experiment_result, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        user_prompt = (
            f"Please write the Abstract of a research paper based on the following information.\n"
            f"{'Use LaTeX format.' if self.latex_style else ''}\n"
            f"\nResearch Idea:\n{idea}\n"
            f"\nMethod Design:\n{method_design}\n"
            f"\nExperiment Result/Output:\n{experiment_result}\n"
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.abstract_system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else "" 