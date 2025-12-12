#!/bin/bash

# Script de inicialização para Railway
echo "🚀 Iniciando aplicação Django..."

# Definir porta padrão se não estiver definida
export PORT=${PORT:-8000}

echo "📊 Porta configurada: $PORT"

# Executar migrações
echo "🔄 Executando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar servidor com Gunicorn
echo "🌐 Iniciando servidor Gunicorn na porta $PORT..."
exec gunicorn home_services.wsgi:application --bind 0.0.0.0:$PORT --workers 2