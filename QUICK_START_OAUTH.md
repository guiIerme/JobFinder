# 🚀 Quick Start - Autenticação Social

## Instalação Rápida

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione suas credenciais OAuth
# (Veja OAUTH_SETUP_INSTRUCTIONS.md para obter as credenciais)
```

### 3. Executar Migrações

```bash
python manage.py migrate
```

### 4. Criar Superusuário (se ainda não tiver)

```bash
python manage.py createsuperuser
```

### 5. Configurar OAuth Automaticamente (Opcional)

```bash
python setup_oauth.py
```

Ou configure manualmente no Django Admin:
1. Acesse: http://localhost:8000/admin/
2. Vá para "Social applications"
3. Adicione as aplicações sociais

### 6. Iniciar o Servidor

```bash
python manage.py runserver
```

### 7. Testar

Acesse: http://localhost:8000/login/

Você verá os botões de login social:
- 🔴 Entrar com Google
- 🔵 Entrar com Facebook
- ⚫ Entrar com Microsoft

## 📝 Obtendo Credenciais OAuth

Consulte o arquivo `OAUTH_SETUP_INSTRUCTIONS.md` para instruções detalhadas sobre como obter as credenciais de cada provedor.

### Links Rápidos:

- **Google**: https://console.cloud.google.com/
- **Facebook**: https://developers.facebook.com/
- **Microsoft**: https://portal.azure.com/

## ⚙️ Configuração Mínima

Para testar rapidamente, você pode configurar apenas um provedor (ex: Google):

1. Obtenha as credenciais do Google
2. Adicione ao `.env`:
   ```
   GOOGLE_CLIENT_ID=seu_client_id
   GOOGLE_CLIENT_SECRET=seu_client_secret
   ```
3. Execute `python setup_oauth.py`
4. Teste o login com Google

## 🔧 Troubleshooting

### Erro: "Site matching query does not exist"
```bash
python manage.py migrate
python setup_oauth.py
```

### Erro: "redirect_uri_mismatch"
Verifique se a URL de callback está correta no console do provedor:
- Google: `http://localhost:8000/accounts/google/login/callback/`
- Facebook: `http://localhost:8000/accounts/facebook/login/callback/`
- Microsoft: `http://localhost:8000/accounts/microsoft/login/callback/`

### Botões não aparecem
1. Verifique se `django-allauth` está instalado
2. Execute as migrações
3. Limpe o cache do navegador

## 📚 Documentação Completa

Para instruções detalhadas, consulte:
- `OAUTH_SETUP_INSTRUCTIONS.md` - Guia completo de configuração
- [Django Allauth Docs](https://django-allauth.readthedocs.io/)

## 🎯 Funcionalidades

✅ Login com Google
✅ Login com Facebook  
✅ Login com Microsoft/Outlook
✅ Acesso automático ao email do usuário
✅ Criação automática de conta
✅ Integração com sistema de autenticação existente
