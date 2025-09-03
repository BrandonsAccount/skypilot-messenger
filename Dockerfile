# syntax=docker/dockerfile:1
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY app .

RUN pip install --no-cache-dir -r requirements.txt

ENV LLM_API_URL="http://llm-api/endpoint"
ENV MCP_CLIENT_URL="http://mcp-client/execute"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]