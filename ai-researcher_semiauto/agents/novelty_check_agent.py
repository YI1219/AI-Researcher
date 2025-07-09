import openai
import requests
from ..llm_utils import get_llm_responses
from ..config import GEMINI_API_KEY

class NoveltyCheckAgent:
    """
    Check the novelty and originality of a research idea by searching both RAG and Google Scholar, then analyzing the results.
    """
    def __init__(self, model="gemini-2.5-flash-latest", tool_server_url="http://localhost:8001/api/tool/execute", task_id_prefix="novelty_check"):
        self.model = model
        self.client = openai.OpenAI(api_key=GEMINI_API_KEY)
        self.tool_server_url = tool_server_url
        self.task_id_prefix = task_id_prefix
        self.system_message = (
            "You are an expert research evaluator. Your job is to assess whether a given research idea is novel and original, based on the latest literature search results. "
            "You will be given a research idea, a search query, and two sources: (1) RAG-based academic search results, and (2) Google Scholar search results. "
            "Carefully analyze the results to determine if the idea is already well-studied or if it is innovative. "
            "Output a clear, concise English judgment: Is the idea novel? Is it already covered by existing works? Justify your answer in 2-4 sentences."
        )

    def run(self, idea, query, rag_k=10, rag_m=5, scholar_pages=1, year_low=None, year_high=None, print_debug=False, message_history=None):
        """
        Args:
            idea (str): The research idea to check.
            query (str): The search query string.
        Returns:
            str: LLM-generated novelty judgment.
        """
        if message_history is None:
            message_history = []
        # 1. Call RAG search
        rag_results = self._call_rag_search(query, rag_k, rag_m)
        # 2. Call Google Scholar search
        scholar_results = self._call_scholar_search(query, scholar_pages, year_low, year_high)
        # 3. Summarize results
        rag_summary = self._summarize_rag_results(rag_results)
        scholar_summary = self._summarize_scholar_results(scholar_results)
        # 4. Compose prompt
        user_prompt = (
            f"Research Idea: {idea}\n"
            f"\nSearch Query: {query}\n"
            f"\nRAG Search Results (key papers/abstracts):\n{rag_summary}\n"
            f"\nGoogle Scholar Search Results (key findings):\n{scholar_summary}\n"
            f"\nBased on the above, is the research idea novel and original? Is it already covered by existing works? "
            f"Provide a clear, concise English judgment (2-4 sentences)."
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

    def _call_rag_search(self, query, k, m):
        payload = {
            "task_id": f"{self.task_id_prefix}_rag",
            "tool_name": "rag_search_abstracts",
            "params": {
                "query": query,
                "k": k,
                "m": m
            }
        }
        response = requests.post(self.tool_server_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("data", {})
            else:
                raise RuntimeError(f"Tool server error (RAG): {result.get('error')}")
        else:
            raise RuntimeError(f"HTTP error (RAG): {response.status_code}, {response.text}")

    def _call_scholar_search(self, query, pages, year_low, year_high):
        params = {"query": query}
        if pages is not None:
            params["pages"] = pages
        if year_low is not None:
            params["year_low"] = year_low
        if year_high is not None:
            params["year_high"] = year_high
        payload = {
            "task_id": f"{self.task_id_prefix}_scholar",
            "tool_name": "google_scholar_search",
            "params": params
        }
        response = requests.post(self.tool_server_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("data", {})
            else:
                raise RuntimeError(f"Tool server error (Scholar): {result.get('error')}")
        else:
            raise RuntimeError(f"HTTP error (Scholar): {response.status_code}, {response.text}")

    def _summarize_rag_results(self, rag_results):
        papers = rag_results.get("papers", [])
        summary = ""
        for i, paper in enumerate(papers[:3]):
            summary += f"{i+1}. {paper.get('title', '')} ({paper.get('publish_year', '')}): {paper.get('abstract', '')[:200]}...\n"
        return summary or "No RAG results."

    def _summarize_scholar_results(self, scholar_results):
        entries = scholar_results.get("entries", [])
        summary = ""
        for i, entry in enumerate(entries[:3]):
            title = entry.get('title', '')
            snippet = entry.get('snippet', '')
            year = entry.get('year', '')
            summary += f"{i+1}. {title} ({year}): {snippet[:200]}...\n"
        return summary or "No Google Scholar results." 