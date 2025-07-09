import openai
from ..llm_utils import get_llm_responses
from ..config import GEMINI_API_KEY

class IdeaGenerationAgent:
    """
    Generate a research paper idea based on the outputs of RAG and Google Scholar search agents.
    """
    def __init__(self, model="gemini-2.5-flash-latest"):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.system_message = (
            "You are an expert research assistant. Your job is to generate innovative, valuable, and feasible research paper ideas based on the latest literature search results. "
            "You will be given two sources: (1) RAG-based academic search results, and (2) Google Scholar search results. "
            "Analyze the key topics, trends, and gaps from both sources, and propose a concise, original research idea. "
            "Your output should be a clear, actionable research idea (1-3 sentences), suitable for a new academic paper."
        )

    def run(self, topic, rag_results, scholar_results, print_debug=False, message_history=None):
        """
        Args:
            topic (str): The original research topic.
            rag_results (dict): Output from RAGSearchAbstractsAgent.
            scholar_results (dict): Output from GoogleScholarSearchAgent.
        Returns:
            str: Generated research idea.
        """
        if message_history is None:
            message_history = []
        # Format the search results for the prompt
        rag_summary = self._summarize_rag_results(rag_results)
        scholar_summary = self._summarize_scholar_results(scholar_results)
        user_prompt = (
            f"Topic: {topic}\n"
            f"\nRAG Search Results (key papers/abstracts):\n{rag_summary}\n"
            f"\nGoogle Scholar Search Results (key findings):\n{scholar_summary}\n"
            f"\nBased on the above, propose a novel, valuable, and feasible research paper idea. "
            f"Your answer should be 1-3 sentences, clear and actionable."
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

    def _summarize_rag_results(self, rag_results):
        # Extract and format top 3 papers from RAG results
        papers = rag_results.get("papers", [])
        summary = ""
        for i, paper in enumerate(papers[:3]):
            summary += f"{i+1}. {paper.get('title', '')} ({paper.get('publish_year', '')}): {paper.get('abstract', '')[:200]}...\n"
        return summary or "No RAG results."

    def _summarize_scholar_results(self, scholar_results):
        # Try to extract and format top 3 results from Google Scholar output
        # This part may need adjustment based on actual output structure
        entries = scholar_results.get("entries", [])
        summary = ""
        for i, entry in enumerate(entries[:3]):
            title = entry.get('title', '')
            snippet = entry.get('snippet', '')
            year = entry.get('year', '')
            summary += f"{i+1}. {title} ({year}): {snippet[:200]}...\n"
        return summary or "No Google Scholar results." 