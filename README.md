# 🎯 Plataforma de Captação de Leads com Inteligência Territorial

MVP enxuto e robusto para automatizar a captação de leads, aplicar inteligência territorial e agilizar o processo de vendas com agente de IA e integração com WhatsApp.

## ✨ Funcionalidades

- **Autenticação JWT** – Login seguro com usuários e perfis (admin/usuário)
- **Captação de Leads** – Formulário web + integração WhatsApp + importação CSV
- **Inteligência Territorial** – Mapa interativo com polígonos de território e atribuição automática por geolocalização
- **Agente de IA** – Qualificação de leads (score 0–100) e geração de mensagens personalizadas via OpenAI GPT-4o-mini
- **WhatsApp** – Envio e recebimento de mensagens via Twilio WhatsApp API com auto-resposta
- **Dashboard** – Estatísticas em tempo real com gráficos por status e território
- **Busca & Filtros** – Pesquisa por nome, email, telefone, cidade com filtros por status/origem/território
- **Paginação** – Tabela de leads paginada (20 por página)
- **Export CSV** – Exportar leads filtrados em CSV
- **Import CSV** – Importar leads em lote via arquivo CSV (arrastar e soltar)
- **Ações em Lote** – Selecionar múltiplos leads para qualificar com IA, mudar status ou excluir
- **Detalhe e Edição** – Modal completo com timeline de anotações por lead
- **Configurações** – Gestão de territórios, usuários e senha via interface web

## 🛠 Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 + FastAPI + SQLAlchemy + SQLite |
| IA | OpenAI GPT-4o-mini |
| WhatsApp | Twilio WhatsApp API |
| Geolocalização | geopy (Nominatim) + Shapely |
| Frontend | HTML/CSS/JS + Leaflet.js + Chart.js |
| Infraestrutura | Docker + Nginx |

## 🚀 Início Rápido

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas chaves de API
```

### 2. Rodar com Docker (recomendado)

```bash
docker compose up --build
```

- **Frontend:** http://localhost
- **API:** http://localhost:8000
- **Docs API:** http://localhost:8000/docs

### 3. Rodar localmente (desenvolvimento)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Abra `frontend/login.html` no navegador. Credenciais padrão: **admin / admin123**.

## 📁 Estrutura

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + seed territórios + seed admin
│   │   ├── database.py          # SQLAlchemy + SQLite
│   │   ├── models.py            # ORM: User, Lead, Territory, WhatsAppMessage, LeadNote
│   │   ├── schemas.py           # Pydantic v2 schemas
│   │   ├── routers/             # Endpoints REST
│   │   │   ├── auth.py          # Login, me, change-password, users
│   │   │   ├── leads.py         # CRUD, search, export CSV, import CSV, bulk, notes
│   │   │   ├── territories.py
│   │   │   ├── whatsapp.py
│   │   │   ├── ai_agent.py
│   │   │   └── dashboard.py
│   │   ├── services/            # Lógica de negócio
│   │   │   ├── auth_service.py  # JWT (PyJWT 2.12.0) + passlib/bcrypt
│   │   │   ├── ai_service.py    # OpenAI
│   │   │   ├── whatsapp_service.py  # Twilio
│   │   │   ├── lead_service.py
│   │   │   └── territory_service.py
│   │   └── utils/
│   │       └── geo_utils.py     # Geocodificação + polígonos
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── login.html               # Página de login (JWT)
│   ├── index.html               # Landing page de captação
│   ├── dashboard.html           # Dashboard: stats, gráficos, busca, paginação, bulk, CSV
│   ├── map.html                 # Mapa territorial interativo
│   ├── login.html               # Página de autenticação
│   └── settings.html            # Configurações: territórios, usuários, senha
├── docker-compose.yml
├── nginx.conf
└── .env.example
```

## 🔌 API Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/auth/login` | Login (retorna JWT) |
| GET | `/api/auth/me` | Dados do usuário atual |
| POST | `/api/auth/change-password` | Alterar senha |
| GET/POST | `/api/auth/users` | Listar / criar usuários (admin) |
| GET/POST | `/api/leads/` | Listar (com busca/filtros) / criar leads |
| GET | `/api/leads/export/csv` | Exportar leads em CSV |
| POST | `/api/leads/import/csv` | Importar leads de arquivo CSV |
| POST | `/api/leads/bulk` | Ações em lote (delete/qualify/set_status) |
| GET/PUT/DELETE | `/api/leads/{id}` | Detalhe, atualizar, remover |
| POST | `/api/leads/{id}/qualify` | Qualificação por IA |
| GET/POST | `/api/leads/{id}/notes` | Timeline de anotações |
| GET/POST | `/api/territories/` | Listar / criar territórios |
| GET | `/api/territories/{id}/leads` | Leads por território |
| POST | `/api/whatsapp/webhook` | Webhook Twilio |
| POST | `/api/whatsapp/send` | Enviar mensagem WhatsApp |
| POST | `/api/ai/qualify-lead` | Qualificar lead com IA |
| POST | `/api/ai/generate-message` | Gerar mensagem WhatsApp |
| POST | `/api/ai/analyze-territory` | Insights de território |
| GET | `/api/dashboard/stats` | Estatísticas gerais |

## 🔐 Autenticação

O sistema usa JWT (Bearer token). No primeiro boot é criado o usuário padrão:
- **Usuário:** `admin`
- **Senha:** `admin123`

> ⚠️ Altere a senha padrão após o primeiro login em **Configurações → Senha**.


## 🌍 Territórios Pré-configurados

O sistema inicia com 5 territórios brasileiros:
- São Paulo - Capital
- Rio de Janeiro
- Minas Gerais - BH
- Rio Grande do Sul
- Bahia - Salvador

## ⚙️ Configuração WhatsApp (Twilio)

1. Crie conta em [twilio.com](https://twilio.com)
2. Ative o WhatsApp Sandbox
3. Configure o webhook: `https://seu-dominio.com/api/whatsapp/webhook`
4. Defina `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` e `TWILIO_WHATSAPP_NUMBER` no `.env`
