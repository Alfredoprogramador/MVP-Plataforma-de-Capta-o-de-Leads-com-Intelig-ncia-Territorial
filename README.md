# 🚀 MVP - Plataforma de Captação de Leads com Inteligência Territorial

Plataforma completa para captação e qualificação automatizada de leads, com foco em inteligência territorial (segmentação por bairro), integração com WhatsApp, agente de IA para qualificação, geração de propostas e sistema de follow-up automatizado.

## ✨ Funcionalidades Principais

- 📍 **Landing Pages Segmentadas por Bairro** - Geração dinâmica com templates configuráveis
- 💬 **Integração WhatsApp Bidirecional** - Envio/recebimento de texto, áudio, imagem e vídeo
- 🤖 **Agente de IA para Qualificação** - GPT-4 para conversas naturais e classificação automática
- 📄 **Geração de Propostas** - PDF e visualização web com botão de aceite
- ⏰ **Follow-up Multimídia** - Mensagens agendadas com timer de urgência
- 📊 **Painel Administrativo** - Dashboard completo com métricas e filtros
- 🎯 **Tracking de Origem** - Captura automática de fonte (UTM, WhatsApp, etc.)

## 🚀 Quick Start

### Com Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial.git
cd MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial

# Configure variáveis de ambiente
cp .env.example .env
nano .env  # Adicione suas credenciais

# Inicie os containers
docker-compose up -d

# Acesse a aplicação
# API: http://localhost:5000
# Admin: http://localhost:5000/admin
```

### Configuração Mínima Necessária

Edite o arquivo `.env` com:

```env
# WhatsApp Cloud API (obrigatório)
WHATSAPP_API_TOKEN=seu_token_aqui
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id_aqui

# OpenAI (obrigatório)
OPENAI_API_KEY=sua_chave_openai_aqui

# URL pública (obrigatório para webhooks)
WEBHOOK_BASE_URL=https://seu-dominio.com
```

## 📚 Documentação Completa

Para documentação detalhada, incluindo:
- Instalação manual
- Configuração do WhatsApp
- Deploy em VPS
- API Reference
- Troubleshooting

Veja: [DOCUMENTATION.md](DOCUMENTATION.md)

## 🏗️ Stack Tecnológica

- **Backend:** Python 3.11 + Flask + SQLAlchemy + PostgreSQL
- **IA:** OpenAI GPT-4
- **Messaging:** WhatsApp Cloud API / Twilio
- **Background Jobs:** Celery + Redis
- **Deploy:** Docker + Docker Compose

## 📊 Endpoints Principais

- `GET /health` - Health check
- `POST /api/leads` - Criar lead
- `GET /api/leads` - Listar leads (com filtros)
- `GET /api/leads/stats` - Estatísticas
- `POST/GET /api/whatsapp/webhook` - WhatsApp webhook
- `POST /api/proposals` - Criar proposta
- `GET /admin` - Dashboard administrativo
- `GET /landing/<slug>` - Landing page

## 🔐 Segurança

- ✅ Configuração via variáveis de ambiente
- ✅ Webhooks verificados
- ✅ HTTPS recomendado para produção
- ✅ Validação de dados
- ✅ Rate limiting (recomendado adicionar)

## 📈 Roadmap Futuro

- [ ] Autenticação JWT para admin
- [ ] Templates de mensagem WhatsApp
- [ ] Analytics avançado
- [ ] Integração com CRM
- [ ] Chatbot multi-idioma
- [ ] Mobile app

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [DOCUMENTATION.md](DOCUMENTATION.md) para mais detalhes.

## 📄 Licença

MIT License - veja LICENSE para detalhes.

---

**Desenvolvido com ❤️ para automação de vendas e captação de leads**
