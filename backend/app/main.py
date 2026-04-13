from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.routers import auth, costs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando API CloudCost IQ...")
    try:
        init_db()
        logger.info("Banco de dados inicializado")
    except Exception as e:
        logger.warning(f"Inicialização do banco de dados ignorada: {e}")
    yield
    logger.info("Encerrando API CloudCost IQ...")

app = FastAPI(
    title="CloudCost IQ API",
    description="Análise inteligente de custos em nuvem para infraestrutura AWS",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(costs.router)

@app.get("/")
async def root():
    return {
        "name": "CloudCost IQ API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
