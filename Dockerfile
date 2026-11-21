# LangChain HITL Research Agent: Streamlit app in a container.
#
#   docker build -t hitl-research-agent .
#   docker run --rm -p 8501:8501 --env-file .env hitl-research-agent
#   open http://localhost:8501
#
# Keys (GROQ_API_KEY, TAVILY_API_KEY, optional GROQ_MODEL and
# MAX_RESEARCH_RUNS_PER_SESSION) come from the environment at run time.
# They are never baked into the image.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').status == 200 else 1)"

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
