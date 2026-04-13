# Documentação de Arquitetura - CloudCost IQ

## Visão Geral do Sistema

O CloudCost IQ é uma plataforma de análise inteligente de custos de infraestrutura em nuvem AWS. A arquitetura segue um padrão de microsserviços com três componentes principais: frontend React, backend FastAPI e banco de dados PostgreSQL.

## Arquitetura de Componentes

### Camada de Frontend
- **Tecnologia:** React 18 + Vite
- **Styling:** Tailwind CSS
- **Comunicação:** API REST via Axios
- **Porta:** 3000 (exposta)
- **Funcionalidades:** Dashboard de custos, Login, visualização de relatórios

### Camada de Backend
- **Tecnologia:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0
- **Autenticação:** JWT com python-jose
- **Porta:** 8000 (exposta)
- **Endpoints:** /auth/*, /costs/*, /health

### Camada de Dados
- **Banco:** PostgreSQL 15 Alpine
- **Porta:** 5432 (interna)
- **Persistencia:** Volume Docker

### Infraestrutura
- **Orquestração:** Docker Compose
- **Cloud:** AWS (provisionamento via Terraform)
- **Estado Terraform:** S3 + DynamoDB

## Fluxo de Dados

```
Usuario -> Frontend (3000) -> Backend (8000) -> PostgreSQL (5432)
                    |              |
                    v              v
              AWS Cost Explorer   AWS Secrets
```

## Estrutura de Diretórios

```
cloudcost-iq/
├── backend/
│   ├── app/
│   │   ├── routers/    # endpoints API
│   │   ├── services/   # lógica de negócio
│   │   ├── models/    # schemas DB
│   │   └── main.py    # aplicação FastAPI
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/     # componentes página
│   │   ├── services/  # chamadas API
│   │   └── App.jsx
│   ├── Dockerfile
│   └── package.json
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── iam.tf
└── docker-compose.yml
```

## Stack Tecnológico

| Componente | Tecnologia | Versão |
|------------|------------|-------|
| Backend Framework | FastAPI | 0.109.0 |
| Servidor ASGI | Uvicorn | 0.27.0 |
| ORM | SQLAlchemy | 2.0.25 |
| Banco de Dados | PostgreSQL | 15 |
| Frontend | React | 18 |
| Build Tool | Vite | latest |
| CSS | Tailwind | latest |
| Cloud SDK | Boto3 | 1.34.0 |
| Provisionamento | Terraform | >=1.0 |

## Autenticação e Autorização

O sistema utiliza JWT (JSON Web Tokens) com os seguintes parâmetros:
- **Algoritmo:** HS256
- **Validade Token:** 30 minutos (configurável via ACCESS_TOKEN_EXPIRE_MINUTES)
- **Hash de Senha:** Bcrypt via passlib

## Integração AWS

### Serviços AWS Utilizados
- **AWS Cost Explorer:** Consulta de custos granularity diária
- **AWS Organizations:** Análise por conta/tag
- **AWS IAM:** Credenciais com permissões granulares

### Permissões IAM Necessárias
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ce:GetCostAndUsage",
      "ce:GetDimensionValues",
      "ce:GetTags"
    ],
    "Resource": "*"
  }]
}
```

## Considerações de Segurança

1. **Credenciais AWS:** Armazenadas em variáveis de ambiente, nunca em código
2. **CORS:** Configurado para permitir origens específicas em produção
3. **Secrets:** SECRET_KEY deve ser alterado em produção
4. **Banco:** Credenciais padrão devem ser alteradas
5. **HTTPS:** Recomendado em produção (nginx reverse proxy)

## Escalabilidade

- **Horizontal:** Backend sem estado permite réplicas múltiplas
- **Vertical:** Recursos Docker configuráveis (CPU, memória)
- **Banco:** PostgreSQL suporta réplicas de leitura
- **Cache:** Redis opcional para sessões

## Variáveis de Ambiente

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| AWS_ACCESS_KEY_ID | Sim | - | Chave de acesso AWS |
| AWS_SECRET_ACCESS_KEY | Sim | - | Chave secreta AWS |
| AWS_REGION | Sim | us-east-1 | Região AWS |
| DATABASE_URL | Sim | - | String conexão PostgreSQL |
| SECRET_KEY | Sim | - | Chave JWT |
| ALGORITHM | Não | HS256 | Algoritmo JWT |
| ACCESS_TOKEN_EXPIRE_MINUTES | Não | 30 | Expiração token |

##Health Checks

- Backend: GET /health retorna {"status": "healthy"}
- Database: Healthcheck via pg_isready
- Frontend: Verificação de conectividade com API

## CI/CD

Github Actions configurado em `.github/workflows/ci.yml`:
- Lint e typecheck em pushes
- Build de imagens Docker
- Testes unitários automáticos