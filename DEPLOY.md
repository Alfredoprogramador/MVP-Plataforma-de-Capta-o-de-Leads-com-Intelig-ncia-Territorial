# Guia de Deploy em VPS

Este guia detalha o processo completo de deploy da plataforma em uma VPS Linux.

## Pré-requisitos

- VPS com Ubuntu 20.04+ ou Debian 11+
- Mínimo 2GB RAM, 2 vCPUs
- 20GB de armazenamento
- Acesso SSH root ou sudo
- Domínio configurado (opcional, mas recomendado)

## Passo 1: Preparar o Servidor

### 1.1 Atualizar o sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Instalar Docker

```bash
# Remover versões antigas (se existirem)
sudo apt remove docker docker-engine docker.io containerd runc

# Instalar dependências
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Verificar instalação
docker --version
```

### 1.3 Instalar Docker Compose

```bash
# Baixar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker-compose --version
```

### 1.4 Instalar Git

```bash
sudo apt install -y git
```

## Passo 2: Clonar e Configurar a Aplicação

### 2.1 Clonar repositório

```bash
cd /opt
sudo git clone https://github.com/Alfredoprogramador/MVP-Plataforma-de-Capta-o-de-Leads-com-Intelig-ncia-Territorial.git leads-platform
cd leads-platform
```

### 2.2 Configurar variáveis de ambiente

```bash
sudo cp .env.example .env
sudo nano .env
```

Configure as seguintes variáveis:

```env
# Database
DATABASE_URL=postgresql://leads_user:SENHA_FORTE_AQUI@db:5432/leads_db

# API Keys
OPENAI_API_KEY=sk-sua-chave-openai-aqui
WHATSAPP_API_TOKEN=seu-token-whatsapp-aqui
WHATSAPP_PHONE_NUMBER_ID=seu-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=seu-business-account-id

# Security
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_AQUI
WEBHOOK_VERIFY_TOKEN=ESCOLHA_UM_TOKEN_ALEATORIO

# Base URL
BASE_URL=https://seu-dominio.com
# ou
BASE_URL=http://SEU_IP_VPS:8000

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=False
```

Para gerar uma SECRET_KEY segura:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 Criar diretórios necessários

```bash
sudo mkdir -p media logs
sudo chmod 755 media logs
```

## Passo 3: Iniciar a Aplicação

### 3.1 Build e start dos containers

```bash
sudo docker-compose up -d --build
```

### 3.2 Verificar status dos containers

```bash
sudo docker-compose ps
```

Todos os containers devem estar "Up":
- db (PostgreSQL)
- redis
- app (API)
- celery_worker
- celery_beat

### 3.3 Ver logs

```bash
# Logs de todos os serviços
sudo docker-compose logs -f

# Logs de um serviço específico
sudo docker-compose logs -f app
sudo docker-compose logs -f celery_worker
```

### 3.4 Testar a aplicação

```bash
curl http://localhost:8000/health
```

Deve retornar: `{"status":"healthy","version":"1.0.0"}`

## Passo 4: Configurar Nginx (Recomendado)

### 4.1 Instalar Nginx

```bash
sudo apt install -y nginx
```

### 4.2 Criar configuração

```bash
sudo nano /etc/nginx/sites-available/leads-platform
```

Cole a seguinte configuração:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;  # Substitua pelo seu domínio

    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static {
        alias /opt/leads-platform/app/static;
        expires 30d;
    }

    location /media {
        alias /opt/leads-platform/media;
        expires 30d;
    }
}
```

### 4.3 Ativar configuração

```bash
sudo ln -s /etc/nginx/sites-available/leads-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4.4 Configurar Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Passo 5: Configurar SSL/HTTPS (Recomendado)

### 5.1 Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 5.2 Obter certificado SSL

```bash
sudo certbot --nginx -d seu-dominio.com
```

Siga as instruções:
- Forneça um email
- Aceite os termos
- Escolha redirecionar HTTP para HTTPS (opção 2)

### 5.3 Renovação automática

O Certbot configura renovação automática. Teste com:

```bash
sudo certbot renew --dry-run
```

## Passo 6: Configurar WhatsApp Webhook

### 6.1 No Facebook Developers

1. Acesse https://developers.facebook.com/
2. Vá para seu App > WhatsApp > Configuration
3. Configure o Webhook:
   - **Callback URL**: `https://seu-dominio.com/api/whatsapp/webhook`
   - **Verify Token**: (use o mesmo que está no .env)
4. Subscreva aos campos:
   - `messages`
   - `message_status`

### 6.2 Testar webhook

```bash
curl "https://seu-dominio.com/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=SEU_TOKEN&hub.challenge=test"
```

Deve retornar: `test`

## Passo 7: Configurar Backup Automático

### 7.1 Criar script de backup

```bash
sudo nano /opt/backup-leads.sh
```

Cole o script:

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
docker exec leads-platform_db_1 pg_dump -U leads_user leads_db | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup de arquivos
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/leads-platform/media

# Manter apenas últimos 7 backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 7.2 Tornar executável

```bash
sudo chmod +x /opt/backup-leads.sh
```

### 7.3 Agendar com cron

```bash
sudo crontab -e
```

Adicione:

```cron
# Backup diário às 2h da manhã
0 2 * * * /opt/backup-leads.sh >> /var/log/leads-backup.log 2>&1
```

## Passo 8: Monitoramento

### 8.1 Verificar logs da aplicação

```bash
# Logs do Docker
sudo docker-compose logs -f app

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 8.2 Verificar uso de recursos

```bash
# Uso de containers
docker stats

# Uso do servidor
htop  # ou top
df -h
free -h
```

## Passo 9: Manutenção

### 9.1 Atualizar aplicação

```bash
cd /opt/leads-platform
sudo git pull
sudo docker-compose down
sudo docker-compose up -d --build
```

### 9.2 Reiniciar serviços

```bash
# Reiniciar todos os containers
sudo docker-compose restart

# Reiniciar apenas a aplicação
sudo docker-compose restart app

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 9.3 Ver logs de erros

```bash
# Logs da aplicação
sudo docker-compose logs --tail=100 app

# Logs do Celery
sudo docker-compose logs --tail=100 celery_worker
```

## Passo 10: Criar Landing Page de Exemplo

### 10.1 Via API

```bash
curl -X POST "https://seu-dominio.com/api/landing-pages/" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "centro-sp",
    "title": "Serviços no Centro de São Paulo",
    "neighborhood": "Centro",
    "city": "São Paulo",
    "state": "SP",
    "template_name": "default",
    "meta_title": "Melhores Serviços no Centro de SP",
    "meta_description": "Encontre os melhores serviços para o Centro de São Paulo"
  }'
```

### 10.2 Acessar a landing page

Acesse: `https://seu-dominio.com/lp/centro-sp`

## Troubleshooting

### Containers não iniciam

```bash
# Ver logs completos
sudo docker-compose logs

# Verificar se portas estão em uso
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :5432
```

### Banco de dados não conecta

```bash
# Entrar no container do banco
sudo docker-compose exec db psql -U leads_user -d leads_db

# Verificar se banco existe
\l

# Sair
\q
```

### WhatsApp webhook não funciona

1. Verifique se a URL está acessível externamente
2. Verifique o verify_token no .env
3. Veja os logs: `sudo docker-compose logs -f app`
4. Teste manualmente o endpoint

### Alto uso de memória

```bash
# Limpar containers e imagens não usados
docker system prune -a

# Verificar uso por container
docker stats
```

## Comandos Úteis

```bash
# Parar todos os containers
sudo docker-compose down

# Iniciar sem build
sudo docker-compose up -d

# Rebuild completo
sudo docker-compose up -d --build --force-recreate

# Ver containers ativos
sudo docker ps

# Entrar em um container
sudo docker-compose exec app bash

# Executar comando no container
sudo docker-compose exec app python -c "from app.database import engine; print(engine)"
```

## Segurança Adicional

### Fail2Ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Updates automáticos

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs
2. Consulte a documentação da API em `/docs`
3. Abra uma issue no GitHub
