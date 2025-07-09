# AI-Researcher

AI-Researcher is an automated research assistant that leverages Gemini's API and multiple specialized agents to generate research papers from an initial topic. The workflow includes literature search, idea generation, experiment design, code generation, LaTeX writing, and PDF compilation, all overseen by a mentor agent.

## Workflow Steps
1. **Idea Agent**: Generates literature search queries and ideas based on the topic.
2. **Experience Agent**: Designs methods and experiments, generates code requirements, and obtains experimental results.
3. **Method Write Agent & Experience Write Agent**: Write the methods and experiments sections in LaTeX.
4. **Related Works Write Agent & Reference Write Agent**: Search for related works and references, and write these sections in LaTeX.
5. **Abstract Write Agent & Instruction Write Agent**: Write the abstract and introduction.
6. **LaTeX Splicing & PDF Generation**: Combine all LaTeX sections and compile to PDF.

A mentor agent supervises each step, deciding whether to continue or regenerate, and can update prompts as needed. 