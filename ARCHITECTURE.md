# 🏗️ Arquitetura da Plataforma

## Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERNET / CLIENTS                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX (SSL/TLS)                          │
│                    Reverse Proxy & Load Balancer                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      API Routes                             │ │
│  │  • /api/leads          • /api/proposals                    │ │
│  │  • /api/whatsapp       • /api/landing-pages                │ │
│  │  • /admin              • /landing/{slug}                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Business Services                        │ │
│  │  • WhatsAppService     • ProposalService                   │ │
│  │  • AILeadAgent         • Utilities                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │  Celery      │
│   Database   │    │   Cache &    │    │  Workers     │
│              │    │   Queue      │    │              │
│  • Leads     │    │              │    │• Follow-ups  │
│  • Pages     │    │  • Sessions  │    │• Emails      │
│  • Proposals │    │  • Tasks     │    │• Scheduled   │
│  • Messages  │    │              │    │  Messages    │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Fluxo de Dados Principal

### 1. Captura de Lead (Landing Page)

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Visitor   │────────▶│  Landing    │────────▶│   Create    │
│  (Browser)  │  HTTP   │    Page     │  POST   │    Lead     │
└─────────────┘         └─────────────┘         └─────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────┐
                                                │  Database   │
                                                │   + UTM     │
                                                │  Tracking   │
                                                └─────────────┘
```

### 2. Conversa WhatsApp com IA

```
┌────────────┐         ┌────────────┐         ┌────────────┐
│  WhatsApp  │────────▶│  Webhook   │────────▶│   Parse    │
│   Cloud    │  POST   │  Endpoint  │         │  Message   │
│    API     │         └────────────┘         └────────────┘
└────────────┘                                        │
      ▲                                               ▼
      │                                       ┌────────────┐
      │                                       │  AI Agent  │
      │                                       │  (GPT-4)   │
      │                                       └────────────┘
      │                                               │
      │                                               ▼
      │                                       ┌────────────┐
      │                                       │  Classify  │
      │                                       │    Lead    │
      │                                       └────────────┘
      │                                               │
      │          ┌────────────┐                      │
      └──────────│   Send     │◀─────────────────────┘
           POST  │  Response  │
                 └────────────┘
```

### 3. Geração e Aceite de Proposta

```
┌────────────┐         ┌────────────┐         ┌────────────┐
│   Admin    │────────▶│   Create   │────────▶│  Generate  │
│  Creates   │  API    │  Proposal  │         │    PDF     │
│  Proposal  │         └────────────┘         └────────────┘
└────────────┘                │                       │
                              │                       ▼
                              │               ┌────────────┐
                              │               │   Store    │
                              │               │    PDF     │
                              │               └────────────┘
                              ▼                       │
                      ┌────────────┐                 │
                      │   Send     │◀────────────────┘
                      │  WhatsApp  │
                      │   Link     │
                      └────────────┘
                              │
                              ▼
                      ┌────────────┐
                      │   Lead     │
                      │   Clicks   │
                      │   & Views  │
                      └────────────┘
                              │
                              ▼
                      ┌────────────┐
                      │  Accepts   │
                      │  Proposal  │
                      └────────────┘
```

### 4. Follow-up Automatizado

```
┌────────────┐         ┌────────────┐         ┌────────────┐
│   Create   │────────▶│   Celery   │────────▶│   Redis    │
│  Follow-up │         │    Task    │         │   Queue    │
└────────────┘         └────────────┘         └────────────┘
                                                      │
                                                      ▼
                                              ┌────────────┐
                                              │   Celery   │
                                              │   Worker   │
                                              └────────────┘
                                                      │
                                                      ▼
                                              ┌────────────┐
                                              │   Check    │
                                              │  Schedule  │
                                              └────────────┘
                                                      │
                                                      ▼
                                              ┌────────────┐
                                              │   Send     │
                                              │  WhatsApp  │
                                              │  Message   │
                                              └────────────┘
```

## Componentes do Sistema

### Backend (Python/Flask)

```
backend/
├── app.py                    # Aplicação principal
├── config.py                 # Configurações
├── tasks.py                  # Tarefas Celery
├── app/
│   ├── models.py            # SQLAlchemy Models
│   ├── routes/              # API Endpoints
│   │   ├── leads.py         # CRUD de Leads
│   │   ├── whatsapp.py      # WhatsApp webhook
│   │   ├── landing.py       # Landing pages
│   │   ├── proposals.py     # Propostas
│   │   └── admin.py         # Dashboard
│   ├── services/            # Lógica de Negócio
│   │   ├── whatsapp_service.py
│   │   ├── ai_service.py
│   │   └── proposal_service.py
│   ├── templates/           # HTML Templates
│   └── utils/               # Utilitários
└── tests/                   # Testes
```

### Database Schema

```sql
-- Leads (Principal)
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(200),
    neighborhood VARCHAR(100),
    status VARCHAR(20),
    score INTEGER,
    temperature VARCHAR(10),
    source VARCHAR(50),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Landing Pages
CREATE TABLE landing_pages (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(200) UNIQUE,
    title VARCHAR(200),
    neighborhood VARCHAR(100),
    template_name VARCHAR(50),
    hero_title VARCHAR(300),
    content_sections JSON,
    is_active BOOLEAN
);

-- Conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    direction VARCHAR(10),
    message_type VARCHAR(20),
    content TEXT,
    ai_processed BOOLEAN,
    created_at TIMESTAMP
);

-- Proposals
CREATE TABLE proposals (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    title VARCHAR(200),
    service_items JSON,
    total_value NUMERIC(10,2),
    status VARCHAR(20),
    pdf_url VARCHAR(500),
    accepted_at TIMESTAMP
);

-- Follow-ups
CREATE TABLE follow_ups (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    scheduled_for TIMESTAMP,
    message_content TEXT,
    include_timer BOOLEAN,
    status VARCHAR(20)
);
```

## Integrações Externas

### WhatsApp Cloud API

```
Meta Graph API v18.0
├── Send Messages
│   ├── Text
│   ├── Image
│   ├── Audio
│   ├── Video
│   └── Document
├── Receive Messages (Webhook)
│   ├── Parse incoming
│   └── Mark as read
└── Templates
    └── Pre-approved messages
```

### OpenAI GPT-4

```
OpenAI API
├── Chat Completions
│   ├── Lead qualification
│   ├── Conversation handling
│   ├── Intent detection
│   └── Information extraction
└── Configuration
    ├── Model: gpt-4-turbo-preview
    ├── Temperature: 0.7
    └── Max tokens: 200-500
```

## Segurança

### Camadas de Proteção

1. **SSL/TLS** - Nginx com Let's Encrypt
2. **Firewall** - UFW configurado
3. **Rate Limiting** - Recomendado implementar
4. **Environment Variables** - Credenciais protegidas
5. **Webhook Verification** - Token de verificação
6. **Input Validation** - Sanitização de dados

## Performance

### Otimizações

- **Redis Caching** - Cache de sessões e dados
- **Database Indexing** - Índices em campos de busca
- **CDN** - Cloudflare recomendado
- **Gunicorn Workers** - 4 workers por padrão
- **Connection Pooling** - SQLAlchemy pool

### Escalabilidade

```
Single Server (até 1000 leads/dia)
    ↓
VPS Upgrade (até 5000 leads/dia)
    ↓
Load Balancer + 2 Servers (até 20000 leads/dia)
    ↓
Kubernetes + Auto-scaling (ilimitado)
```

## Monitoramento

### Logs

```
Application Logs
├── Flask (INFO level)
├── Celery (INFO level)
├── WhatsApp (DEBUG level)
└── AI Agent (INFO level)
```

### Métricas Recomendadas

- Response time (API)
- Queue length (Celery)
- Database connections
- Memory usage
- CPU usage
- Disk space

## Backup Strategy

### Diário
- Database dump (PostgreSQL)
- Arquivos de upload (PDFs)

### Semanal
- Snapshot completo do servidor

### Mensal
- Backup offsite (S3, Spaces)

## Disaster Recovery

### RTO (Recovery Time Objective)
- Target: < 4 horas

### RPO (Recovery Point Objective)
- Target: < 24 horas

### Procedimento
1. Restaurar database do backup mais recente
2. Restaurar arquivos de upload
3. Recriar containers Docker
4. Verificar integridade dos dados
5. Reativar webhooks

---

**Documentação completa em**: DOCUMENTATION.md, API_REFERENCE.md, DEPLOY_GUIDE.md
