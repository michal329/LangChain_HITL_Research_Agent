# Deploying to Streamlit Community Cloud

The app is ready to run on [Streamlit Community Cloud](https://share.streamlit.io) (free) straight from this GitHub repository.

## 1. Push the repository

Make sure `main` on GitHub contains `app.py`, `requirements.txt` and the `.streamlit/` folder. Never commit `.env` or `.streamlit/secrets.toml`; both are git-ignored.

## 2. Create the app

1. Sign in to <https://share.streamlit.io> with GitHub and click **Create app → Deploy a public app from GitHub**.
2. Fill in:
   - **Repository:** `michal329/LangChain_HITL_Research_Agent`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** pick a short subdomain, e.g. `michal-research-agent` → `https://michal-research-agent.streamlit.app`
3. Open **Advanced settings**:
   - **Python version:** `3.12`
   - **Secrets:** paste the contents of [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example) with your real keys:

     ```toml
     GROQ_API_KEY = "gsk_..."
     TAVILY_API_KEY = "tvly-..."
     GROQ_MODEL = "llama-3.3-70b-versatile"
     MAX_RESEARCH_RUNS_PER_SESSION = 5
     ```
4. Click **Deploy**. The first build takes a few minutes.

## 3. Protecting your API quota

The deployed app uses **your** Groq and Tavily keys for every visitor.

- `MAX_RESEARCH_RUNS_PER_SESSION` caps research runs per browser session (0 = unlimited).
- Both providers have free tiers with their own rate and usage limits. If a link gets heavy traffic, lower the cap or rotate the keys.
- To change a secret later: **App → Settings → Secrets**. The app restarts with the new values.

## Notes

- Settings are read from environment variables first (`.env` locally), then from `st.secrets`, so the same code runs locally and in the cloud.
- An app with no traffic goes to sleep after a while; the first visitor wakes it up in under a minute.
- Run the tests locally with `pip install -r requirements-dev.txt && pytest -v`.
