from .base_agent import BaseAgent
from .paper_stage_agents import PaperAssemblerAgent

class QueryAnalysisAgent(BaseAgent):
    def analyze(self, topic, paper_structure=None, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are an academic search expert. The paper will follow this structure: {structure}. "
            f"Transform the following topic into a concise English academic search query for this paper.\nTopic: {topic}\nOutput only the query."
        )
        return self.call_llm(prompt, pre_advice=pre_advice)

class RAGSearchAgent(BaseAgent):
    def search(self, query, k=10, m=5, workflow_steps=None):
        params = {"query": query, "k": k, "m": m}
        return self.call_tool("rag_search_abstracts", params)

class GoogleScholarSearchAgent(BaseAgent):
    def search(self, query, pages=1, year_low=None, year_high=None, workflow_steps=None):
        params = {"query": query, "pages": pages}
        if year_low: params["year_low"] = year_low
        if year_high: params["year_high"] = year_high
        return self.call_tool("google_scholar_search", params)

class IdeaGenerationAgent(BaseAgent):
    def generate(self, topic, rag_results, scholar_results, paper_structure=None, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are a research idea generator. The paper will follow this structure: {structure}. "
            f"Based on the topic and search results, propose a novel, valuable, and feasible research idea that fits this structure.\n"
            f"Topic: {topic}\nRAG Results: {str(rag_results)[:500]}\nScholar Results: {str(scholar_results)[:500]}\n"
            f"Output 1-3 sentences."
        )
        return self.call_llm(prompt, pre_advice=pre_advice)

class NoveltyCheckAgent(BaseAgent):
    def check(self, idea, query, rag_k=10, rag_m=5, scholar_pages=1, year_low=None, year_high=None, paper_structure=None, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        rag_results = self.call_tool("rag_search_abstracts", {"query": query, "k": rag_k, "m": rag_m})
        scholar_results = self.call_tool("google_scholar_search", {"query": query, "pages": scholar_pages, "year_low": year_low, "year_high": year_high})
        prompt = (
            f"{steps_str}"
            f"You are a research novelty evaluator. The paper will follow this structure: {structure}. "
            f"Given the idea and search results, judge if the idea is novel and fits the paper structure.\n"
            f"Idea: {idea}\nRAG: {str(rag_results)[:500]}\nScholar: {str(scholar_results)[:500]}\n"
            f"Is the idea novel? Justify in 2-4 sentences."
        )
        return self.call_llm(prompt, pre_advice=pre_advice) 