from .base_agent import BaseAgent

class PaperAssemblerAgent:
    DEFAULT_STRUCTURE = [
        "Title", "Abstract", "Introduction", "Related Work", "Methods", "Experiments and Results", "Conclusion", "References"
    ]
    def __init__(self, latex_style=True):
        self.latex_style = latex_style
    def assemble(self, title, abstract, introduction, related_work, methods, experiments, conclusion, references):
        def safe(section, name):
            return section if section and section.strip() else f"[No {name} provided]"
        title = safe(title, "Title")
        abstract = safe(abstract, "Abstract")
        introduction = safe(introduction, "Introduction")
        related_work = safe(related_work, "Related Work")
        methods = safe(methods, "Methods")
        experiments = safe(experiments, "Experiments/Results")
        conclusion = safe(conclusion, "Conclusion")
        references = safe(references, "References")
        if self.latex_style:
            return self._assemble_latex(title, abstract, introduction, related_work, methods, experiments, conclusion, references)
        else:
            return self._assemble_plain(title, abstract, introduction, related_work, methods, experiments, conclusion, references)
    def _assemble_latex(self, title, abstract, introduction, related_work, methods, experiments, conclusion, references):
        return f"""
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{graphicx}}
\\usepackage{{cite}}
\\title{{{title}}}
\\begin{{document}}
\\maketitle
\\begin{{abstract}}
{abstract}
\\end{{abstract}}
\\section{{Introduction}}
{introduction}
\\section{{Related Work}}
{related_work}
\\section{{Methods}}
{methods}
\\section{{Experiments and Results}}
{experiments}
\\section{{Conclusion}}
{conclusion}
\\section*{{References}}
{references}
\\end{{document}}
"""
    def _assemble_plain(self, title, abstract, introduction, related_work, methods, experiments, conclusion, references):
        return f"""
{title}

Abstract
--------
{abstract}

Introduction
------------
{introduction}

Related Work
------------
{related_work}

Methods
-------
{methods}

Experiments and Results
-----------------------
{experiments}

Conclusion
----------
{conclusion}

References
----------
{references}
"""

class PaperWriterAgent(BaseAgent):
    def write_methods(self, method_design, paper_structure=None, latex_style=True, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are writing the 'Methods' section of a research paper. "
            f"The overall paper structure is: {structure}. "
            f"Ensure your writing fits seamlessly into this structure and references other sections where appropriate. "
            f"{'Use LaTeX.' if latex_style else ''}\n"
            f"Method Design: {method_design}"
        )
        return self.call_llm(prompt, system_prompt="You are an academic paper writer.", pre_advice=pre_advice)
    def write_experiments(self, experiment_plan, experiment_result, paper_structure=None, latex_style=True, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are writing the 'Experiments and Results' section of a research paper. "
            f"The overall paper structure is: {structure}. "
            f"Ensure your writing fits seamlessly into this structure and references other sections where appropriate. "
            f"{'Use LaTeX.' if latex_style else ''}\n"
            f"Experiment Plan: {experiment_plan}\nResult: {str(experiment_result)[:1000]}"
        )
        return self.call_llm(prompt, system_prompt="You are an academic paper writer.", pre_advice=pre_advice)

class PaperSectionWriterAgent(BaseAgent):
    def write_section(self, section_name, content, paper_structure=None, latex_style=True, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are writing the '{section_name}' section of a research paper. "
            f"The paper follows this structure: {structure}. "
            f"Ensure this section is coherent with the rest of the paper and references other sections if needed. "
            f"{'Use LaTeX.' if latex_style else ''}\n"
            f"Content: {content}"
        )
        return self.call_llm(prompt, system_prompt="You are an academic section writer.", pre_advice=pre_advice)

class RelatedWorkWriterAgent(BaseAgent):
    def write_related_work(self, topic, rag_results, scholar_results, paper_structure=None, latex_style=True, pre_advice=None, workflow_steps=None):
        structure = paper_structure or PaperAssemblerAgent.DEFAULT_STRUCTURE
        steps = workflow_steps or []
        steps_str = f"The full workflow consists of the following steps: {steps}.\n" if steps else ""
        prompt = (
            f"{steps_str}"
            f"You are writing the 'Related Work' section for a research paper on '{topic}'. "
            f"The paper structure is: {structure}. "
            f"Use the following search results to ensure the section fits the context of the whole paper. "
            f"{'Use LaTeX.' if latex_style else ''}\n"
            f"RAG: {str(rag_results)[:500]}\nScholar: {str(scholar_results)[:500]}"
        )
        return self.call_llm(prompt, system_prompt="You are a related work summarizer.", pre_advice=pre_advice) 