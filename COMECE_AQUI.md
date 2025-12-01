# 🚀 COMECE AQUI - Login Social em 5 Passos

## ⚠️ SITUAÇÃO ATUAL

Seu sistema está **100% implementado**, mas os botões de login social não funcionam porque você está usando credenciais de exemplo.

**Tempo para resolver:** 15 minutos (apenas Google)

---

## 📝 5 PASSOS PARA FAZER FUNCIONAR

### 1️⃣ Acesse o Google Cloud Console
🔗 https://console.cloud.google.com/

- Faça login com sua conta Google
- Clique em "Select a project" (topo da página)
- Clique em "NEW PROJECT"
- Nome: `Job Finder`
- Clique em "CREATE"

---

### 2️⃣ Configure o OAuth Consent Screen

- Menu lateral: "APIs & Services" > "OAuth consent screen"
- Selecione: **External**
- Clique em "CREATE"

**Preencha:**
- App name: `Job Finder`
- User support email: seu email
- Developer contact: seu email

Clique em "SAVE AND CONTINUE"

**Em Scopes:**
- Clique em "ADD OR REMOVE SCOPES"
- Marque: `.../auth/userinfo.email` e `.../auth/userinfo.profile`
- Clique em "UPDATE"
- Clique em "SAVE AND CONTINUE"

**Em Test users:**
- Clique em "ADD USERS"
- Adicione seu email
- Clique em "SAVE AND CONTINUE"

---

### 3️⃣ Crie as Credenciais OAuth

- Menu lateral: "Credentials"
- Clique em "CREATE CREDENTIALS"
- Selecione: "OAuth client ID"

**Configure:**
- Application type: **Web application**
- Name: `Job Finder Web`

**Em "Authorized redirect URIs":**
- Clique em "ADD URI"
- Cole: `http://localhost:8000/accounts/google/login/callback/`
- Clique em "CREATE"

**📋 IMPORTANTE:** Uma janela aparecerá com:
- **Client ID** (algo como: 123456789-abc.apps.googleusercontent.com)
- **Client Secret** (algo como: GOCSPX-abc123def456)

**COPIE AMBOS!** Você vai precisar deles no próximo passo.

---

### 4️⃣ Adicione as Credenciais no Projeto

**Abra o arquivo `.env` na raiz do projeto e edite:**

```env
# Substitua estas linhas:
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Por (cole suas credenciais reais):
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456
```

**Salve o arquivo!**

---

### 5️⃣ Atualize e Teste

**No terminal, execute:**

```bash
# Atualizar configuração no Django
python manage.py setup_social_auth

# Verificar se está tudo OK
python test_credentials.py

# Iniciar o servidor
python manage.py runserver
```

**Teste:**
1. Abra: http://localhost:8000/login/
2. Clique em "Entrar com Google"
3. Autorize o acesso
4. Pronto! Você estará logado! 🎉

---

## ✅ VERIFICAÇÃO

Após cada passo, você pode verificar:

```bash
# Ver se as credenciais são válidas
python test_credentials.py

# Ver a configuração completa
python check_oauth_config.py
```

---

## 🐛 PROBLEMAS COMUNS

### "redirect_uri_mismatch"
**Solução:** Verifique se você colocou exatamente:
```
http://localhost:8000/accounts/google/login/callback/
```
(com a barra `/` no final!)

### "invalid_client"
**Solução:** 
1. Verifique se copiou corretamente o Client ID e Secret
2. Execute: `python manage.py setup_social_auth`
3. Reinicie o servidor

### "Access blocked: This app's request is invalid"
**Solução:**
1. Volte ao Google Cloud Console
2. OAuth consent screen > ADD USERS
3. Adicione seu email como usuário de teste

### Botões não aparecem
**Solução:**
1. Limpe o cache do navegador (Ctrl+Shift+Delete)
2. Recarregue a página (Ctrl+F5)

---

## 📚 PRECISA DE MAIS AJUDA?

- **Guia rápido:** `GUIA_RAPIDO_CREDENCIAIS.md`
- **Guia completo:** `OAUTH_SETUP_INSTRUCTIONS.md`
- **Status atual:** `STATUS_OAUTH.md`

---

## 🎯 DEPOIS QUE FUNCIONAR

Quer adicionar Facebook e Microsoft também?
Consulte: `GUIA_RAPIDO_CREDENCIAIS.md`

---

## 💡 DICA IMPORTANTE

**Não commite o arquivo `.env` no Git!**

Ele já está no `.gitignore`, mas verifique antes de fazer commit.
As credenciais OAuth são secretas e não devem ser compartilhadas.

---

## 🎉 BOA SORTE!

Em 15 minutos você terá login com Google funcionando!

Se tiver dúvidas, consulte a documentação ou execute os scripts de verificação.
