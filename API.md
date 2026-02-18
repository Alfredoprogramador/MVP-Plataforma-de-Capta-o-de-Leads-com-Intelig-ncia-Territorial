# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://seu-dominio.com`

## Authentication

Atualmente a API não requer autenticação. Em produção, recomenda-se adicionar autenticação JWT.

## Endpoints

### Health Check

#### GET /health

Verifica se a aplicação está rodando.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Leads

### Create Lead

#### POST /api/leads/

Cria um novo lead.

**Request Body:**
```json
{
  "name": "João Silva",
  "phone": "+5511999999999",
  "email": "joao@example.com",
  "neighborhood": "Centro",
  "city": "São Paulo",
  "state": "SP",
  "source": "landing_page",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "campanha-janeiro"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "João Silva",
  "phone": "+5511999999999",
  "email": "joao@example.com",
  "neighborhood": "Centro",
  "city": "São Paulo",
  "state": "SP",
  "source": "landing_page",
  "status": "new",
  "temperature": "unqualified",
  "score": 0,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "last_interaction_at": null
}
```

### List Leads

#### GET /api/leads/

Lista leads com filtros opcionais.

**Query Parameters:**
- `skip` (int): Número de registros a pular (default: 0)
- `limit` (int): Número máximo de registros (default: 100)
- `status` (string): Filtrar por status (new, contacted, qualified, etc.)
- `temperature` (string): Filtrar por temperatura (hot, warm, cold)
- `neighborhood` (string): Filtrar por bairro
- `source` (string): Filtrar por origem

**Example:**
```
GET /api/leads/?status=qualified&temperature=hot&limit=20
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "João Silva",
    "phone": "+5511999999999",
    ...
  }
]
```

### Get Lead

#### GET /api/leads/{lead_id}

Obtém detalhes de um lead específico.

**Response:** `200 OK`

### Update Lead

#### PUT /api/leads/{lead_id}

Atualiza um lead.

**Request Body:**
```json
{
  "name": "João Silva Junior",
  "status": "qualified",
  "temperature": "hot",
  "score": 85,
  "notes": "Lead muito interessado, pronto para proposta"
}
```

### Delete Lead

#### DELETE /api/leads/{lead_id}

Deleta um lead.

**Response:** `200 OK`

### Get Lead Messages

#### GET /api/leads/{lead_id}/messages

Lista todas as mensagens de um lead.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "lead_id": 1,
    "content": "Olá, gostaria de mais informações",
    "message_type": "text",
    "is_from_lead": true,
    "sent": true,
    "delivered": true,
    "read": false,
    "created_at": "2024-01-15T10:35:00"
  }
]
```

### Get Analytics

#### GET /api/leads/stats/analytics

Retorna estatísticas e métricas dos leads.

**Response:** `200 OK`
```json
{
  "total_leads": 150,
  "new_leads": 45,
  "qualified_leads": 30,
  "converted_leads": 20,
  "leads_by_status": {
    "new": 45,
    "contacted": 25,
    "qualified": 30,
    "proposal_sent": 15,
    "converted": 20
  },
  "leads_by_temperature": {
    "hot": 25,
    "warm": 50,
    "cold": 40,
    "unqualified": 35
  },
  "leads_by_neighborhood": {
    "Centro": 50,
    "Vila Mariana": 30,
    "Pinheiros": 40
  },
  "leads_by_source": {
    "landing_page": 80,
    "whatsapp": 40,
    "instagram": 30
  }
}
```

---

## Landing Pages

### Create Landing Page

#### POST /api/landing-pages/

Cria uma nova landing page.

**Request Body:**
```json
{
  "slug": "centro-sp",
  "title": "Serviços no Centro de São Paulo",
  "neighborhood": "Centro",
  "city": "São Paulo",
  "state": "SP",
  "template_name": "default",
  "template_data": {
    "subtitle": "As melhores soluções para sua empresa"
  },
  "meta_title": "Serviços Centro SP",
  "meta_description": "Encontre os melhores serviços no Centro de São Paulo"
}
```

**Response:** `201 Created`

### List Landing Pages

#### GET /api/landing-pages/

Lista landing pages.

**Query Parameters:**
- `skip` (int)
- `limit` (int)
- `neighborhood` (string)
- `is_active` (boolean)

### Submit Landing Page Form

#### POST /api/landing-pages/{page_id}/submit

Submete formulário de lead de uma landing page.

**Request Body:**
```json
{
  "name": "Maria Santos",
  "phone": "+5511988888888",
  "email": "maria@example.com",
  "message": "Gostaria de mais informações sobre os serviços"
}
```

**Query Parameters (UTM):**
- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_content`
- `utm_term`

**Example:**
```
POST /api/landing-pages/1/submit?utm_source=google&utm_medium=cpc&utm_campaign=janeiro
```

**Response:** `200 OK`
```json
{
  "message": "Lead submitted successfully",
  "lead_id": 15
}
```

---

## WhatsApp

### Verify Webhook

#### GET /api/whatsapp/webhook

Endpoint para verificação do webhook do WhatsApp.

**Query Parameters:**
- `hub.mode`: subscribe
- `hub.verify_token`: seu token de verificação
- `hub.challenge`: challenge string

### Receive Messages

#### POST /api/whatsapp/webhook

Recebe mensagens do WhatsApp (chamado automaticamente pelo WhatsApp).

### Send Message

#### POST /api/whatsapp/send

Envia mensagem via WhatsApp manualmente.

**Request Body:**
```json
{
  "phone": "+5511999999999",
  "message": "Olá! Como podemos ajudar?",
  "message_type": "text"
}
```

Para enviar mídia:
```json
{
  "phone": "+5511999999999",
  "message": "Confira nossa proposta",
  "message_type": "image",
  "media_url": "https://exemplo.com/imagem.jpg"
}
```

**Response:** `200 OK`

---

## Proposals

### Create Proposal

#### POST /api/proposals/

Cria uma proposta para um lead.

**Request Body:**
```json
{
  "lead_id": 1,
  "title": "Proposta de Serviço Premium",
  "description": "Incluindo:\n- Serviço A\n- Serviço B\n- Suporte 24/7",
  "amount": 1500.00
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "lead_id": 1,
  "title": "Proposta de Serviço Premium",
  "description": "...",
  "amount": 1500.00,
  "pdf_path": "/app/media/proposals/proposal_1_20240115.pdf",
  "proposal_link": "http://localhost:8000/proposals/1",
  "is_accepted": false,
  "accepted_at": null,
  "created_at": "2024-01-15T11:00:00",
  "expires_at": "2024-01-22T11:00:00"
}
```

### List Proposals

#### GET /api/proposals/

Lista propostas.

**Query Parameters:**
- `skip` (int)
- `limit` (int)
- `lead_id` (int): Filtrar por lead
- `is_accepted` (boolean): Filtrar por aceitas/não aceitas

### Get Proposal

#### GET /api/proposals/{proposal_id}

Obtém detalhes de uma proposta.

### Download Proposal PDF

#### GET /api/proposals/{proposal_id}/pdf

Baixa o PDF da proposta.

**Response:** PDF file

### Accept Proposal

#### POST /api/proposals/{proposal_id}/accept

Aceita uma proposta.

**Response:** `200 OK`
```json
{
  "message": "Proposal accepted successfully"
}
```

### View Proposal Page

#### GET /api/proposals/{proposal_id}/view

Visualiza página HTML de aceite da proposta.

**Response:** HTML page

---

## Public Routes

### Landing Page

#### GET /lp/{slug}

Renderiza landing page pública.

**Example:**
```
GET /lp/centro-sp
```

Retorna página HTML renderizada.

### Proposal Acceptance Page

#### GET /proposals/{proposal_id}

Página pública para aceite de proposta.

---

## Status Codes

- `200 OK`: Sucesso
- `201 Created`: Recurso criado
- `400 Bad Request`: Dados inválidos
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro do servidor

---

## Rate Limiting

Atualmente não há rate limiting implementado. Recomenda-se adicionar em produção.

---

## Webhooks

### WhatsApp Webhook Configuration

Configure seu webhook do WhatsApp para apontar para:

```
https://seu-dominio.com/api/whatsapp/webhook
```

O webhook receberá:
- Mensagens recebidas
- Status de mensagens (enviada, entregue, lida)

---

## Examples

### Complete Lead Flow

1. **Lead capturado via landing page:**
```bash
POST /api/landing-pages/1/submit
{
  "name": "João Silva",
  "phone": "+5511999999999",
  "email": "joao@example.com"
}
```

2. **Lead recebe mensagem automática via WhatsApp** (automático)

3. **Conversa com IA qualifica o lead** (automático)

4. **Admin cria proposta:**
```bash
POST /api/proposals/
{
  "lead_id": 1,
  "title": "Proposta Comercial",
  "description": "Detalhes...",
  "amount": 1500.00
}
```

5. **Lead recebe proposta via WhatsApp** (automático)

6. **Lead aceita proposta:**
```bash
POST /api/proposals/1/accept
```

7. **Sistema notifica equipe de vendas** (automático)

---

## Testing

### Test Health
```bash
curl http://localhost:8000/health
```

### Test Webhook Verification
```bash
curl "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=your-token&hub.challenge=test"
```

### Create Test Lead
```bash
curl -X POST http://localhost:8000/api/leads/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"+5511999999999","source":"test"}'
```

### Get Analytics
```bash
curl http://localhost:8000/api/leads/stats/analytics
```

---

Para documentação interativa completa, acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
