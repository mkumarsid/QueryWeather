FROM python:3.11-slim

# System-level dependencies for Poetry and builds
RUN apt-get update && apt-get install -y curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set work directory
WORKDIR /app

# Copy only dependency files first to leverage Docker layer cache
COPY pyproject.toml poetry.lock* ./

# Disable virtualenvs (install in system site-packages)
RUN poetry config virtualenvs.create false

# Install dependencies only
RUN poetry install --no-root --no-interaction

# Copy the full source code into the image
COPY . .

# Expose both API and Streamlit ports
EXPOSE 8000 8501

# Run both FastAPI and Streamlit apps
CMD ["bash", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run uinterface/streamlit_dashboard.py --server.port 8501 --server.address 0.0.0.0"]
