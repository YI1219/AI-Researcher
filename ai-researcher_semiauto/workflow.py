import time
from agents.query_agent import QueryAnalysisAgent
from agents.rag_search_agent import RAGSearchAbstractsAgent
from agents.google_scholar_agent import GoogleScholarSearchAgent
from agents.idea_agent import IdeaGenerationAgent
from agents.novelty_check_agent import NoveltyCheckAgent
from agents.method_design_agent import MethodDesignAgent
from agents.code_generation_agent import CodeGenerationAgent
from agents.experiment_agent import ExperimentAgent
from agents.experiment_evaluation_agent import ExperimentEvaluationAgent
from agents.paper_writer_agent import PaperWriterAgent
from agents.related_work_writer_agent import RelatedWorkWriterAgent
from agents.paper_section_writer_agent import PaperSectionWriterAgent
from agents.paper_assembler_agent import PaperAssemblerAgent

class ResearchWorkflow:
    def __init__(self, topic, workspace_dir="code_workspace"):
        self.topic = topic
        self.workspace_dir = workspace_dir
        # Instantiate all agents
        self.query_agent = QueryAnalysisAgent()
        self.rag_agent = RAGSearchAbstractsAgent()
        self.scholar_agent = GoogleScholarSearchAgent()
        self.idea_agent = IdeaGenerationAgent()
        self.novelty_agent = NoveltyCheckAgent()
        self.method_agent = MethodDesignAgent()
        self.coder_agent = CodeGenerationAgent(workspace_dir=workspace_dir)
        self.experiment_agent = ExperimentAgent(workspace_dir=workspace_dir)
        self.exp_eval_agent = ExperimentEvaluationAgent()
        self.paper_writer = PaperWriterAgent()
        self.related_writer = RelatedWorkWriterAgent()
        self.section_writer = PaperSectionWriterAgent()
        self.assembler = PaperAssemblerAgent()

    def run(self):
        # 1. Query generation
        query = self.query_agent.run(self.topic)
        # 2. Parallel: RAG & Google Scholar search
        rag_results = self.rag_agent.run(query)
        scholar_results = self.scholar_agent.run(query)
        # 3. Idea generation with up to 2 retries if not novel
        idea_history = []
        for idea_attempt in range(2):
            idea = self.idea_agent.run(self.topic, rag_results, scholar_results, message_history=idea_history)
            novelty_judgment = self.novelty_agent.run(idea, query)
            if "novel" in novelty_judgment.lower() and "not" not in novelty_judgment.lower():
                break
            idea_history.append({"role": "assistant", "content": idea})
            idea_history.append({"role": "user", "content": novelty_judgment})
        else:
            # If still not novel after 2 tries, use last idea
            pass
        # 4. Method and code design
        method_design = self.method_agent.run(idea)
        code_results = self.coder_agent.run(method_design)
        # 5. Experiment loop: up to 3 code/experiment attempts, else fallback to new idea
        for code_attempt in range(3):
            exp_result = self.experiment_agent.run(method_design)
            if "error" in exp_result.get("execution_result", {}):
                # Re-run code generation and experiment
                code_results = self.coder_agent.run(method_design)
                continue
            # 6. Experiment evaluation
            eval_result = self.exp_eval_agent.run(exp_result["plan"], exp_result["execution_result"])
            if "not ideal" in eval_result.lower() or "improve" in eval_result.lower():
                # Go back to method design
                method_design = self.method_agent.run(idea)
                code_results = self.coder_agent.run(method_design)
                continue
            # If experiment is ideal, break
            break
        else:
            # If failed 3 times, go back to idea generation
            return self.run()
        # 7. Paper writing (parallel)
        methods_section = self.paper_writer.write_methods(method_design)
        experiments_section = self.paper_writer.write_experiments(exp_result["plan"], exp_result["execution_result"])
        related_work = self.related_writer.write_related_work(rag_results, scholar_results)
        references = self.related_writer.write_references(rag_results, scholar_results)
        introduction = self.section_writer.write_introduction(idea, method_design, exp_result["execution_result"])
        conclusion = self.section_writer.write_conclusion(idea, method_design, exp_result["execution_result"])
        abstract = self.section_writer.write_abstract(idea, method_design, exp_result["execution_result"])
        # 8. Assemble paper
        title = self.topic
        full_paper = self.assembler.assemble(
            title=title,
            abstract=abstract,
            introduction=introduction,
            related_work=related_work,
            methods=methods_section,
            experiments=experiments_section,
            conclusion=conclusion,
            references=references
        )
        # 9. Save paper
        with open(f"{self.workspace_dir}/final_paper.tex", "w", encoding="utf-8") as f:
            f.write(full_paper)
        return full_paper 