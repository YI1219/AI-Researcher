import openai
from ..llm_utils import get_llm_responses
from ..config import GEMINI_API_KEY

class MethodDesignAgent:
    """
    Given a research idea, use LLM to design the research methodology and propose a high-level code architecture (if needed), but do NOT generate any code.
    """
    def __init__(self, model="gemini-2.5-flash-latest"):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.system_message = (
            "You are an expert research engineer. Your job is to design research methodologies and propose high-level code architectures for new research ideas. "
            "You should only provide method design, algorithmic steps, and code structure suggestions (if needed). Do NOT write or output any code. "
            "Your answer should be clear, structured, and actionable for a research team."
        )

    def run(self, idea, print_debug=False, message_history=None):
        """
        Args:
            idea (str): The research idea to design for.
        Returns:
            str: LLM-generated method and architecture design (no code).
        """
        if message_history is None:
            message_history = []
        user_prompt = (
            f"Research Idea: {idea}\n"
            f"\nPlease design a detailed research methodology and, if appropriate, propose a high-level code architecture for this idea. "
            f"Do NOT write or output any code. Only provide method design, algorithmic steps, and code structure suggestions."
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