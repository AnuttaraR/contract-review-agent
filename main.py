"""
Entry point for the FastAPI webhook server.
For the Streamlit UI, run: streamlit run streamlit_app.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.storage.database import init_db
from app.knowledge_base.loader import load_knowledge_base

from app.api.webhook import app
import uvicorn

if __name__ == "__main__":
    init_db()
    load_knowledge_base()

    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
