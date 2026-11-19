FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MCP_HOST=0.0.0.0 MCP_PORT=9000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home mcp
COPY server.py repository.py queries.py ./
USER 10001
EXPOSE 9000
CMD ["python","server.py"]
