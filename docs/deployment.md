# Deploy - Job Finder

## Visão Geral

Este documento descreve como fazer deploy da aplicação Job Finder em diferentes ambientes.

## Requisitos do Sistema

### Produção:
- Python 3.8+
- PostgreSQL 12+
- Nginx (opcional, para servir arquivos estáticos)
- Gunicorn ou uWSGI
- Redis (para caching e sessions)

### Desenvolvimento:
- Python 3.8+
- SQLite (banco de dados de desenvolvimento)

## Configuração do Ambiente

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd Pi_mobile
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie o arquivo de exemplo e configure as variáveis:

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 5. Configurar o banco de dados

```bash
# Para desenvolvimento (SQLite)
python manage.py migrate

# Para produção (PostgreSQL)
# Certifique-se de que o PostgreSQL está rodando e configurado
python manage.py migrate --settings=home_services.settings_production
```

### 6. Criar superusuário

```bash
python manage.py createsuperuser
```

## Deploy com Docker

### Usando docker-compose

```bash
# Construir e iniciar os containers
docker-compose up --build

# Em segundo plano
docker-compose up --build -d

# Parar os containers
docker-compose down
```

### Deploy manual com Docker

```bash
# Construir a imagem
docker build -t jobfinder .

# Rodar o container
docker run -p 8000:8000 jobfinder
```

## Deploy em Servidor Linux

### 1. Instalar dependências do sistema

```bash
sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

### 2. Configurar PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE jobfinder;
CREATE USER jobfinder_user WITH PASSWORD 'secure_password';
ALTER ROLE jobfinder_user SET client_encoding TO 'utf8';
ALTER ROLE jobfinder_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jobfinder_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE jobfinder TO jobfinder_user;
\q
```

### 3. Configurar a aplicação

```bash
# Criar diretório da aplicação
sudo mkdir -p /var/www/jobfinder
sudo chown $USER:$USER /var/www/jobfinder

# Copiar arquivos da aplicação
cp -r . /var/www/jobfinder

# Instalar dependências
cd /var/www/jobfinder
pip install -r requirements.txt
```

### 4. Configurar Gunicorn

```bash
# Instalar Gunicorn
pip install gunicorn

# Testar Gunicorn
gunicorn --bind 0.0.0.0:8000 home_services.wsgi:application
```

### 5. Configurar Systemd

Criar arquivo `/etc/systemd/system/jobfinder.service`:

```ini
[Unit]
Description=Job Finder Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/jobfinder
ExecStart=/var/www/jobfinder/venv/bin/gunicorn --workers 3 --bind unix:/var/www/jobfinder/jobfinder.sock home_services.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Habilitar e iniciar o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl start jobfinder
sudo systemctl enable jobfinder
```

### 6. Configurar Nginx

Criar arquivo `/etc/nginx/sites-available/jobfinder`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/jobfinder;
    }
    
    location /media/ {
        root /var/www/jobfinder;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/jobfinder/jobfinder.sock;
    }
}
```

Habilitar o site:

```bash
sudo ln -s /etc/nginx/sites-available/jobfinder /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Configurar SSL (opcional)

Usando Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## Deploy na Nuvem

### Heroku

1. Criar arquivo `Procfile`:

```
web: gunicorn home_services.wsgi:application
```

2. Instalar o Heroku CLI e fazer login
3. Criar app no Heroku
4. Fazer deploy:

```bash
git push heroku main
```

### AWS

1. Usar Elastic Beanstalk
2. Configurar RDS para PostgreSQL
3. Configurar S3 para arquivos estáticos

### Google Cloud Platform

1. Usar App Engine
2. Configurar Cloud SQL
3. Configurar Cloud Storage

## Variáveis de Ambiente

As seguintes variáveis devem ser configuradas em produção:

```bash
# Django
SECRET_KEY=chave-secreta-forte
DEBUG=False
DJANGO_ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Database
DB_NAME=nome-do-banco
DB_USER=usuario-do-banco
DB_PASSWORD=senha-do-banco
DB_HOST=endereco-do-banco
DB_PORT=5432

# Email
EMAIL_HOST=smtp.seu-provedor.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@provedor.com
EMAIL_HOST_PASSWORD=sua-senha

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_sua_chave_publicavel
STRIPE_SECRET_KEY=sk_live_sua_chave_secreta
```

## Backup e Recuperação

### Backup do banco de dados

```bash
# PostgreSQL
pg_dump -U jobfinder_user -h localhost jobfinder > backup.sql

# SQLite (desenvolvimento)
cp db.sqlite3 backup.sqlite3
```

### Restaurar backup

```bash
# PostgreSQL
psql -U jobfinder_user -h localhost jobfinder < backup.sql
```

## Monitoramento

### Logs

```bash
# Ver logs do Gunicorn
sudo journalctl -u jobfinder

# Ver logs do Nginx
sudo tail -f /var/log/nginx/error.log
```

### Health Checks

A aplicação inclui um endpoint de health check em `/health/` que verifica:

- Conexão com o banco de dados
- Status do cache
- Conectividade com serviços externos

Para verificar o status da aplicação manualmente:

```bash
# Usando curl
curl http://localhost:8000/health/

# Usando wget
wget -qO- http://localhost:8000/health/
```

## Manutenção

O sistema inclui vários comandos de manutenção úteis:

### Backup do banco de dados

```bash
# Criar backup completo
python manage.py backup_database --include-media --compress

# Criar backup apenas do banco de dados
python manage.py backup_database
```

### Limpeza de mensagens de chat antigas

```bash
# Remover mensagens com mais de 30 dias
python manage.py cleanup_chat_messages

# Remover mensagens com mais de 90 dias
python manage.py cleanup_chat_messages --days 90

# Ver o que seria removido sem realmente remover
python manage.py cleanup_chat_messages --days 90 --dry-run
```

### Exportação de dados do usuário (conformidade GDPR)

```bash
# Exportar dados de um usuário específico
python manage.py export_user_data --user-id 123 --format json

# Exportar em formato CSV
python manage.py export_user_data --user-id 123 --format csv
```

### Regenerar dados de exemplo (apenas desenvolvimento)

```bash
# Limpar dados existentes e importar novos dados de exemplo
python manage.py import_sample_data --clear-existing
```

## Atualizações

### Processo de atualização

1. Fazer backup do banco de dados
2. Parar o serviço:

```bash
sudo systemctl stop jobfinder
```

3. Atualizar o código:

```bash
cd /var/www/jobfinder
git pull origin main
```

4. Atualizar dependências:

```bash
pip install -r requirements.txt
```

5. Aplicar migrações:

```bash
python manage.py migrate
```

6. Coletar arquivos estáticos:

```bash
python manage.py collectstatic --noinput
```

7. Reiniciar o serviço:

```bash
sudo systemctl start jobfinder
```

## Troubleshooting

### Problemas comuns:

1. **502 Bad Gateway**: Verificar se o serviço Gunicorn está rodando
2. **Permission denied**: Verificar permissões de arquivos e diretórios
3. **Database connection failed**: Verificar configurações do banco de dados
4. **Static files not found**: Verificar configuração do Nginx e coleta de arquivos estáticos

### Comandos úteis:

```bash
# Ver status do serviço
sudo systemctl status jobfinder

# Ver logs do serviço
sudo journalctl -u jobfinder -f

# Testar configuração do Nginx
sudo nginx -t

# Reiniciar serviços
sudo systemctl restart jobfinder
sudo systemctl restart nginx
```