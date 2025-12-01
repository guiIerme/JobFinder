#!/bin/bash

# Script de deploy para Job Finder
# Este script automatiza o processo de deploy da aplicação

echo "Iniciando processo de deploy do Job Finder..."

# Verificar se o virtual environment existe, se não, criá-lo
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python -m venv venv
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar/atualizar dependências
echo "Instalando/atualizando dependências..."
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Aplicar migrações
echo "Aplicando migrações do banco de dados..."
python manage.py migrate

# Criar superusuário se não existir
echo "Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@jobfinder.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

# Reiniciar o servidor (exemplo com gunicorn)
echo "Reiniciando o servidor..."
# pkill gunicorn
# gunicorn --bind 0.0.0.0:8000 home_services.wsgi:application &

echo "Deploy concluído com sucesso!"
echo "A aplicação está disponível em http://localhost:8000"