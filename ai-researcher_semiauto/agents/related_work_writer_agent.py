import openai
from ..llm_utils import get_llm_responses
from ..config import GEMINI_API_KEY

class RelatedWorkWriterAgent:
    """
    Generate the Related Work and References sections of a research paper based on literature search results.
    """
    def __init__(self, model="gemini-2.5-flash-latest", latex_style=True):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.latex_style = latex_style
        self.related_work_system_message = (
            "You are an expert academic writer. Your job is to write the Related Work section of a research paper based on the provided literature search results. "
            "Write in clear, formal academic English. If latex_style is True, use LaTeX formatting."
        )
        self.references_system_message = (
            "You are an expert academic writer. Your job is to write the References section of a research paper based on the provided literature search results. "
            "Format the references in a standard academic style. If latex_style is True, use LaTeX/BibTeX formatting."
        )

    def write_related_work(self, rag_results, scholar_results, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        rag_summary = self._summarize_rag_results(rag_results)
        scholar_summary = self._summarize_scholar_results(scholar_results)
        user_prompt = (
            f"Please write the Related Work section of a research paper based on the following literature search results.\n"
            f"{'Use LaTeX format.' if self.latex_style else ''}\n"
            f"\nRAG Search Results:\n{rag_summary}\n"
            f"\nGoogle Scholar Search Results:\n{scholar_summary}\n"
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.related_work_system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else ""

    def write_references(self, rag_results, scholar_results, print_debug=False, message_history=None):
        if message_history is None:
            message_history = []
        rag_summary = self._summarize_rag_results(rag_results)
        scholar_summary = self._summarize_scholar_results(scholar_results)
        user_prompt = (
            f"Please write the References section of a research paper based on the following literature search results.\n"
            f"{'Use LaTeX/BibTeX format.' if self.latex_style else ''}\n"
            f"\nRAG Search Results:\n{rag_summary}\n"
            f"\nGoogle Scholar Search Results:\n{scholar_summary}\n"
        )
        content, _ = get_llm_responses(
            prompt=user_prompt,
            client=self.client,
            model=self.model,
            system_message=self.references_system_message,
            print_debug=print_debug,
            message_history=message_history,
        )
        return content[0].strip() if content else ""

    def _summarize_rag_results(self, rag_results):
        papers = rag_results.get("papers", [])
        summary = ""
        for i, paper in enumerate(papers[:5]):
            summary += f"{i+1}. {paper.get('title', '')} ({paper.get('publish_year', '')}): {paper.get('author', '')}. {paper.get('abstract', '')[:200]}...\n"
        return summary or "No RAG results."

    def _summarize_scholar_results(self, scholar_results):
        entries = scholar_results.get("entries", [])
        summary = ""
        for i, entry in enumerate(entries[:5]):
            title = entry.get('title', '')
            author = entry.get('author', '')
            year = entry.get('year', '')
            snippet = entry.get('snippet', '')
            summary += f"{i+1}. {title} ({year}): {author}. {snippet[:200]}...\n"
        return summary or "No Google Scholar results." 