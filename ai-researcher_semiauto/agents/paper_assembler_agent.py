class PaperAssemblerAgent:
    """
    Assemble all sections into a complete research paper (optionally in LaTeX format).
    """
    def __init__(self, latex_style=True):
        self.latex_style = latex_style

    def assemble(self, title, abstract, introduction, related_work, methods, experiments, conclusion, references):
        """
        Args:
            title (str): Paper title.
            abstract (str): Abstract section.
            introduction (str): Introduction section.
            related_work (str): Related Work section.
            methods (str): Methods section.
            experiments (str): Experiments/Results section.
            conclusion (str): Conclusion section.
            references (str): References section.
        Returns:
            str: The full paper as a single string (LaTeX or plain text).
        """
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