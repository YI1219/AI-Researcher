import os
import logging
import time
from agents.idea_stage_agents import (
    QueryAnalysisAgent, RAGSearchAgent, GoogleScholarSearchAgent,
    IdeaGenerationAgent, NoveltyCheckAgent
)
from agents.method_stage_agents import (
    MethodDesignAgent, CodeGenerationAgent, ExperimentAgent, ExperimentEvaluationAgent
)
from agents.paper_stage_agents import (
    PaperWriterAgent, RelatedWorkWriterAgent, PaperSectionWriterAgent, PaperAssemblerAgent
)
from agents.functional_agents import ResultValidationAgent

WORKFLOW_STEPS = [
    "QueryAnalysis", "RAGSearch", "GoogleScholarSearch", "IdeaGeneration", "NoveltyCheck",
    "MethodDesign", "CodeGeneration", "Experiment", "ExperimentEvaluation",
    "RelatedWorkWriting", "PaperWriting", "PaperAssembly"
]
PAPER_GOAL = "Generate a novel, high-quality, and complete academic research paper on the given topic, following standard academic structure and best practices."

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ResearchWorkflow")

# 通用重试装饰器
def retry_on_exception(max_retries=10, delay=2, logger=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if logger:
                        logger.warning(f"Exception in {func.__name__} (attempt {attempt}/{max_retries}): {e}")
                    if attempt == max_retries:
                        if logger:
                            logger.error(f"Max retries reached for {func.__name__}. Raising exception.")
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

STEP_DEPENDENCIES = {
    "QueryAnalysis": [],
    "RAGSearch": ["query"],
    "GoogleScholarSearch": ["query"],
    "IdeaGeneration": ["rag_results", "scholar_results"],
    "NoveltyCheck": ["idea", "query"],
    "MethodDesign": ["idea"],
    "CodeGeneration": ["method_design"],
    "Experiment": ["method_design"],
    "ExperimentEvaluation": ["experiment"],
    "RelatedWorkWriting": ["rag_results", "scholar_results"],
    "PaperWriting": ["method_design", "experiment"],
    "PaperAssembly": ["methods_section", "experiments_section", "related_work"],
}

class ResearchWorkflow:
    def __init__(self, topic, workspace_dir="code_workspace"):
        self.topic = topic
        self.workspace_dir = workspace_dir
        os.makedirs(self.workspace_dir, exist_ok=True)
        # Instantiate all agents
        self.query_agent = QueryAnalysisAgent()
        self.rag_agent = RAGSearchAgent()
        self.scholar_agent = GoogleScholarSearchAgent()
        self.idea_agent = IdeaGenerationAgent()
        self.novelty_agent = NoveltyCheckAgent()
        self.method_agent = MethodDesignAgent()
        self.coder_agent = CodeGenerationAgent()
        self.experiment_agent = ExperimentAgent()
        self.exp_eval_agent = ExperimentEvaluationAgent()
        self.paper_writer = PaperWriterAgent()
        self.related_writer = RelatedWorkWriterAgent()
        self.section_writer = PaperSectionWriterAgent()
        self.assembler = PaperAssemblerAgent()
        self.validator = ResultValidationAgent()

    @retry_on_exception(max_retries=10, delay=2, logger=logger)
    def safe_llm_call(self, agent_method, *args, **kwargs):
        return agent_method(*args, **kwargs)

    @retry_on_exception(max_retries=10, delay=2, logger=logger)
    def safe_tool_call(self, agent_method, *args, **kwargs):
        return agent_method(*args, **kwargs)

    def run(self):
        step_data = {}
        pre_advices = {step: None for step in WORKFLOW_STEPS}
        step_idx = 0

        while step_idx < len(WORKFLOW_STEPS):
            step = WORKFLOW_STEPS[step_idx]
            logger.info(f"Starting step: {step}")
            try:
                # --- 1. QueryAnalysis ---
                if step == "QueryAnalysis":
                    result = self.safe_llm_call(
                        self.query_agent.analyze,
                        self.topic,
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    step_data["query"] = result
                    step_idx += 1
                    continue

                # --- 2. RAGSearch ---
                elif step == "RAGSearch":
                    result = self.safe_tool_call(
                        self.rag_agent.search,
                        step_data["query"]
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["rag_results"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 3. GoogleScholarSearch ---
                elif step == "GoogleScholarSearch":
                    result = self.safe_tool_call(
                        self.scholar_agent.search,
                        step_data["query"]
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["scholar_results"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 4. IdeaGeneration ---
                elif step == "IdeaGeneration":
                    result = self.safe_llm_call(
                        self.idea_agent.generate,
                        self.topic,
                        step_data["rag_results"],
                        step_data["scholar_results"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["idea"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 5. NoveltyCheck ---
                elif step == "NoveltyCheck":
                    result = self.safe_llm_call(
                        self.novelty_agent.check,
                        step_data["idea"],
                        step_data["query"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok") and "novel" in result.lower() and "not" not in result.lower():
                        step_data["novelty"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 6. MethodDesign ---
                elif step == "MethodDesign":
                    result = self.safe_llm_call(
                        self.method_agent.design,
                        step_data["idea"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["method_design"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 7. CodeGeneration ---
                elif step == "CodeGeneration":
                    result = self.safe_llm_call(
                        self.coder_agent.generate_code,
                        step_data["method_design"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["code"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 8. Experiment ---
                elif step == "Experiment":
                    result = self.safe_llm_call(
                        self.experiment_agent.run_experiment,
                        step_data["method_design"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["experiment"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 9. ExperimentEvaluation ---
                elif step == "ExperimentEvaluation":
                    result = self.safe_llm_call(
                        self.exp_eval_agent.evaluate,
                        step_data["experiment"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["experiment_evaluation"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 10. RelatedWorkWriting ---
                elif step == "RelatedWorkWriting":
                    result = self.safe_llm_call(
                        self.related_writer.write_related_work,
                        self.topic,
                        step_data["rag_results"],
                        step_data["scholar_results"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    validation = self.safe_llm_call(
                        self.validator.validate,
                        result, workflow_steps=WORKFLOW_STEPS, paper_goal=PAPER_GOAL
                    )
                    if validation.strip().startswith("ok"):
                        step_data["related_work"] = result
                        step_idx += 1
                    else:
                        restart, advice = self._parse_validation(validation)
                        restart_checked = self._find_first_missing_dependency(restart, step_data)
                        if restart_checked != restart:
                            logger.warning(f"Step {step} failed validation, but {restart} depends on {restart_checked}. Restarting from {restart_checked}.")
                        restart = restart_checked
                        pre_advices[restart] = advice
                        step_idx = WORKFLOW_STEPS.index(restart)
                        continue

                # --- 11. PaperWriting ---
                elif step == "PaperWriting":
                    methods_section = self.safe_llm_call(
                        self.paper_writer.write_methods,
                        step_data["method_design"],
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    experiments_section = self.safe_llm_call(
                        self.paper_writer.write_experiments,
                        step_data["experiment"].get("plan", ""),
                        step_data["experiment"].get("execution_result", ""),
                        pre_advice=pre_advices[step],
                        workflow_steps=WORKFLOW_STEPS
                    )
                    step_data["methods_section"] = methods_section
                    step_data["experiments_section"] = experiments_section
                    step_idx += 1

                # --- 12. PaperAssembly ---
                elif step == "PaperAssembly":
                    title = self.topic
                    abstract = "TODO: Generate abstract"
                    introduction = "TODO: Generate introduction"
                    conclusion = "TODO: Generate conclusion"
                    references = "TODO: Generate references"
                    full_paper = self.assembler.assemble(
                        title=title,
                        abstract=abstract,
                        introduction=introduction,
                        related_work=step_data.get("related_work", ""),
                        methods=step_data.get("methods_section", ""),
                        experiments=step_data.get("experiments_section", ""),
                        conclusion=conclusion,
                        references=references
                    )
                    with open(f"{self.workspace_dir}/final_paper.tex", "w", encoding="utf-8") as f:
                        f.write(full_paper)
                    logger.info(f"Paper assembled and saved to {self.workspace_dir}/final_paper.tex")
                    return full_paper
            except Exception as e:
                logger.error(f"Exception in step {step}: {e}")
                raise

    def _parse_validation(self, validation):
        # 解析validator返回的RESTART_TO和advice
        lines = validation.strip().splitlines()
        restart = None
        advice = None
        for line in lines:
            if line.startswith("RESTART_TO:"):
                restart = line.replace("RESTART_TO:", "").strip()
            elif line.startswith("Proactive advice:"):
                advice = line.replace("Proactive advice:", "").strip()
        return restart, advice

    def _find_first_missing_dependency(self, step, step_data, visited=None):
        if visited is None:
            visited = set()
        if step in visited:
            return step  # 防止递归环
        visited.add(step)
        for dep in STEP_DEPENDENCIES.get(step, []):
            if dep not in step_data:
                # 找到哪个step负责产出dep
                for s, deps in STEP_DEPENDENCIES.items():
                    if dep in deps:
                        return self._find_first_missing_dependency(s, step_data, visited)
                return step  # dep没有更早的生产者，直接回退到当前step
        return step

# 用法示例
if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI for protein folding"
    workflow = ResearchWorkflow(topic)
    workflow.run() 