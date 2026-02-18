# 🚀 Guia de Deploy em VPS

Este guia detalha o processo completo de deploy da plataforma em uma VPS (Virtual Private Server).

## 📋 Pré-requisitos

- VPS com Ubuntu 22.04 LTS (mínimo 2GB RAM, 2 vCPUs, 20GB disco)
- Domínio próprio apontando para o IP da VPS
- Acesso root via SSH
- Credenciais das APIs (WhatsApp, OpenAI)

## 🔧 Servidores VPS Recomendados

- **DigitalOcean**: Droplet Basic (2GB RAM) - ~$12/mês
- **Vultr**: Cloud Compute (2GB RAM) - ~$12/mês
- **AWS EC2**: t3.small - ~$15/mês
- **Linode**: Linode 4GB - ~$24/mês
- **Hetzner**: CX21 (2 vCPU, 4GB RAM) - ~€5/mês

## 🚀 Instalação Passo a Passo

### 1. Configuração Inicial do Servidor

```bash
# Conecte via SSH
ssh root@SEU_IP_VPS

# Atualize o sistema
apt update && apt upgrade -y

# Instale pacotes básicos
apt install -y curl git nano ufw fail2ban
```

### 2. Configuração de Segurança

```bash
# Configure o firewall
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw enable

# Configure fail2ban (proteção contra brute force)
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Instalar Docker e Docker Compose

```bash
# Instale Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instale Docker Compose
apt install -y docker-compose-plugin

# Verifique instalação
docker --version
docker compose version
```

### 4. Configurar Domínio

```bash
# Aponte seu domínio para o IP da VPS
# No painel do seu registrador de domínio, adicione:
# Tipo A: @ -> SEU_IP_VPS
# Tipo A: www -> SEU_IP_VPS

# Verifique se está propagado
ping seu-dominio.com
```

### 5. Instalar Nginx

```bash
# Instale Nginx
apt install -y nginx

# Configure Nginx como proxy reverso
nano /etc/nginx/sites-available/leads-platform
```

Adicione a seguinte configuração:

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

```bash
# Ative o site
ln -s /etc/nginx/sites-available/leads-platform /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # Remove site padrão

# Teste a configuração
nginx -t

# Reinicie Nginx
systemctl restart nginx
```

### 6. Configurar SSL com Let's Encrypt

```bash
# Instale Certbot
apt install -y certbot python3-certbot-nginx

# Obtenha certificado SSL (gratuito)
certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Certbot vai pedir seu email e fazer configuração automática
# Escolha opção 2 para redirecionar HTTP para HTTPS

# Configure renovação automática
certbot renew --dry-run
```

### 7. Clone e Configure o Projeto

```bash
# Crie diretório para aplicação
mkdir -p /opt/leads-platform
cd /opt/leads-platform

# Clone o repositório
git clone https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial.git .

# Configure variáveis de ambiente
cp .env.example .env
nano .env
```

Configure as seguintes variáveis no `.env`:

```env
# Application
FLASK_ENV=production
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_AQUI
DEBUG=False

# Database (as credenciais do docker-compose)
DATABASE_URL=postgresql://leads_user:MUDE_ESTA_SENHA@db:5432/leads_platform

# WhatsApp Cloud API
WHATSAPP_API_TOKEN=seu_token_meta_aqui
WHATSAPP_PHONE_NUMBER_ID=seu_phone_number_id
WHATSAPP_VERIFY_TOKEN=crie_um_token_aleatorio_aqui
WHATSAPP_BUSINESS_ACCOUNT_ID=seu_business_account_id

# OpenAI
OPENAI_API_KEY=sua_chave_openai_aqui
OPENAI_MODEL=gpt-4-turbo-preview

# URLs
FRONTEND_URL=https://seu-dominio.com
BACKEND_URL=https://seu-dominio.com
WEBHOOK_BASE_URL=https://seu-dominio.com

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=GERE_OUTRA_CHAVE_SECRETA_FORTE
```

Para gerar chaves secretas fortes:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 8. Iniciar a Aplicação

```bash
# Inicie os containers
docker compose up -d

# Verifique se está rodando
docker compose ps

# Veja os logs
docker compose logs -f backend

# Para sair dos logs: Ctrl+C
```

### 9. Inicializar o Banco de Dados

```bash
# Execute as migrações
docker compose exec backend flask db upgrade

# Verifique se está funcionando
curl https://seu-dominio.com/health
```

### 10. Configurar Webhook do WhatsApp

1. Acesse Meta for Developers: https://developers.facebook.com/
2. Vá para seu app > WhatsApp > Configuration
3. Configure Webhook:
   - **Callback URL**: `https://seu-dominio.com/api/whatsapp/webhook`
   - **Verify Token**: (o mesmo que você colocou em WHATSAPP_VERIFY_TOKEN no .env)
4. Subscribe to fields: `messages`
5. Clique em "Verify and Save"

### 11. Criar uma Landing Page de Teste

```bash
# Entre no container
docker compose exec backend python

# No Python shell:
from app.models import db, LandingPage
from app import create_app

app = create_app('production')
with app.app_context():
    page = LandingPage(
        slug='teste',
        title='Página de Teste',
        neighborhood='Centro',
        hero_title='Bem-vindo à Nossa Plataforma',
        hero_subtitle='Entre em contato para saber mais',
        cta_text='Solicitar Orçamento',
        is_active=True
    )
    db.session.add(page)
    db.session.commit()
    print(f"Landing page criada: https://seu-dominio.com/landing/teste")
```

Ou via API:

```bash
curl -X POST https://seu-dominio.com/api/landing-pages \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "teste",
    "title": "Página de Teste",
    "neighborhood": "Centro",
    "hero_title": "Bem-vindo à Nossa Plataforma",
    "hero_subtitle": "Entre em contato para saber mais",
    "cta_text": "Solicitar Orçamento"
  }'
```

## 📊 Monitoramento

### Logs

```bash
# Ver todos os logs
docker compose logs -f

# Logs da aplicação
docker compose logs -f backend

# Logs do Celery worker
docker compose logs -f celery_worker

# Logs do PostgreSQL
docker compose logs -f db
```

### Status dos Containers

```bash
# Ver status
docker compose ps

# Reiniciar um serviço
docker compose restart backend

# Parar tudo
docker compose down

# Iniciar tudo
docker compose up -d
```

### Uso de Recursos

```bash
# Ver uso de recursos
docker stats

# Disco
df -h

# Memória
free -h
```

## 🔄 Atualizações

```bash
# Pare a aplicação
docker compose down

# Atualize o código
git pull origin main

# Reconstrua as imagens
docker compose build

# Inicie novamente
docker compose up -d

# Execute migrações se necessário
docker compose exec backend flask db upgrade
```

## 💾 Backup

### Backup do Banco de Dados

```bash
# Criar backup
docker compose exec db pg_dump -U leads_user leads_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker compose exec -T db psql -U leads_user leads_platform < backup_20240101_120000.sql
```

### Backup Automático (Cron)

```bash
# Edite crontab
crontab -e

# Adicione linha para backup diário às 3h da manhã
0 3 * * * cd /opt/leads-platform && docker compose exec -T db pg_dump -U leads_user leads_platform > /backups/leads_$(date +\%Y\%m\%d).sql
```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Veja os logs
docker compose logs backend

# Verifique configuração
docker compose config

# Recrie o container
docker compose up -d --force-recreate backend
```

### Erro de conexão com banco

```bash
# Verifique se o PostgreSQL está rodando
docker compose ps db

# Teste conexão
docker compose exec db psql -U leads_user -d leads_platform
```

### WhatsApp não recebe mensagens

1. Verifique logs: `docker compose logs backend | grep whatsapp`
2. Teste webhook manualmente: `curl https://seu-dominio.com/api/whatsapp/webhook`
3. Verifique configuração no Meta for Developers
4. Confirme que WEBHOOK_BASE_URL está correto no .env

### Erro 502 Bad Gateway

```bash
# Verifique se aplicação está rodando
docker compose ps

# Reinicie Nginx
systemctl restart nginx

# Verifique logs do Nginx
tail -f /var/log/nginx/error.log
```

## 🔒 Hardening de Segurança

### 1. Desabilitar login root direto via SSH

```bash
# Crie um usuário admin
adduser admin
usermod -aG sudo admin
usermod -aG docker admin

# Desabilite root login
nano /etc/ssh/sshd_config
# Altere: PermitRootLogin no

# Reinicie SSH
systemctl restart sshd
```

### 2. Configure backup remoto

Use serviços como:
- AWS S3
- DigitalOcean Spaces
- Backblaze B2

### 3. Monitoring com Uptime Robot

- Cadastre em https://uptimerobot.com (gratuito)
- Monitore: `https://seu-dominio.com/health`
- Configure alertas por email

## 📈 Performance

### Otimizações Recomendadas

1. **Redis caching**: Já incluído
2. **CDN**: Use Cloudflare (gratuito) na frente do domínio
3. **Compressão**: Nginx já comprime automaticamente
4. **HTTP/2**: Habilitado automaticamente com SSL

### Escalabilidade

Para mais de 10.000 leads/mês:

1. Aumente recursos da VPS (4GB RAM, 4 vCPUs)
2. Configure PostgreSQL para mais conexões
3. Adicione mais workers Celery
4. Use load balancer se necessário

## 💰 Custos Estimados

### Mensal
- VPS (2GB): $12-15
- Domínio: $1-2/mês (se anual)
- WhatsApp Cloud API: Gratuito até 1.000 conversas/mês
- OpenAI API: ~$20-50 (depende do uso)
- **Total**: ~$35-70/mês

## ✅ Checklist de Deploy

- [ ] VPS configurada e atualizada
- [ ] Domínio apontando para VPS
- [ ] Docker e Docker Compose instalados
- [ ] Nginx configurado
- [ ] SSL configurado (Let's Encrypt)
- [ ] Projeto clonado
- [ ] .env configurado com todas as credenciais
- [ ] Containers rodando
- [ ] Banco de dados inicializado
- [ ] Webhook do WhatsApp configurado
- [ ] Landing page de teste criada
- [ ] Backup automático configurado
- [ ] Monitoramento configurado

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs: `docker compose logs -f`
2. Consulte DOCUMENTATION.md
3. Abra uma issue no GitHub

---

**Boa sorte com seu deploy! 🚀**
