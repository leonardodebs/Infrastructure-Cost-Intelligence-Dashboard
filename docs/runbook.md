# Runbook Operacional - CloudCost IQ

## Procedimentos de Startup

### Iniciar Todos os Serviços

```bash
cd cloudcost-iq
docker-compose up -d
```

### Verificar Status dos Serviços

```bash
docker-compose ps
```

Saída esperada:
```
NAME                IMAGE               STATUS           PORTS
cloudcostiq-db      postgres:15        Up (healthy)    5432->5432
cloudcostiq-backend cloudcostiq-backend Up               0.0.0.0:8000->8000/tcp
cloudcostiq-frontend cloudcostiq-frontend Up               0.0.0.0:3000->3000/tcp
```

### Verificar Saúde da API

```bash
curl http://localhost:8000/health
```

Resposta esperada: `{"status":"healthy"}`

### Acessar Interface Web

Url: `http://localhost:3000`

## Procedimentos de Shutdown

### Parar Todos os Serviços

```bash
docker-compose down
```

### Parar com Remoção de Volumes

```bash
docker-compose down -v
```

### Shutdown de Emergência

```bash
docker-compose kill
```

## Procedimentos de Restart

### Restartar Serviço Específico

```bash
docker-compose restart backend
docker-compose restart frontend
docker-compose restart db
```

### Rebuild e Restart

```bash
docker-compose up -d --build
```

## Troubleshooting

### Problema: Backend Não Inicia

**Sintoma:** Container em estado `Restarting`

**Diagnóstico:**
```bash
docker-compose logs backend
```

**Causas Comuns:**
1. Banco não está pronto - Verificar se db está `healthy`
2. Variáveis de ambiente ausentes - Verificar `.env`
3. Porta 8000 em uso - Verificar processo

**Solução:**
```bash
# Verificar logs
docker-compose logs backend

# Verificar variáveis
docker-compose exec backend env | grep -E "AWS|DATABASE|SECRET"

# Verificar porta
netstat -ano | findstr :8000
```

### Problema: Banco Não Conecta

**Sintoma:** Erro de conexão no backend

**Diagnóstico:**
```bash
docker-compose logs backend | grep "connection"
docker-compose exec db pg_isready
```

**Solução:**
```bash
# Reiniciar banco
docker-compose restart db

# Verificar credenciais
docker-compose exec db psql -U postgres -c "SELECT 1"
```

### Problema: Erro de Credenciais AWS

**Sintoma:** `ClientError` ou `AccessDenied`

**Diagnóstico:**
```bash
docker-compose logs backend | grep -i "aws\|credential"
```

**Solução:**
1. Verificar variáveis AWS no `.env`:
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

2. Validar credenciais:
```bash
aws sts get-caller-identity
```

3. Verificar permissões IAM

### Problema: Frontend Não Carrega

**Sintoma:** Página em branco ou erro de connexion

**Diagnóstico:**
```bash
docker-compose logs frontend
curl http://localhost:3000
```

**Solução:**
```bash
# Verificar variável de API
docker-compose exec frontend env | grep REACT_APP

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Problema: Lentidão na API

**Sintoma:** Timeout em requisições

**Diagnóstico:**
```bash
docker-compose stats
docker-compose logs backend
```

**Solução:**
```bash
# Aumentar recursos
docker-compose up -d --scale backend=2

# Verificar queries lentas
docker-compose exec db psql -U postgres -d cloudcostiq -c "SELECT * FROM pg_stat_activity"
```

### Problema: CORS Erro

**Sintoma:** `Cross-Origin Request Blocked`

**Solução:**
Editar `main.py` e especificar origens:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Monitoramento

### Verificar Uso de Recursos

```bash
docker stats
```

### Verificar Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Verificar Tamanho do Banco

```bash
docker-compose exec db psql -U postgres -d cloudcostiq -c "SELECT pg_size_pretty(pg_database_size('cloudcostiq'));"
```

## Backup e Restore

### Backup do Banco

```bash
docker-compose exec db pg_dump -U postgres cloudcostiq > backup_$(date +%Y%m%d).sql
```

### Restore do Banco

```bash
docker-compose exec -T db psql -U postgres cloudcostiq < backup_YYYYMMDD.sql
```

### Backup de Volumes

```bash
docker run --rm -v cloudcostiq_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Manutenção

### Limpar Containers Parados

```bash
docker container prune -f
```

### Limpar Imagens Não Usadas

```bash
docker image prune -f
```

### Limpar Cache Docker

```bash
docker system prune -f
```

### Atualizar Aplicação

```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### rolling Update

```bash
docker-compose up -d --build
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

## Comandos Úteis

### Acessar Shell do Backend

```bash
docker-compose exec backend sh
```

### Acessar Shell do Banco

```bash
docker-compose exec db psql -U postgres -d cloudcostiq
```

### Verificar Variáveis de Ambiente

```bash
docker-compose exec backend env
```

### Listar Tabelas do Banco

```bash
docker-compose exec db psql -U postgres -d cloudcostiq -c "\dt"
```

### Verificar Ultimas Requisições

```bash
docker-compose logs --tail=100 backend | grep "GET\|POST"
```

## Emergência

### Trava Completa do Sistema

1. Verificar logs: `docker-compose logs > emergencia.log`
2. Parar tudo: `docker-compose down`
3. Verificar recursos: `docker stats`
4. Limpar e reiniciar: `docker system prune -f && docker-compose up -d`

### Recuperar Senha de Admin

```bash
docker-compose exec backend python -c "from app.services.auth import get_password_hash; print(get_password_hash('nova_senha'))"
# Atualizar no banco manualmente
```

### Reinstalação do Zero

```bash
docker-compose down -v
rm -rf postgres_data
docker-compose up -d --build
```