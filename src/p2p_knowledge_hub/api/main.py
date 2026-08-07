from fastapi import FastAPI
from p2p_knowledge_hub.api.routes.documents import router as documents_router

app = FastAPI()

app.include_router(documents_router)
