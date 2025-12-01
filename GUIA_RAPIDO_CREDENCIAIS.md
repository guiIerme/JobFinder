# 🚀 Guia Rápido - Como Obter Credenciais OAuth

## ⚠️ IMPORTANTE
As credenciais atuais no `.env` são apenas exemplos e **NÃO FUNCIONAM**.
Você precisa obter credenciais reais dos provedores.

## 🔴 GOOGLE - Mais Fácil (Recomendado para começar)

### Passo 1: Criar Projeto
1. Acesse: https://console.cloud.google.com/
2. Clique em "Select a project" > "NEW PROJECT"
3. Nome: `Job Finder`
4. Clique em "CREATE"

### Passo 2: Configurar OAuth Consent Screen
1. No menu lateral: "APIs & Services" > "OAuth consent screen"
2. Selecione "External"
3. Clique em "CREATE"
4. Preencha:
   - App name: `Job Finder`
   - User support email: seu email
   - Developer contact: seu email
5. Clique em "SAVE AND CONTINUE"
6. Em "Scopes", clique em "ADD OR REMOVE SCOPES"
7. Selecione:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
8. Clique em "UPDATE" > "SAVE AND CONTINUE"
9. Em "Test users", adicione seu email
10. Clique em "SAVE AND CONTINUE"

### Passo 3: Criar Credenciais
1. No menu lateral: "Credentials"
2. Clique em "CREATE CREDENTIALS" > "OAuth client ID"
3. Application type: "Web application"
4. Name: `Job Finder Web`
5. Em "Authorized redirect URIs", clique em "ADD URI" e adicione:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
6. Clique em "CREATE"
7. **COPIE** o Client ID e Client Secret que aparecem

### Passo 4: Adicionar ao .env
Edite o arquivo `.env` e substitua:
```env
GOOGLE_CLIENT_ID=cole_aqui_o_client_id_real
GOOGLE_CLIENT_SECRET=cole_aqui_o_client_secret_real
```

### Passo 5: Atualizar no Django
```bash
python manage.py setup_social_auth
```

### Passo 6: Testar
```bash
python manage.py runserver
```
Acesse: http://localhost:8000/login/ e clique em "Entrar com Google"

---

## 🔵 FACEBOOK (Opcional)

### Passo 1: Criar App
1. Acesse: https://developers.facebook.com/
2. Clique em "My Apps" > "Create App"
3. Selecione "Consumer" > "Next"
4. App name: `Job Finder`
5. App contact email: seu email
6. Clique em "Create App"

### Passo 2: Adicionar Facebook Login
1. No dashboard, clique em "Add Product"
2. Encontre "Facebook Login" > "Set Up"
3. Selecione "Web"
4. Site URL: `http://localhost:8000`
5. Clique em "Save"

### Passo 3: Configurar Redirect URIs
1. Menu lateral: "Facebook Login" > "Settings"
2. Em "Valid OAuth Redirect URIs", adicione:
   ```
   http://localhost:8000/accounts/facebook/login/callback/
   ```
3. Clique em "Save Changes"

### Passo 4: Obter Credenciais
1. Menu lateral: "Settings" > "Basic"
2. **COPIE** o "App ID" (Client ID)
3. Clique em "Show" no "App Secret" e **COPIE**

### Passo 5: Adicionar ao .env
```env
FACEBOOK_CLIENT_ID=cole_aqui_o_app_id
FACEBOOK_CLIENT_SECRET=cole_aqui_o_app_secret
```

### Passo 6: Modo de Desenvolvimento
1. No topo da página, mude de "In development" para "Live"
2. Ou adicione usuários de teste em "Roles" > "Test Users"

---

## ⚫ MICROSOFT (Opcional)

### Passo 1: Registrar App
1. Acesse: https://portal.azure.com/
2. Procure por "Azure Active Directory"
3. Menu lateral: "App registrations" > "New registration"
4. Name: `Job Finder`
5. Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
6. Redirect URI:
   - Platform: Web
   - URI: `http://localhost:8000/accounts/microsoft/login/callback/`
7. Clique em "Register"

### Passo 2: Obter Client ID
1. Na página Overview, **COPIE** o "Application (client) ID"

### Passo 3: Criar Client Secret
1. Menu lateral: "Certificates & secrets"
2. Clique em "New client secret"
3. Description: `Job Finder Secret`
4. Expires: 24 months
5. Clique em "Add"
6. **COPIE IMEDIATAMENTE** o "Value" (não será mostrado novamente!)

### Passo 4: Adicionar ao .env
```env
MICROSOFT_CLIENT_ID=cole_aqui_o_application_id
MICROSOFT_CLIENT_SECRET=cole_aqui_o_secret_value
```

---

## 🔧 Após Configurar as Credenciais

### 1. Atualizar no Django
```bash
python manage.py setup_social_auth
```

### 2. Verificar Configuração
```bash
python check_oauth_config.py
```

### 3. Reiniciar o Servidor
```bash
python manage.py runserver
```

### 4. Testar
1. Acesse: http://localhost:8000/login/
2. Clique em um dos botões de login social
3. Autorize o acesso quando solicitado
4. Você será redirecionado de volta logado!

---

## 🐛 Problemas Comuns

### "redirect_uri_mismatch"
- Verifique se a URL de callback está **exatamente igual** no console do provedor
- Inclua a barra final `/`
- Use `http://localhost:8000` (não `127.0.0.1`)

### "invalid_client"
- Verifique se copiou corretamente o Client ID e Secret
- Execute `python manage.py setup_social_auth` novamente
- Reinicie o servidor

### "App not approved"
- Google: Adicione seu email em "Test users"
- Facebook: Mude para modo "Live" ou adicione usuários de teste

### Botões não aparecem
- Verifique se executou as migrações: `python manage.py migrate`
- Limpe o cache do navegador (Ctrl+Shift+Delete)

---

## 📝 Checklist

- [ ] Criar projeto no Google Cloud Console
- [ ] Configurar OAuth Consent Screen
- [ ] Criar credenciais OAuth
- [ ] Copiar Client ID e Secret
- [ ] Adicionar ao arquivo .env
- [ ] Executar `python manage.py setup_social_auth`
- [ ] Reiniciar o servidor
- [ ] Testar o login

---

## 💡 Dica

**Comece apenas com o Google!** É o mais fácil de configurar e testar.
Depois que funcionar, adicione Facebook e Microsoft se quiser.

---

## 🆘 Precisa de Ajuda?

1. Verifique a configuração: `python check_oauth_config.py`
2. Consulte o guia completo: `OAUTH_SETUP_INSTRUCTIONS.md`
3. Verifique os logs do servidor para erros específicos
