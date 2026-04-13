# API FastAPI para análise de custos AWS
# Endpoints: autenticação, custos, anomalias, conformidade de tags

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.routers import auth, costs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gerencia o ciclo de vida da aplicação (startup e shutdown)
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

# Aplicação FastAPI com lifespan gerenciado
app = FastAPI(
    title="CloudCost IQ API",
    description="Análise inteligente de custos em nuvem para infraestrutura AWS",
    version="1.0.0",
    lifespan=lifespan
)

# Configura CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui routers da aplicação
app.include_router(auth.router)
app.include_router(costs.router)

# Endpoint raiz com informações da API
@app.get("/")
async def root():
    return {
        "name": "CloudCost IQ API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check para verificação de status
@app.get("/health")
async def health_check():
    return {"status": "healthy"}