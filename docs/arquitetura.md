# Documentação de Arquitetura - CloudCost IQ

## Visão Geral do Sistema

O CloudCost IQ é uma plataforma de análise inteligente de custos de infraestrutura em nuvem AWS. A arquitetura segue um padrão de microsserviços modernos, desenhada para ser hospedada facilmente através de provedores PaaS (Platform as a Service) contêinerizados, como o **Railway**.

A plataforma possui três componentes principais:
1. **Frontend (Nginx + React)**
2. **Backend (FastAPI)**
3. **Database (PostgreSQL Gerenciado)**

## Arquitetura de Componentes

### Camada de Frontend
- **Tecnologia:** React 18 + Vite
- **Styling:** Tailwind CSS
- **Transparencia e Proxy:** Nginx (para hospedar a SPA gerada pelo React e rotear o path `/auth`, `/api`, `/costs` ao backend).
- **Funcionalidades:** Dashboard de custos, Login, visualização de relatórios.

### Camada de Backend
- **Tecnologia:** FastAPI (Python 3.12)
- **ORM:** SQLAlchemy 2.0
- **Autenticação:** JWT com `python-jose` protegido por roteamento de Reverse Proxy Nginx.
- **Integração Externa:** Consulta AWS via `boto3`.

### Camada de Dados
- **Banco:** PostgreSQL Engine (Railway Native)
- **Persistência:** Volumes gerenciados automaticamente pelo PaaS.

## Fluxo de Dados e Rede (Railway)

```
Navegador Web
       | (HTTPS - Domínio Público do Frontend)
       v
Railway Edge Router
       |
       v
[ Serviço Frontend (Nginx Proxy) ]
       | --(Proxy Pass Reverso usando BACKEND_URL)--> [ Serviço Backend ]
                                                               |
                                                               v
                                                    [ Banco de Dados PostgreSQL ]
                                                               |
                                                        (Chamadas Externas) -> API do AWS Cost Explorer
```

## Estrutura de Diretórios e Serviços

```
cloudcost-iq/
├── backend/          (Serviço 1 - API)
│   ├── app/
│   │   ├── routers/    # endpoints API
│   │   ├── services/   # lógica de negócio
│   │   ├── models/     # schemas DB
│   │   └── main.py     # aplicação FastAPI
│   └── Dockerfile
├── frontend/         (Serviço 2 - UI & Proxy)
│   ├── src/
│   │   ├── pages/      # componentes página
│   │   ├── services/   # chamadas API (axios)
│   │   └── App.jsx
│   ├── nginx.conf      # Regras vitais do Reverse Proxy
│   └── Dockerfile
└── terraform/        (Opcional: Legado AWS ECS)
```

## Stack Tecnológico

| Componente | Tecnologia | Papel Fundamental |
|------------|------------|-------------------|
| Web Proxy | Nginx | Roteamento HTTPS & Prevenção CORS |
| Backend API | FastAPI | Fast Performance Rest Framework |
| ORM | SQLAlchemy | Consultas e mapeamento Postgres |
| Frontend Engine| React & Vite | Criação rápida e leve (SPA) |
| DevOps & PaaS | Railway | Deploy contínuo, Logs e Networking Integrado |
| Relatórios | Recharts | Visualizações financeiras de Cloud |

## Autenticação e Proxy Seguro

O sistema utiliza a combinação de **JWT (JSON Web Tokens)** + **Nginx Proxy Pass**.
- Em vez de expor portas diferentes aos usuários, o Nginx é o "Porteiro".
- Quando a URL `/auth/login` é batida no frontend, o Nginx empacota esse pedido e direciona (via `BACKEND_URL`) com grandes tamanhos de Buffer (`proxy_buffer_size`) diretos para a API invisível, retornando a autenticação perfeitamente.
- O Token JWT gerado é o "crachá" para as telas protegidas do React.

## Variáveis de Ambiente Essenciais (Deploy)

A configuração se baseia amplamente no motor do **Railway**.

### Variáveis do Backend Service
| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `AWS_ACCESS_KEY_ID` | Sim | Chave de acesso AWS com política de Costs |
| `AWS_SECRET_ACCESS_KEY` | Sim | Chave secreta AWS |
| `AWS_REGION` | Sim | Região AWS default (`us-east-1` recomendado) |
| `DATABASE_URL` | Sim | A url automatizada gerada na aba 'Connect' do Postgres no Railway |
| `SECRET_KEY` | Sim | Chave SHA-256 para o JWT Auth |

### Variáveis do Frontend Service
| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `BACKEND_URL` | Sim | URL HTTPS de domínio público gerada para o serviço do *Backend* |

## Lições Aprendidas de Infraestrutura
- O override do Header HTTP `$host` dentro do Nginx causa a Falha de Hostname (`status 400 Bad Request`) em serviços de PaaS. Retiramos da configuração default porque os Load Balancers do PaaS usam o Host Header para decidir qual container chamar.
- O Uvicorn do FastAPI costuma gerar Headers longos de Proxy. As diretivas de `proxy_buffer_size 128k` garantem estabilidade de sessão sem gerar o trágico erro 502 (`upstream sent too big header`).