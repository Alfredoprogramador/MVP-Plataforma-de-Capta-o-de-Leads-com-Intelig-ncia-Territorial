# Quick Start Guide

Este guia mostra como iniciar rapidamente a plataforma em seu ambiente local.

## Início Rápido (5 minutos)

### 1. Pré-requisitos

- Docker e Docker Compose instalados
- Git instalado

### 2. Clone e Configure

```bash
# Clone o repositório
git clone https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial.git
cd MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial

# Copie o arquivo de ambiente
cp .env.example .env
```

### 3. Configure Credenciais (Opcional para Teste)

Edite o arquivo `.env` e adicione suas credenciais:

```bash
nano .env
```

**Mínimo para testar:**
```env
DATABASE_URL=sqlite:///./leads.db
SECRET_KEY=test-secret-key-change-in-production
```

**Para funcionalidades completas:**
```env
OPENAI_API_KEY=sk-sua-chave-aqui
WHATSAPP_API_TOKEN=seu-token-aqui
WHATSAPP_PHONE_NUMBER_ID=seu-id-aqui
```

### 4. Inicie a Aplicação

```bash
docker-compose up -d
```

### 5. Aguarde a Inicialização

```bash
# Veja os logs
docker-compose logs -f app

# Aguarde até ver: "Application startup complete"
# Pressione Ctrl+C para sair dos logs
```

### 6. Acesse a Aplicação

Abra seu navegador:

- **Home**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Primeiros Passos

### Criar uma Landing Page

Via API (usando curl):

```bash
curl -X POST http://localhost:8000/api/landing-pages/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "teste-sp",
    "title": "Teste de Serviços",
    "neighborhood": "Centro",
    "city": "São Paulo",
    "state": "SP",
    "template_name": "default"
  }'
```

Ou via Swagger UI:
1. Acesse http://localhost:8000/docs
2. Expanda `POST /api/landing-pages/`
3. Clique em "Try it out"
4. Preencha os dados
5. Clique em "Execute"

### Acessar a Landing Page

Após criar, acesse:
```
http://localhost:8000/lp/teste-sp
```

### Submeter um Lead de Teste

Preencha o formulário na landing page ou use a API:

```bash
curl -X POST http://localhost:8000/api/landing-pages/1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Teste",
    "phone": "+5511999999999",
    "email": "joao@teste.com"
  }'
```

### Ver Leads Capturados

No Admin Dashboard:
```
http://localhost:8000/admin
```

Ou via API:
```bash
curl http://localhost:8000/api/leads/
```

### Ver Estatísticas

```bash
curl http://localhost:8000/api/leads/stats/analytics
```

## Testando Sem WhatsApp/OpenAI

Você pode testar a maior parte da plataforma sem configurar WhatsApp ou OpenAI:

### O que funciona sem API keys:
- ✅ Landing pages
- ✅ Captura de leads
- ✅ Admin dashboard
- ✅ Criação de propostas (sem envio WhatsApp)
- ✅ Analytics
- ✅ Filtros e busca

### O que precisa de API keys:
- ❌ Receber/enviar mensagens WhatsApp
- ❌ Agente de IA para qualificação
- ❌ Respostas automáticas

## Comandos Úteis

### Ver logs de todos os serviços
```bash
docker-compose logs -f
```

### Ver logs de um serviço específico
```bash
docker-compose logs -f app
docker-compose logs -f celery_worker
```

### Reiniciar a aplicação
```bash
docker-compose restart app
```

### Parar tudo
```bash
docker-compose down
```

### Parar e limpar dados
```bash
docker-compose down -v
```

### Acessar o banco de dados
```bash
docker-compose exec db psql -U leads_user -d leads_db
```

### Executar comandos Python no container
```bash
docker-compose exec app python
```

## Exemplos de Uso da API

### 1. Criar Landing Pages para Vários Bairros

```bash
# Pinheiros
curl -X POST http://localhost:8000/api/landing-pages/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "pinheiros-sp",
    "title": "Serviços em Pinheiros",
    "neighborhood": "Pinheiros",
    "city": "São Paulo",
    "state": "SP",
    "template_name": "default"
  }'

# Vila Mariana
curl -X POST http://localhost:8000/api/landing-pages/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "vila-mariana-sp",
    "title": "Serviços na Vila Mariana",
    "neighborhood": "Vila Mariana",
    "city": "São Paulo",
    "state": "SP",
    "template_name": "default"
  }'
```

### 2. Listar Leads com Filtros

```bash
# Leads qualificados
curl "http://localhost:8000/api/leads/?status=qualified"

# Leads quentes
curl "http://localhost:8000/api/leads/?temperature=hot"

# Leads de um bairro específico
curl "http://localhost:8000/api/leads/?neighborhood=Centro"

# Combinar filtros
curl "http://localhost:8000/api/leads/?status=qualified&temperature=hot&neighborhood=Centro"
```

### 3. Criar Proposta para um Lead

```bash
curl -X POST http://localhost:8000/api/proposals/ \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 1,
    "title": "Proposta Premium",
    "description": "Pacote completo incluindo:\n- Serviço A\n- Serviço B\n- Suporte",
    "amount": 2500.00
  }'
```

### 4. Simular Aceite de Proposta

```bash
curl -X POST http://localhost:8000/api/proposals/1/accept
```

### 5. Atualizar Status de Lead

```bash
curl -X PUT http://localhost:8000/api/leads/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "qualified",
    "temperature": "hot",
    "score": 90,
    "notes": "Lead muito interessado"
  }'
```

## Desenvolvendo Localmente (Sem Docker)

Se preferir desenvolver sem Docker:

### 1. Instalar Dependências

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

```bash
# Usar SQLite para desenvolvimento
export DATABASE_URL=sqlite:///./leads.db
```

### 3. Iniciar Servidor

```bash
uvicorn app.main:app --reload
```

### 4. Iniciar Celery (terminal separado)

```bash
# Worker
celery -A app.tasks.celery_app worker --loglevel=info

# Beat (terminal separado)
celery -A app.tasks.celery_app beat --loglevel=info
```

## Troubleshooting

### Porta 8000 já em uso

```bash
# Parar processo na porta 8000
sudo lsof -ti:8000 | xargs kill -9

# Ou mudar a porta no docker-compose.yml
```

### Containers não iniciam

```bash
# Ver logs de erro
docker-compose logs

# Rebuild completo
docker-compose down
docker-compose up --build
```

### Erro ao conectar ao banco

```bash
# Verificar se container do banco está rodando
docker-compose ps

# Reiniciar banco
docker-compose restart db
```

## Próximos Passos

1. **Configure suas API Keys** no `.env` para funcionalidades completas
2. **Customize o template** em `app/templates/default.html`
3. **Configure o WhatsApp** seguindo o guia no README.md
4. **Deploy em VPS** seguindo o guia em DEPLOY.md
5. **Explore a API** em http://localhost:8000/docs

## Suporte

- 📚 Documentação completa: [README.md](README.md)
- 🚀 Guia de deploy: [DEPLOY.md](DEPLOY.md)
- 📡 Referência da API: [API.md](API.md)
- 🔧 Issues: https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial/issues

---

**Dica**: Use o Swagger UI em `/docs` para testar todos os endpoints interativamente!
