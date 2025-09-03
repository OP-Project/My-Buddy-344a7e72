# 🌤️📈📄 hey_buddy — Multi-Agent Assistant

A modular multi-agent AI assistant (Weather, Stock, PDF) built around CrewAI-style orchestration. This README prioritizes the repository's existing links, default port, and Linux/Windows commands.

## 🚀 Features
- Weather Agent: current conditions, forecasts, auto/manual location, lifestyle recommendations
- Stock Agent: price data, trend analysis, company info and AI-generated insights
- PDF Analyzer: robust text extraction and AI summarization

## 🛠️ Quick Setup (Linux & Windows)

1. Clone
   ```bash
   git clone <repository-url>
   cd hey_buddy
   ```

2. Create virtual environment

   Linux / macOS:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   Windows (cmd.exe):
   ```cmd
   python -m venv .venv
   .\.venv\Scripts\activate.bat
   ```

3. Install
   ```bash
   pip install -r requirements.txt
   ```

4. Environment variables (`.env` in repo root)
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   WEATHER_API_KEY=your_weatherapi_key_here
   IPINFO_TOKEN=your_ipinfo_token_here
   SERPER_API_KEY=your_serper_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 🔑 Useful Links (priority)
- Google Gemini / API keys: https://makersuite.google.com/app/apikey
- Swagger UI (FastAPI docs): http://localhost:8000/docs
- Redoc (alternate): http://localhost:8000/redoc
- WeatherAPI: https://www.weatherapi.com/
- IPInfo (optional): https://ipinfo.io/
- Serper (optional): https://serper.dev/
- (Optional) Google Cloud SDK: https://cloud.google.com/sdk

## 🚀 Run (Localhost on port 8000)

- Run the primary app (if using the Python entrypoint):
  ```bash
  python3 src/main.py
  ```
  or on Windows:
  ```powershell
  python src/main.py
  ```

- If using FastAPI with uvicorn (recommended for Swagger UI on port 8000):
  ```bash
  pip install "uvicorn[standard]"
  uvicorn src.main:app --reload --port 8000
  ```
  Windows (PowerShell/cmd) same commands apply.

- If a Gradio UI is added, update its port to 8000 (or use the default Gradio port). Open:
  http://localhost:8000

## 🏗️ Project layout (important files)
- src/main.py — entry point (Gradio / FastAPI integration)
- src/orchestrator/ — orchestration logic
- src/orchestrator/agents/ — agent definitions, tools, prompts, sub-agents
- src/clients/ — external API clients (Gemini, etc.)
- src/config/ — app settings and logging
- src/validation/ — input/output schemas

## 🗂️ Branch Naming Convention

| Type       | Suggested Pattern              | Example                   | Use Case                                                               |
| ---------- | ------------------------------ | ------------------------- | ---------------------------------------------------------------------- |
| Feature    | `feature/<short-description>`  | `feature/user-auth`       | New functionality or enhancements visible to users                     |
| Bugfix     | `bugfix/<short-description>`   | `bugfix/fix-login-crash`  | Fixing a defect that is not urgent                                     |
| Hotfix     | `hotfix/<short-description>`   | `hotfix/security-patch`   | Critical fix that needs immediate release                              |
| Release    | `release/v<version>`           | `release/v1.0.0`          | Preparing a production release                                         |
| Experiment | `exp/<short-description>`      | `exp/test-new-ui`         | Trying out an idea or prototype                                        |
| Chore      | `chore/<short-description>`    | `chore/update-logger`     | Maintenance tasks, configs, dependencies, non-user-facing improvements |
| Docs       | `docs/<short-description>`     | `docs/add-setup-guide`    | Documentation updates or additions                                     |
| Test       | `test/<short-description>`     | `test/add-api-unit-tests` | Adding or improving tests                                              |
| Refactor   | `refactor/<short-description>` | `refactor/prompt-engine`  | Restructuring code without changing functionality                      |

## 🔧 Customization
- Add agents in `src/orchestrator/agents/` and tools in `src/orchestrator/agents/tools/`
- Change config in `src/config/app_settings.py`
- Update prompts in `src/orchestrator/agents/prompts/`

## 🐛 Troubleshooting (common)
- API key errors: confirm `.env` values and quotas
- Weather errors: verify location string and WEATHER_API_KEY
- Stock errors: check ticker correctness and network
- PDF errors: ensure file is not password-protected