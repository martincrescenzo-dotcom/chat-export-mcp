FROM python:3.12-slim
WORKDIR /app
COPY chat_export_mcp.py .
ENTRYPOINT ["python3", "/app/chat_export_mcp.py"]
