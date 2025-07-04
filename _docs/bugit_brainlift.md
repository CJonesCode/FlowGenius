# Brainlift Document: BugIt

### Starting Question

Why do I have to switch context so much to handle new features or bugs?

### Rationale

Solutions like Linear are often too large and team-focused for small projects or personal workflows. There's a clear need for a lightweight, CLI-first tool tailored for individual or discrete bug and feature management.

### Brainlift Chronology

- **Q (Product Design):** What kind of tool should I build?
  - **A:** A CLI-first tool that improves my personal workflow or hobby.
  - **Notes:** Considered C# + Mono, bug tracking, documenting bugs in flow.
- **Q (Tech Fit):** Is LangGraph or n8n a better fit?
  - **A:** LangGraph. It supports stateful, conditional AI workflows — perfect for classification/tagging pipelines.
- **Q (Language Choice):** Should I use C# or Python for the CLI?
  - **A:** Python. Shared codebase with LangGraph, faster iteration, simpler integration.
- **Q (LangGraph Support):** Is LangGraph available in languages other than Python?
  - **A:** No. LangGraph is Python-only.
- **Q (Architecture):** Is an HTTP server required to use LangGraph?
  - **A:** No. It can be embedded directly into a Python CLI using function calls.
- **Q (Data Format):** Should we use JSON or YAML for saving bug data?
  - **A:** JSON. Easier to parse, safer for LLM ingestion, more widely supported.
- **Q (Data Format):** Will pretty-printing JSON cause issues when supplying to tools?
  - **A:** No, it's safe when parsed with standard tools (e.g., `json.load()`). Pretty-printed JSON improves readability and works fine with LangGraph and LLMs. Compact output may be added as an optional CLI flag.
- **Q (Market Research):** Are there similar tools?
  - **A:** Kind of. Linear, GitHub CLI, Notion AI, etc. overlap partially, but none focus on in-flow CLI-based bug capture with LangGraph AI.
- **Q (Positioning):** How does this differ from Linear?
  - **A:** Linear is team/project oriented, GUI-first, and cloud-based. BugIt is CLI-first, dev-centric, AI-structured, and local.
- **Q (Future Integration):** Should I integrate it into Cursor via VSCode plugin?
  - **A:** Eventually yes, but MVP will focus on CLI and may later add an MCP interface.
- **Q (Data Design):** Should bugs be indexed by ID or position?
  - **A:** Use UUIDs or hashes, not positional indexes. This avoids race conditions and ordering problems, especially when supporting future async features.
- **Q (Data Identity):** Should the UUID be stored in the JSON itself?
  - **A:** Yes. Storing the UUID in the JSON ensures consistent referencing, traceability, and enables deduplication, clustering, or syncing workflows.
- **Q (Refactor Design):** How can we design for a future switch to `@langchain/langgraph`?
  - **A:** Encapsulate LangGraph logic in a clean Python interface (e.g., a single `run_bugit_graph()` function), avoid tightly coupling data flow to internal Python-only types, and keep the graph modular so a future TS implementation can follow the same state transitions.
- **Q (Architecture & Stack Planning):** Should we use the new TypeScript version of LangGraph?
  - **A:** For now, no. The MVP is based on the mature Python version of LangGraph. However, a TypeScript version (`@langchain/langgraph`) has been published and may be used in the future for tighter integration with web tools or unified stack design.
- **Q (LLM Configuration):** How should a user specify which API key or models to use?
  - **A:** Support command-line flags, environment variables (`export BUGIT_API_KEY=...`), and a local `.bugitrc` config file. Avoid global config fallback and `.env` loading to keep scope simple.
- **Q (LLM Routing):** How do we support multiple models?
  - **A:** In the future, `.bugitrc` may define a model map by task (e.g. `title`, `tagging`, `default`) and support multiple API keys. For the MVP, we will support only a single model and API key.
- **Q (UX/Discoverability):** How can we help users avoid needing to remember model names?
  - **A:** Add a `bugit models` command that outputs suggested model IDs and links to provider docs. This can be hardcoded for the MVP and upgraded to a live-fetching command as a stretch goal.
- **Q (LLM Usability):** Is there a `latest` model string?
  - **A:** No, most providers (OpenAI, Anthropic) require explicit model names. Some names like `gpt-4` may act as floating aliases, but should not be relied upon. Explicit model strings (e.g., `gpt-4o`, `claude-3-opus-20240229`) must be used.

### Resources Used

- OpenAI Model Reference: [https://platform.openai.com/docs/models](https://platform.openai.com/docs/models)
- LangGraph docs: [https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- Typer CLI framework: [https://typer.tiangolo.com/](https://typer.tiangolo.com/)
- Cursor compatibility with Python: personal experience and testing
- Linear/GitHub CLI comparisons
- LLM integration knowledge from LangChain, OpenAI JSON-mode usage
- Tom Tarpey's FAQ-GISTS: [https://github.com/Gauntlet-AI/FAQ-GISTS](https://github.com/Gauntlet-AI/FAQ-GISTS) – curated practical references for Git, CLI tools, Python, VSCode, and LLM integration
- Command-Line UX in 2020: [https://medium.com/relay-sh/command-line-ux-in-2020-e537018ebb69](https://medium.com/relay-sh/command-line-ux-in-2020-e537018ebb69) – best practices for CLI user experience
- 12-Factor CLI Apps: [https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46) – design principles for robust CLI tools
- Cisco Blog on CLI UX: [https://outshift.cisco.com/blog/cli-ux](https://outshift.cisco.com/blog/cli-ux) – analysis of CLI user experience and design pitfalls
- CLIG.dev: [https://clig.dev/](https://clig.dev/) – guide to good CLI design, focusing on usability and conventions

