import openai
from .llm_utils import get_llm_responses
from .config import GEMINI_API_KEY


class QueryAnalysisAgent:
    """
    Analyze a given topic and generate a high-quality, concise search query suitable for RAG retrieval.
    """
    def __init__(self, model="gemini-2.5-flash-latest"):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.system_message = (
            "You are an academic information retrieval expert. Your job is to transform user topics into highly effective, precise, and concise academic search queries. "
            "Your goals are:\n"
            "1. Understand the core intent of the user's topic.\n"
            "2. Apply best practices in academic search to convert the topic into a clear, concise, and directly usable English search query.\n"
            "3. The query should avoid redundant or irrelevant words and highlight the main keywords.\n"
            "4. The query should be no longer than 20 words.\n"
            "5. Output only the final English search query, with no explanation or extra content."
        )

    def run(self, topic, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        user_prompt = (
            f"Transform the following topic into a high-quality English academic search query.\n"
            f"Topic: {topic}\n"
            f"Only output the final English search query. Do not provide any explanation."
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        # content is a list, return the first item
        return content[0].strip() if content else ""
