#!/usr/bin/env bash
# build.sh - Script de build para o Render

set -o errexit  # exit on error

echo "🚀 Iniciando build para o Render..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "🗃️ Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🔄 Executando migrações..."
python manage.py migrate

echo "✅ Build concluído com sucesso!"