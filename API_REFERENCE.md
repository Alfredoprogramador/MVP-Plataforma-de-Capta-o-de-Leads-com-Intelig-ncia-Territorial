# 📚 API Reference - Quick Guide

## Base URL
```
Development: http://localhost:5000
Production: https://seu-dominio.com
```

## Authentication
Currently, the API does not require authentication for most endpoints. For production, consider implementing JWT authentication.

## Endpoints

### Health Check
```bash
GET /health
```
Response:
```json
{"status": "healthy"}
```

### Leads

#### Create Lead
```bash
POST /api/leads
Content-Type: application/json

{
  "name": "João Silva",
  "phone": "11999999999",
  "email": "joao@email.com",
  "neighborhood": "Jardim Paulista",
  "city": "São Paulo",
  "state": "SP",
  "source": "landing_page",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "summer",
  "landing_page_id": 1,
  "notes": "Interessado em serviços"
}
```

#### List Leads
```bash
GET /api/leads?page=1&per_page=20&neighborhood=Centro&status=new&temperature=hot
```

Query Parameters:
- `page` (int): Page number
- `per_page` (int): Results per page (max 100)
- `neighborhood` (string): Filter by neighborhood
- `status` (string): new, contacted, qualified, proposal_sent, accepted, rejected
- `temperature` (string): hot, warm, cold
- `source` (string): landing_page, whatsapp, instagram, google

#### Get Lead
```bash
GET /api/leads/{id}
```

#### Update Lead
```bash
PUT /api/leads/{id}
Content-Type: application/json

{
  "status": "contacted",
  "score": 75,
  "temperature": "hot",
  "notes": "Lead muito interessado"
}
```

#### Get Statistics
```bash
GET /api/leads/stats
```

Response:
```json
{
  "total_leads": 150,
  "by_temperature": {
    "hot": 30,
    "warm": 70,
    "cold": 50
  },
  "by_status": {
    "new": 20,
    "contacted": 60,
    "qualified": 40,
    "proposal_sent": 20,
    "accepted": 10
  },
  "conversion_rate": 6.67
}
```

### Landing Pages

#### Create Landing Page
```bash
POST /api/landing-pages
Content-Type: application/json

{
  "slug": "jardim-paulista",
  "title": "Serviços no Jardim Paulista",
  "neighborhood": "Jardim Paulista",
  "hero_title": "Soluções Completas no Jardim Paulista",
  "hero_subtitle": "Atendemos sua região com excelência",
  "hero_image_url": "https://example.com/image.jpg",
  "content_sections": [
    {
      "title": "Nossos Serviços",
      "content": "Oferecemos serviços de alta qualidade..."
    }
  ],
  "cta_text": "Solicitar Orçamento",
  "cta_button_color": "#0066cc",
  "is_active": true
}
```

#### List Landing Pages
```bash
GET /api/landing-pages?neighborhood=Centro
```

#### Update Landing Page
```bash
PUT /api/landing-pages/{id}
Content-Type: application/json

{
  "title": "Novo Título",
  "is_active": true
}
```

#### View Landing Page (Browser)
```
GET /landing/{slug}
```

### WhatsApp

#### Webhook Verification (GET)
```bash
GET /api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=CHALLENGE
```

#### Webhook Messages (POST)
```bash
POST /api/whatsapp/webhook
Content-Type: application/json

# This is called automatically by WhatsApp Cloud API
```

#### Send Manual Message
```bash
POST /api/whatsapp/send
Content-Type: application/json

{
  "lead_id": 1,
  "phone": "5511999999999",
  "type": "text",
  "message": "Olá! Como podemos ajudar?"
}
```

#### Send Media Message
```bash
POST /api/whatsapp/send
Content-Type: application/json

{
  "lead_id": 1,
  "phone": "5511999999999",
  "type": "image",
  "media_url": "https://example.com/image.jpg",
  "caption": "Confira nossa oferta especial!"
}
```

### Proposals

#### Create Proposal
```bash
POST /api/proposals
Content-Type: application/json

{
  "lead_id": 1,
  "title": "Proposta de Serviço - Cliente João",
  "description": "Proposta para instalação completa",
  "service_items": [
    {
      "name": "Instalação Básica",
      "description": "Instalação de equipamentos básicos",
      "value": 500.00
    },
    {
      "name": "Manutenção",
      "description": "Manutenção mensal durante 6 meses",
      "value": 300.00
    }
  ],
  "total_value": 800.00,
  "validity_days": 7
}
```

Response:
```json
{
  "message": "Proposal created successfully",
  "proposal": {
    "id": 1,
    "lead_id": 1,
    "title": "Proposta de Serviço - Cliente João",
    "total_value": 800.00,
    "status": "pending",
    "pdf_url": "http://localhost:5000/uploads/proposal_1_20240101_120000.pdf",
    "view_url": "http://localhost:5000/proposal/1/view",
    "valid_until": "2024-01-08T12:00:00"
  }
}
```

#### Get Proposal
```bash
GET /api/proposals/{id}
```

#### View Proposal (Browser)
```
GET /proposal/{id}/view
```

#### Accept Proposal
```bash
POST /api/proposals/{id}/accept
```

#### Reject Proposal
```bash
POST /api/proposals/{id}/reject
Content-Type: application/json

{
  "reason": "Preço muito alto"
}
```

### Admin Dashboard

#### View Dashboard
```
GET /admin
```

## Response Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

## Error Format

```json
{
  "error": "Error message description"
}
```

## Examples with curl

### Create a complete workflow

```bash
# 1. Create landing page
curl -X POST http://localhost:5000/api/landing-pages \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "test-page",
    "title": "Test Landing Page",
    "neighborhood": "Centro",
    "hero_title": "Welcome!",
    "cta_text": "Get Quote"
  }'

# 2. Create lead (simulating form submission)
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "phone": "11999999999",
    "email": "test@example.com",
    "neighborhood": "Centro",
    "landing_page_id": 1,
    "utm_source": "google"
  }'

# 3. Get lead details
curl http://localhost:5000/api/leads/1

# 4. Create proposal
curl -X POST http://localhost:5000/api/proposals \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 1,
    "title": "Service Proposal",
    "total_value": 500.00,
    "service_items": [
      {"name": "Service A", "description": "Description", "value": 500.00}
    ]
  }'

# 5. Get statistics
curl http://localhost:5000/api/leads/stats
```

## Python Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:5000"

# Create lead
response = requests.post(
    f"{BASE_URL}/api/leads",
    json={
        "name": "João Silva",
        "phone": "11999999999",
        "email": "joao@email.com",
        "neighborhood": "Jardim Paulista"
    }
)
lead = response.json()
print(f"Lead created: {lead['lead']['id']}")

# List leads
response = requests.get(
    f"{BASE_URL}/api/leads",
    params={"temperature": "hot", "page": 1}
)
leads = response.json()
print(f"Found {leads['total']} leads")

# Create proposal
response = requests.post(
    f"{BASE_URL}/api/proposals",
    json={
        "lead_id": lead['lead']['id'],
        "title": "Proposta Comercial",
        "total_value": 800.00,
        "service_items": [
            {
                "name": "Serviço Premium",
                "description": "Pacote completo",
                "value": 800.00
            }
        ]
    }
)
proposal = response.json()
print(f"Proposal URL: {proposal['proposal']['view_url']}")
```

## JavaScript Examples

### Using fetch API

```javascript
const BASE_URL = 'http://localhost:5000';

// Create lead
async function createLead() {
  const response = await fetch(`${BASE_URL}/api/leads`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'Maria Santos',
      phone: '11988888888',
      email: 'maria@email.com',
      neighborhood: 'Vila Mariana'
    })
  });
  
  const data = await response.json();
  console.log('Lead created:', data.lead.id);
  return data.lead;
}

// Get statistics
async function getStats() {
  const response = await fetch(`${BASE_URL}/api/leads/stats`);
  const stats = await response.json();
  console.log('Total leads:', stats.total_leads);
  console.log('Conversion rate:', stats.conversion_rate + '%');
}

// Usage
createLead().then(lead => {
  console.log('Created lead:', lead);
});
```

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Implement rate limiting per IP
- Recommended: 100 requests per minute per IP
- Use Flask-Limiter or similar

## Webhooks

### WhatsApp Webhook
The platform receives webhooks from WhatsApp Cloud API at:
```
POST /api/whatsapp/webhook
```

Configure in Meta for Developers:
- URL: `https://seu-dominio.com/api/whatsapp/webhook`
- Verify Token: Value from `.env` WHATSAPP_VERIFY_TOKEN

## Best Practices

1. **Always validate input** before sending to API
2. **Use HTTPS** in production
3. **Handle errors gracefully** in your client
4. **Implement retry logic** for failed requests
5. **Cache responses** when appropriate
6. **Use pagination** for large datasets

## Support

For issues or questions:
- Check DOCUMENTATION.md
- Review DEPLOY_GUIDE.md
- Open an issue on GitHub
