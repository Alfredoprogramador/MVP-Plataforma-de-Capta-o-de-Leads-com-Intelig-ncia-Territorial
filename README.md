# MVP - Plataforma de Captação de Leads com Inteligência Territorial

## 🚀 Visão Geral

Plataforma completa para captação e gestão de leads com inteligência territorial, integração WhatsApp e agente de IA para qualificação automática.

## ✨ Funcionalidades

### 1. Landing Pages Segmentadas por Bairro
- ✅ Criação automática de landing pages por bairro
- ✅ Templates configuráveis e personalizáveis
- ✅ Captura de leads com rastreamento de origem (UTM)
- ✅ Design responsivo e otimizado para conversão

### 2. Integração Bidirecional com WhatsApp
- ✅ Envio e recebimento de mensagens de texto
- ✅ Suporte para mensagens de áudio e imagem
- ✅ WhatsApp Cloud API (oficial)
- ✅ Webhooks para notificações em tempo real
- ✅ Confirmação de leitura e entrega

### 3. Agente de IA para Qualificação
- ✅ Integração com GPT-4 para conversas naturais
- ✅ Classificação automática (Quente/Morno/Frio)
- ✅ Pontuação de leads (0-100)
- ✅ Regras de negócio configuráveis
- ✅ Escalação automática para time comercial

### 4. Geração de Propostas
- ✅ Criação de propostas em PDF
- ✅ Link de aceite com página web
- ✅ QR Code para acesso rápido
- ✅ Registro automático de aceite
- ✅ Notificações via WhatsApp

### 5. Follow-up Multimídia
- ✅ Envio programado de mensagens
- ✅ Suporte para texto, áudio e imagens
- ✅ Timer de urgência configurável
- ✅ Gatilhos baseados em comportamento
- ✅ Lembretes de propostas expirando

### 6. Painel Administrativo
- ✅ Dashboard com métricas em tempo real
- ✅ Filtros por bairro, origem, status
- ✅ Visualização de conversas
- ✅ Gestão de templates
- ✅ Analytics detalhado

### 7. Rastreamento de Origem
- ✅ Captura de parâmetros UTM
- ✅ Identificação de origem (Instagram, Google, etc.)
- ✅ Relatórios por campanha
- ✅ Análise de performance

### 8. Infraestrutura VPS
- ✅ Docker e Docker Compose
- ✅ PostgreSQL + Redis
- ✅ Celery para tarefas assíncronas
- ✅ Pronto para deploy em VPS Linux

## 🛠️ Tecnologias

- **Backend**: Python 3.11 + FastAPI
- **Banco de Dados**: PostgreSQL (ou SQLite para desenvolvimento)
- **Cache/Queue**: Redis + Celery
- **IA**: OpenAI GPT-4
- **WhatsApp**: WhatsApp Cloud API / Twilio
- **PDF**: ReportLab
- **Frontend**: HTML/CSS/JavaScript (vanilla)

## 📦 Instalação

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta WhatsApp Business API
- Chave API OpenAI

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial.git
cd MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial
```

2. Copie o arquivo de ambiente:
```bash
cp .env.example .env
```

3. Configure as variáveis de ambiente no `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/leads_db
OPENAI_API_KEY=sk-your-key-here
WHATSAPP_API_TOKEN=your-token-here
WHATSAPP_PHONE_NUMBER_ID=your-phone-id
SECRET_KEY=your-secret-key
```

4. Inicie com Docker Compose:
```bash
docker-compose up -d
```

5. Acesse a aplicação:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Admin: http://localhost:8000/admin

### Instalação Manual (sem Docker)

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o banco de dados:
```bash
# SQLite (desenvolvimento)
export DATABASE_URL=sqlite:///./leads.db

# PostgreSQL (produção)
export DATABASE_URL=postgresql://user:password@localhost/leads_db
```

3. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

4. Em outro terminal, inicie o Celery Worker:
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

5. Em outro terminal, inicie o Celery Beat:
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

## 🚀 Deploy em VPS

Consulte o arquivo [DEPLOY.md](DEPLOY.md) para instruções detalhadas de deploy em VPS (DigitalOcean, AWS EC2, etc.).

## 📚 Uso da API

### Criar Landing Page

```bash
curl -X POST "http://localhost:8000/api/landing-pages/" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "centro-sp",
    "title": "Serviços no Centro de São Paulo",
    "neighborhood": "Centro",
    "city": "São Paulo",
    "state": "SP",
    "template_name": "default"
  }'
```

### Listar Leads

```bash
curl "http://localhost:8000/api/leads/?status=qualified&limit=10"
```

### Criar Proposta

```bash
curl -X POST "http://localhost:8000/api/proposals/" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 1,
    "title": "Proposta de Serviço",
    "description": "Descrição detalhada do serviço...",
    "amount": 1500.00
  }'
```

### Enviar Mensagem WhatsApp

```bash
curl -X POST "http://localhost:8000/api/whatsapp/send" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+5511999999999",
    "message": "Olá! Como podemos ajudar?",
    "message_type": "text"
  }'
```

## 🔧 Configuração do WhatsApp

### WhatsApp Cloud API

1. Acesse https://developers.facebook.com/
2. Crie um App e adicione WhatsApp Business
3. Obtenha:
   - Phone Number ID
   - Business Account ID
   - Access Token
4. Configure o Webhook:
   - URL: `https://seu-dominio.com/api/whatsapp/webhook`
   - Verify Token: (mesmo do `.env`)
   - Campos: `messages`, `message_status`

### Twilio (Alternativa)

1. Acesse https://www.twilio.com/
2. Obtenha:
   - Account SID
   - Auth Token
   - WhatsApp Number
3. Configure no `.env`

## 📊 Analytics e Métricas

Acesse as estatísticas em tempo real:

```bash
curl http://localhost:8000/api/leads/stats/analytics
```

Retorna:
- Total de leads
- Leads por status
- Leads por temperatura
- Leads por bairro
- Leads por origem

## 🔐 Segurança

- ✅ Validação de dados com Pydantic
- ✅ Webhook verification para WhatsApp
- ✅ CORS configurado
- ✅ Variáveis de ambiente para secrets
- ✅ HTTPS recomendado para produção

## 🧪 Testes

Para testar a aplicação localmente:

```bash
# Teste de saúde
curl http://localhost:8000/health

# Teste de webhook WhatsApp
curl "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=your-token&hub.challenge=test"
```

## 📝 Estrutura do Projeto

```
.
├── app/
│   ├── api/              # Endpoints da API
│   │   ├── leads.py
│   │   ├── landing_pages.py
│   │   ├── whatsapp.py
│   │   └── proposals.py
│   ├── services/         # Lógica de negócio
│   │   ├── whatsapp.py
│   │   ├── ai_agent.py
│   │   └── proposal.py
│   ├── templates/        # Templates HTML
│   │   └── default.html
│   ├── static/           # Arquivos estáticos
│   ├── config.py         # Configurações
│   ├── database.py       # Database setup
│   ├── models.py         # Modelos SQLAlchemy
│   ├── schemas.py        # Schemas Pydantic
│   ├── tasks.py          # Celery tasks
│   └── main.py           # App principal
├── docker-compose.yml    # Orquestração Docker
├── Dockerfile            # Imagem Docker
├── requirements.txt      # Dependências Python
└── .env.example          # Exemplo de variáveis
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é um MVP e está disponível para uso conforme necessário.

## 💬 Suporte

Para dúvidas e suporte:
- Abra uma Issue no GitHub
- Consulte a documentação da API em `/docs`

## 🎯 Roadmap Futuro

- [ ] Interface admin em React/Vue
- [ ] Integração com CRM
- [ ] Análise preditiva com ML
- [ ] Chatbot visual builder
- [ ] Integração com outras redes sociais
- [ ] Testes automatizados
- [ ] Multi-tenancy
- [ ] API de relatórios avançados

---

Desenvolvido com ❤️ para automatizar captação de leads com inteligência territorial.
