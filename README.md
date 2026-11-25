# Research Agent with Human-in-the-Loop Approval

[![CI](https://github.com/michal329/LangChain_HITL_Research_Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/michal329/LangChain_HITL_Research_Agent/actions/workflows/ci.yml)

A research agent built with **LangChain** and **LangGraph** that searches the web with **Tavily**, groups the sources it finds, and **pauses for a human to approve them** in a **Streamlit** UI. Only after approval does it write a summary, based only on the approved sources, using a **Groq**-hosted LLM.

**Highlights**

- The run is paused and resumed through LangGraph's **Human-in-the-Loop middleware** and a **checkpointer**: approving resumes with an edited tool call that carries only the selected sources; rejecting resumes with the reviewer's feedback and sends the agent back to search.
- **Layered design**: UI, services and tools are separate, so the logic is tested without Streamlit.
- **22 pytest tests** that mock the LLM, the agent state and the tools, run in CI with no API keys.
- **Docker** image with a non-root user and a health check, built and smoke-tested in CI.

---

## 🗺️ Architecture

When the agent calls the `approve` tool, the HITL middleware interrupts the graph and hands control to the reviewer in the UI. The reviewer's decision is sent back as a resume command.

```mermaid
graph TD
    User([🧑‍💻 User]) -->|1. Submit Query| Streamlit[Streamlit Frontend]
    Streamlit -->|2. Run Agent| Agent[LangChain / Groq Agent]
    Agent -->|3. Search Query| SearchTool[Tavily Search Tool]
    SearchTool -->|4. Store Sources| SourceService[Source Service Cache]
    Agent -->|5. Propose Sources| ApproveTool[Approve Tool]
    ApproveTool -->|6. Interrupt Graph| HITL[HITL Middleware]
    HITL -->|7. Pause Execution| Streamlit
    Streamlit -->|8. Render Review Board| HITLPanel[UI HITL Panel]
    User -->|9. Select & Approve Sources| HITLPanel
    HITLPanel -->|10. Build Resume Command| ApprovalService[Approval Service]
    ApprovalService -->|11. Resume Graph with Approved Sources| Agent
    Agent -->|12. Generate Final Summary| User
```

---

## ✨ Features

- **Web research**: the agent searches with `Tavily Search` and groups the results for review.
- **Enforced human review**: the `approve` tool is interrupted by middleware, so the agent cannot summarize sources a human has not approved.
- **Granular Approval Board**:
  - Filter candidate sources in real-time.
  - Check/uncheck individual sources to select only the highest-quality references.
  - Approve to edit the tool arguments dynamically and resume execution.
  - Reject with direct textual feedback, directing the agent back to the search phase.
- **Service layer**: business logic is separate from UI rendering, which keeps it easy to unit test.

---

## 🛠️ Project Structure

```bash
LangChain_HITL_Research_Agent/
├── agents/
│   └── info_agent.py         # Agent graph initialization, system prompts, LLM setup
├── config/
│   └── settings.py           # Configuration manager for env settings & key validations
├── middleware/
│   └── hitl.py               # LangGraph Human-in-the-Loop interruption middleware
├── services/
│   ├── approval_service.py   # HITL logic, Command structures (Edit, Reject), filters
│   ├── chat_service.py       # Message polling, interruptions checks, graph invocation
│   ├── source_service.py     # Thread-safe dual-channel caching for search documents
│   └── state_service.py      # Streamlit session-state manager, thread UUID management
├── tools/
│   ├── approve_tool.py       # Intercepted tool definition for source submissions
│   └── search_tool.py        # Tavily integration, caching logic, format utilities
├── ui/
│   ├── chat.py               # Chat message rendering
│   ├── header.py             # Top status bar and header information
│   ├── sidebar.py            # Configuration details & state controllers
│   ├── styles.py             # CSS injected into Streamlit
│   └── hitl_panel.py         # Source selection board & action dispatchers
├── utils/
│   └── logger.py             # Logging setup
├── tests/                    # pytest suite with mocked LLM and tools
├── main.py                   # Main CLI entrypoint to launch Streamlit
├── app.py                    # Streamlit layout core execution thread
└── pytest.ini                # Test path mappings
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
- **Python 3.10 to 3.13** installed on your system.

### 2. Install Dependencies
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/michal329/LangChain_HITL_Research_Agent.git
cd LangChain_HITL_Research_Agent

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required libraries
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory by copying the example:

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
# Required credentials
GROQ_API_KEY=gsk_your_groq_api_key_here
TAVILY_API_KEY=tvly-your_tavily_api_key_here

# Optional model override (Default: llama-3.1-8b-instant)
GROQ_MODEL=llama-3.3-70b-versatile
```

> [!IMPORTANT]
> Both `GROQ_API_KEY` and `TAVILY_API_KEY` are **strictly required** for the agent to initialize. The app will prompt you with a visual validation error if keys are missing.

---

## 💻 Running the Application

To launch the Streamlit frontend dashboard, run the main entry point:

```bash
python main.py
```

This will spin up a local development server, typically opening at `http://localhost:8501`.

### 🐳 Running with Docker

```bash
docker build -t hitl-research-agent .
docker run --rm -p 8501:8501 --env-file .env hitl-research-agent
```

Then open `http://localhost:8501`. The keys are read from `.env` at run time and are never copied into the image (`.dockerignore` excludes `.env` and `.streamlit/secrets.toml`). The container runs as a non-root user and has a health check on Streamlit's `/_stcore/health` endpoint.

### ☁️ Deploying to Streamlit Community Cloud

The app is deployment-ready: pinned `requirements.txt`, `.streamlit/config.toml`, and settings that read from `st.secrets` as well as `.env`. See [DEPLOY.md](DEPLOY.md) for the step-by-step guide.

---

## 🧪 Running the Test Suite

22 tests cover the services and tools. The LLM, the agent state and the tools are mocked, so the tests need no API keys or network:

```bash
# Install the test dependencies, then run all unit tests with verbose outputs
pip install -r requirements-dev.txt
pytest -v
```

### 🔁 Continuous Integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push to `main` and on every pull request:

1. **Tests:** installs `requirements-dev.txt` and runs the suite with no API keys set.
2. **Docker:** builds the image, starts the container and waits for the health endpoint to answer.

---

## 📖 End-to-End Usage Example

A typical research session, step by step.

### Step 1: Submitting a Request
You type the following prompt into the chat input field:
> *"Gather sources on the latest advancements in solid-state battery technology and write a summary."*

### Step 2: Agent Gathers Information
1. The agent initializes, recognizes that it needs sources, and calls the `search` tool with the query: `"solid state battery technology advancements"`.
2. The `search` tool queries the Tavily API and fetches 5-6 sources containing page titles, URLs, and snippets.
3. The results are parsed and cached in the **Source Service**.
4. The agent categorizes these sources and attempts to submit them to the user by calling `approve(sources="...")`.

### Step 3: HITL Interruption (The Review Board)
At this point, the LangGraph engine intercepts the `approve` tool execution. The application switches states:
- The standard chat box is temporarily locked.
- The **Human-in-the-Loop review board** appears.

**What you will see in the UI:**
- **Source List**: Interactive cards showing the Title, URL, and a full snippet for each gathered source.
- **Search Filter**: A text input to query your results (e.g., typing *"Toyota"* will filter down to sources mentioning Toyota).
- **Control Buttons**:
  - `Select All` / `Deselect All` checkboxes.
  - `Approve Selected` (with indicators showing how many sources are checked, e.g., *"Approve Selected (4/5)"*).
  - `Provide Feedback & Search Again` text area and rejection button.

### Step 4: Making a Decision

#### Option A: Approve & Resume (Ideal Path)
1. You review the sources and uncheck Source #3 because it is a low-quality blog post.
2. You click **Approve Selected (4/5)**.
3. Under the hood:
   - The UI grabs the checked sources.
   - `services/approval_service.py` formats these sources into a structured block.
   - It builds an **Edit Command** modifying the `approve` tool call arguments with *only* these 4 sources.
   - The graph resumes.
4. The LLM receives the approved sources and writes a summary based only on them.

#### Option B: Reject & Revise (Redirect Path)
1. You review the sources and notice they are outdated.
2. In the feedback input box, you type:
   - *"These sources are from 2022. Please find recent breakthroughs from late 2025 or 2026."*
3. You click **Provide Feedback & Search Again**.
4. Under the hood:
   - `services/approval_service.py` builds a **Reject Command** carrying your text instructions.
   - The graph resumes, returning the rejection error message to the agent.
5. The agent reads your feedback, adjusts its query, and performs a *new* search on Tavily (e.g. `"solid state battery breakthroughs 2025 2026"`), bringing you back to **Step 3** with fresh, relevant sources!

---

## 💡 Best Practices & Customization

- **Model Selection**: For quick testing, `llama-3.1-8b-instant` is extremely fast. For complex multi-perspective summarization, set `GROQ_MODEL=llama-3.3-70b-versatile` in your `.env`.
- **Parallel Tool Protection**: The agent configuration explicitly sets `parallel_tool_calls=False`. This prevents the LLM from executing a search and trying to self-approve in the same cycle, ensuring reliable HITL flow.
- **New thread**: the **"New Thread"** button in the sidebar starts a fresh session with a new thread ID.
- **Checkpoint storage**: the checkpointer is LangGraph's in-memory `MemorySaver`, so paused runs do not survive a restart. A persistent checkpointer (SQLite or Postgres) would be the next step for production use.
