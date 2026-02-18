# MVP - Plataforma de Captação de Leads com Inteligência Territorial

## 📋 Visão Geral

Esta é uma plataforma completa para captação e qualificação automatizada de leads, com foco em inteligência territorial (segmentação por bairro), integração com WhatsApp, agente de IA para qualificação, geração de propostas e sistema de follow-up automatizado.

## 🎯 Funcionalidades Principais

### 1. Landing Pages Segmentadas por Bairro
- ✅ Geração dinâmica de páginas a partir de templates configuráveis
- ✅ Associação automática de leads ao bairro de origem
- ✅ Tracking completo com UTM parameters
- ✅ Formulário de captura otimizado

### 2. Integração Bidirecional com WhatsApp
- ✅ Envio e recebimento de mensagens (texto, áudio, imagem, vídeo)
- ✅ Suporte para WhatsApp Cloud API (oficial)
- ✅ Webhooks para notificações em tempo real
- ✅ Histórico completo de conversas

### 3. Agente de IA para Qualificação
- ✅ Integração com GPT-4 para conversas naturais
- ✅ Classificação automática de leads (quente/morno/frio)
- ✅ Pontuação de 0-100 baseada em comportamento
- ✅ Regras de negócio configuráveis para escalação
- ✅ Extração automática de informações do lead

### 4. Geração de Propostas
- ✅ Criação de propostas em PDF
- ✅ Visualização web com link compartilhável
- ✅ Botão de aceite integrado
- ✅ Tracking de status (pendente/aceito/rejeitado)
- ✅ Validade configurável

### 5. Follow-up Multimídia com Urgência
- ✅ Agendamento de mensagens automáticas
- ✅ Suporte para texto, imagem, áudio e vídeo
- ✅ Timer regressivo de urgência
- ✅ Gatilhos baseados em comportamento
- ✅ Processamento em background via Celery

### 6. Painel Administrativo
- ✅ Dashboard com métricas essenciais
- ✅ Gestão de leads com filtros avançados
- ✅ Visualização por bairro, status, temperatura, fonte
- ✅ Relatórios de conversão
- ✅ Configuração de templates

### 7. Registro de Origem
- ✅ Captura automática da fonte (UTM, landing page, WhatsApp, etc.)
- ✅ Tracking completo de campanhas
- ✅ Análise de desempenho por canal

## 🏗️ Arquitetura

### Stack Tecnológica

**Backend:**
- Python 3.11
- Flask 3.0 (Framework web)
- SQLAlchemy (ORM)
- PostgreSQL (Banco de dados)
- Celery + Redis (Tarefas assíncronas)
- OpenAI GPT-4 (IA)
- WhatsApp Cloud API

**Frontend:**
- HTML5/CSS3/JavaScript (Admin Dashboard)
- Templates Jinja2 (Landing Pages)

**Infraestrutura:**
- Docker & Docker Compose
- Gunicorn (WSGI Server)
- Nginx (recomendado para produção)

### Estrutura de Diretórios

```
MVP-Plataforma-de-Captacao-de-Leads/
├── backend/
│   ├── app/
│   │   ├── models.py              # Modelos de dados
│   │   ├── routes/                # Rotas da API
│   │   │   ├── leads.py           # Gestão de leads
│   │   │   ├── whatsapp.py        # WhatsApp integration
│   │   │   ├── landing.py         # Landing pages
│   │   │   ├── proposals.py       # Propostas
│   │   │   └── admin.py           # Admin dashboard
│   │   ├── services/              # Serviços de negócio
│   │   │   ├── whatsapp_service.py
│   │   │   ├── ai_service.py
│   │   │   └── proposal_service.py
│   │   └── templates/             # Templates HTML
│   │       ├── landing_page.html
│   │       ├── proposal_view.html
│   │       └── admin_dashboard.html
│   ├── app.py                     # Aplicação Flask
│   ├── config.py                  # Configurações
│   ├── tasks.py                   # Tarefas Celery
│   └── requirements.txt           # Dependências Python
├── docker-compose.yml             # Configuração Docker
├── Dockerfile                     # Imagem Docker
├── .env.example                   # Exemplo de variáveis de ambiente
└── README.md                      # Este arquivo
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker e Docker Compose (opcional, recomendado)

### Opção 1: Instalação com Docker (Recomendado)

1. **Clone o repositório:**
```bash
git clone https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial.git
cd MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial
```

2. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
nano .env  # Edite com suas credenciais
```

3. **Configure as seguintes variáveis obrigatórias:**
```env
# WhatsApp Cloud API
WHATSAPP_API_TOKEN=seu_token_aqui
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id_aqui
WHATSAPP_VERIFY_TOKEN=seu_verify_token_aqui

# OpenAI
OPENAI_API_KEY=sua_chave_openai_aqui

# URLs públicas
WEBHOOK_BASE_URL=https://seu-dominio.com
```

4. **Inicie os containers:**
```bash
docker-compose up -d
```

5. **Verifique se está funcionando:**
```bash
curl http://localhost:5000/health
```

### Opção 2: Instalação Manual

1. **Clone e configure:**
```bash
git clone <repo-url>
cd MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale dependências:**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure PostgreSQL:**
```bash
createdb leads_platform
```

5. **Configure variáveis de ambiente:**
```bash
cp ../.env.example ../.env
# Edite .env com suas credenciais
```

6. **Execute migrações:**
```bash
export FLASK_APP=app.py
flask db upgrade
```

7. **Inicie a aplicação:**
```bash
# Terminal 1: Flask
python app.py

# Terminal 2: Celery Worker
celery -A tasks worker --loglevel=info

# Terminal 3: Celery Beat
celery -A tasks beat --loglevel=info
```

## 📱 Configuração do WhatsApp

### WhatsApp Cloud API (Recomendado)

1. **Acesse o Meta for Developers:**
   - Vá para https://developers.facebook.com/
   - Crie um app do tipo "Business"

2. **Configure WhatsApp:**
   - Adicione o produto "WhatsApp"
   - Gere um token de acesso permanente
   - Configure o número de teste ou número de produção

3. **Configure Webhook:**
   - URL: `https://seu-dominio.com/api/whatsapp/webhook`
   - Verify Token: (o mesmo que você configurou em `.env`)
   - Subscribe to: `messages`

4. **Atualize `.env`:**
```env
WHATSAPP_API_TOKEN=EAAxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_VERIFY_TOKEN=seu_token_verificacao
```

### Alternativa: Twilio

Se preferir usar Twilio:

1. Crie uma conta em https://www.twilio.com/
2. Configure WhatsApp Business API
3. Atualize `.env`:
```env
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## 🤖 Configuração da IA (OpenAI)

1. **Obtenha uma API Key:**
   - Acesse https://platform.openai.com/
   - Crie uma API key

2. **Configure em `.env`:**
```env
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4-turbo-preview
```

3. **Ajuste os thresholds de qualificação:**
```env
HOT_LEAD_THRESHOLD=70    # Leads com score >= 70 são "quentes"
WARM_LEAD_THRESHOLD=40   # Leads com score >= 40 são "mornos"
COLD_LEAD_THRESHOLD=0    # Leads abaixo de 40 são "frios"
```

## 📊 Uso da Plataforma

### 1. Criar Landing Page

**Via API:**
```bash
curl -X POST http://localhost:5000/api/landing-pages \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "jardim-paulista",
    "title": "Serviços no Jardim Paulista",
    "neighborhood": "Jardim Paulista",
    "hero_title": "Soluções Completas no Jardim Paulista",
    "hero_subtitle": "Atendemos sua região com excelência",
    "cta_text": "Solicitar Orçamento Grátis"
  }'
```

**Acessar:**
```
http://localhost:5000/landing/jardim-paulista
```

### 2. Gerenciar Leads

**Listar leads:**
```bash
curl http://localhost:5000/api/leads?neighborhood=Jardim%20Paulista&temperature=hot
```

**Ver estatísticas:**
```bash
curl http://localhost:5000/api/leads/stats
```

**Dashboard administrativo:**
```
http://localhost:5000/admin
```

### 3. Criar Proposta

```bash
curl -X POST http://localhost:5000/api/proposals \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 1,
    "title": "Proposta de Serviço",
    "description": "Serviços completos conforme solicitado",
    "service_items": [
      {
        "name": "Serviço A",
        "description": "Descrição do serviço A",
        "value": 500.00
      },
      {
        "name": "Serviço B",
        "description": "Descrição do serviço B",
        "value": 300.00
      }
    ],
    "total_value": 800.00,
    "validity_days": 7
  }'
```

### 4. Enviar Follow-up

```bash
curl -X POST http://localhost:5000/api/leads/1/followup \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá! Ainda tem interesse em nossos serviços?",
    "schedule_hours": 24,
    "include_timer": true,
    "timer_hours": 24
  }'
```

## 🔐 Segurança

### Recomendações para Produção

1. **Use HTTPS:**
   - Configure SSL/TLS no nginx
   - Use Let's Encrypt para certificados gratuitos

2. **Variáveis de Ambiente:**
   - Nunca commite arquivos `.env`
   - Use secrets management em produção

3. **Firewall:**
   - Bloqueie portas desnecessárias
   - Permita apenas 80/443 (HTTP/HTTPS)

4. **Backup:**
   - Configure backups automáticos do PostgreSQL
   - Faça backup de uploads/arquivos

5. **Monitoring:**
   - Use ferramentas como Sentry para error tracking
   - Configure logs centralizados

## 🌐 Deploy em VPS

### Exemplo com Ubuntu 22.04

1. **Conecte via SSH:**
```bash
ssh root@seu-servidor-ip
```

2. **Instale Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Instale Docker Compose:**
```bash
apt install docker-compose-plugin
```

4. **Clone o projeto:**
```bash
git clone <repo-url>
cd MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial
```

5. **Configure `.env`:**
```bash
cp .env.example .env
nano .env
```

6. **Inicie:**
```bash
docker-compose up -d
```

7. **Configure Nginx (opcional mas recomendado):**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. **Configure SSL com Certbot:**
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d seu-dominio.com
```

## 📈 Monitoramento

### Logs

```bash
# Ver logs da aplicação
docker-compose logs -f backend

# Ver logs do Celery
docker-compose logs -f celery_worker

# Ver todos os logs
docker-compose logs -f
```

### Métricas

Acesse o dashboard administrativo:
```
https://seu-dominio.com/admin
```

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-flask pytest-cov

# Executar testes
pytest

# Com coverage
pytest --cov=app tests/
```

## 🐛 Troubleshooting

### WhatsApp não está recebendo mensagens

1. Verifique se o webhook está configurado corretamente
2. Teste o endpoint: `curl https://seu-dominio.com/api/whatsapp/webhook`
3. Verifique os logs: `docker-compose logs backend | grep whatsapp`

### IA não está respondendo

1. Verifique a API key do OpenAI
2. Confirme que há créditos na conta OpenAI
3. Veja os logs de erro

### Banco de dados não conecta

1. Verifique se o PostgreSQL está rodando: `docker-compose ps`
2. Confirme as credenciais no `.env`
3. Teste conexão: `docker-compose exec db psql -U leads_user -d leads_platform`

## 📞 Suporte

Para questões e suporte:
- GitHub Issues: [Criar issue](https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial/issues)

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🎉 Agradecimentos

- OpenAI pela API GPT
- Meta pela WhatsApp Cloud API
- Comunidade Python e Flask
