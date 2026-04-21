# 🎯 Plataforma de Captação de Leads com Inteligência Territorial

MVP enxuto e robusto para automatizar a captação de leads, aplicar inteligência territorial e agilizar o processo de vendas com agente de IA e integração com WhatsApp.

## ✨ Funcionalidades

- **Captação de Leads** – Formulário web + integração WhatsApp
- **Inteligência Territorial** – Mapa interativo com polígonos de território e atribuição automática por geolocalização
- **Agente de IA** – Qualificação de leads (score 0–100) e geração de mensagens personalizadas via OpenAI GPT-4o-mini
- **WhatsApp** – Envio e recebimento de mensagens via Twilio WhatsApp API com auto-resposta
- **Dashboard** – Estatísticas em tempo real com gráficos por status e território

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

Abra `frontend/index.html` no navegador.

## 📁 Estrutura

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + seed de territórios
│   │   ├── database.py          # SQLAlchemy + SQLite
│   │   ├── models.py            # ORM: Lead, Territory, WhatsAppMessage
│   │   ├── schemas.py           # Pydantic v2 schemas
│   │   ├── routers/             # Endpoints REST
│   │   │   ├── leads.py
│   │   │   ├── territories.py
│   │   │   ├── whatsapp.py
│   │   │   ├── ai_agent.py
│   │   │   └── dashboard.py
│   │   ├── services/            # Lógica de negócio
│   │   │   ├── ai_service.py    # OpenAI
│   │   │   ├── whatsapp_service.py  # Twilio
│   │   │   ├── lead_service.py
│   │   │   └── territory_service.py
│   │   └── utils/
│   │       └── geo_utils.py     # Geocodificação + polígonos
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               # Landing page de captação
│   ├── dashboard.html           # Dashboard com gráficos
│   └── map.html                 # Mapa territorial interativo
├── docker-compose.yml
├── nginx.conf
└── .env.example
```

## 🔌 API Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET/POST | `/api/leads/` | Listar / criar leads |
| GET/PUT/DELETE | `/api/leads/{id}` | Detalhe, atualizar, remover |
| POST | `/api/leads/{id}/qualify` | Qualificação por IA |
| GET/POST | `/api/territories/` | Listar / criar territórios |
| GET | `/api/territories/{id}/leads` | Leads por território |
| POST | `/api/whatsapp/webhook` | Webhook Twilio |
| POST | `/api/whatsapp/send` | Enviar mensagem WhatsApp |
| POST | `/api/ai/qualify-lead` | Qualificar lead com IA |
| POST | `/api/ai/generate-message` | Gerar mensagem WhatsApp |
| POST | `/api/ai/analyze-territory` | Insights de território |
| GET | `/api/dashboard/stats` | Estatísticas gerais |

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
