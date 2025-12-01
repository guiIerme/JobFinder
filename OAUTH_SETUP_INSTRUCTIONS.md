# Instruções de Configuração OAuth - Autenticação Social

Este documento contém as instruções para configurar a autenticação social com Google, Facebook e Microsoft.

## 📋 Pré-requisitos

1. Instalar o pacote django-allauth:
```bash
pip install django-allauth
```

2. Executar as migrações:
```bash
python manage.py migrate
```

## 🔐 Configuração das Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Google OAuth
GOOGLE_CLIENT_ID=seu_google_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_google_client_secret_aqui

# Facebook OAuth
FACEBOOK_CLIENT_ID=seu_facebook_app_id_aqui
FACEBOOK_CLIENT_SECRET=seu_facebook_app_secret_aqui

# Microsoft OAuth
MICROSOFT_CLIENT_ID=seu_microsoft_client_id_aqui
MICROSOFT_CLIENT_SECRET=seu_microsoft_client_secret_aqui
```

## 🌐 Google OAuth Setup

### 1. Criar Projeto no Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Vá para "APIs & Services" > "Credentials"

### 2. Configurar OAuth Consent Screen

1. Clique em "OAuth consent screen"
2. Selecione "External" e clique em "Create"
3. Preencha:
   - App name: Job Finder
   - User support email: seu_email@exemplo.com
   - Developer contact: seu_email@exemplo.com
4. Clique em "Save and Continue"
5. Em "Scopes", adicione:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
6. Clique em "Save and Continue"

### 3. Criar Credenciais OAuth

1. Vá para "Credentials" > "Create Credentials" > "OAuth client ID"
2. Selecione "Web application"
3. Nome: Job Finder Web Client
4. Authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - (Adicione suas URLs de produção quando disponível)
5. Clique em "Create"
6. Copie o **Client ID** e **Client Secret**

## 📘 Facebook OAuth Setup

### 1. Criar App no Facebook Developers

1. Acesse: https://developers.facebook.com/
2. Clique em "My Apps" > "Create App"
3. Selecione "Consumer" e clique em "Next"
4. Preencha:
   - App name: Job Finder
   - App contact email: seu_email@exemplo.com
5. Clique em "Create App"

### 2. Configurar Facebook Login

1. No dashboard do app, clique em "Add Product"
2. Encontre "Facebook Login" e clique em "Set Up"
3. Selecione "Web"
4. Em "Site URL", adicione: `http://localhost:8000`
5. Clique em "Save"

### 3. Configurar Valid OAuth Redirect URIs

1. Vá para "Facebook Login" > "Settings"
2. Em "Valid OAuth Redirect URIs", adicione:
   - `http://localhost:8000/accounts/facebook/login/callback/`
   - `http://127.0.0.1:8000/accounts/facebook/login/callback/`
3. Clique em "Save Changes"

### 4. Obter Credenciais

1. Vá para "Settings" > "Basic"
2. Copie o **App ID** (Client ID)
3. Clique em "Show" no **App Secret** e copie (Client Secret)

## 🔷 Microsoft OAuth Setup

### 1. Registrar App no Azure Portal

1. Acesse: https://portal.azure.com/
2. Vá para "Azure Active Directory" > "App registrations"
3. Clique em "New registration"
4. Preencha:
   - Name: Job Finder
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: 
     - Platform: Web
     - URI: `http://localhost:8000/accounts/microsoft/login/callback/`
5. Clique em "Register"

### 2. Obter Client ID

1. Na página de overview do app, copie o **Application (client) ID**

### 3. Criar Client Secret

1. Vá para "Certificates & secrets"
2. Clique em "New client secret"
3. Descrição: Job Finder Secret
4. Expires: 24 months (ou conforme preferência)
5. Clique em "Add"
6. **IMPORTANTE**: Copie o **Value** imediatamente (não será mostrado novamente)

### 4. Configurar Permissões

1. Vá para "API permissions"
2. Clique em "Add a permission"
3. Selecione "Microsoft Graph"
4. Selecione "Delegated permissions"
5. Adicione:
   - `User.Read`
   - `email`
   - `profile`
6. Clique em "Add permissions"

## 🔧 Configuração no Django Admin

Após configurar as credenciais, você precisa adicionar os Social Applications no Django Admin:

1. Execute o servidor: `python manage.py runserver`
2. Acesse: http://localhost:8000/admin/
3. Faça login como superusuário
4. Vá para "Social applications" > "Add social application"

### Para cada provedor (Google, Facebook, Microsoft):

1. **Provider**: Selecione o provedor (google/facebook/microsoft)
2. **Name**: Nome descritivo (ex: "Google OAuth")
3. **Client id**: Cole o Client ID obtido
4. **Secret key**: Cole o Client Secret obtido
5. **Sites**: Selecione "example.com" (ou seu site configurado)
6. Clique em "Save"

## 🧪 Testando

1. Acesse a página de login: http://localhost:8000/login/
2. Você verá os botões de login social
3. Clique em qualquer um deles para testar
4. Autorize o acesso quando solicitado
5. Você será redirecionado de volta ao sistema logado

## ⚠️ Notas Importantes

### Desenvolvimento Local

- Use `http://localhost:8000` ou `http://127.0.0.1:8000` consistentemente
- Certifique-se de que as URLs de callback estão corretas
- Alguns provedores podem não funcionar com `localhost` - use ngrok se necessário

### Produção

- Atualize as URLs de callback para seu domínio de produção
- Use HTTPS em produção
- Mantenha as credenciais seguras (use variáveis de ambiente)
- Configure `ALLOWED_HOSTS` corretamente no settings.py

### Segurança

- **NUNCA** commite as credenciais no Git
- Use `.env` e adicione ao `.gitignore`
- Rotacione as credenciais periodicamente
- Use diferentes credenciais para desenvolvimento e produção

## 🐛 Troubleshooting

### Erro: "redirect_uri_mismatch"
- Verifique se a URL de callback está exatamente igual no console do provedor
- Certifique-se de incluir a barra final `/`

### Erro: "invalid_client"
- Verifique se o Client ID e Secret estão corretos
- Certifique-se de que o app está configurado no Django Admin

### Erro: "Site matching query does not exist"
- Execute: `python manage.py migrate`
- Verifique se `SITE_ID = 1` está no settings.py
- Acesse o Django Admin e configure o Site

## 📚 Recursos Adicionais

- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
