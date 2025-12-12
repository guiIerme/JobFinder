# 🌟 RENDER - Deploy 100% Gratuito via GitHub

## 📋 **PASSO A PASSO COMPLETO:**

### **1. Preparar código para GitHub:**
```bash
# Inicializar Git
git init

# Adicionar arquivos
git add .

# Commit
git commit -m "Deploy para Render"

# Criar repositório no GitHub (substitua seu-usuario)
# Vá em github.com e crie um repositório novo
```

### **2. Enviar para GitHub:**
```bash
# Adicionar remote (substitua SEU-USUARIO e NOME-REPO)
git remote add origin https://github.com/SEU-USUARIO/NOME-REPO.git

# Enviar código
git branch -M main
git push -u origin main
```

### **3. Deploy no Render:**
1. **Acesse:** https://render.com
2. **Clique:** "New Web Service"
3. **Conecte:** seu repositório GitHub
4. **Configure:**
   - **Name:** jobfinder
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `daphne home_services.asgi:application --port $PORT --bind 0.0.0.0`
   - **Environment:** Python 3

### **4. Variáveis de ambiente:**
No Render, adicione:
- `DEBUG=False`
- `DJANGO_SETTINGS_MODULE=home_services.settings`

### **5. Pronto!**
Seu site estará em: `https://jobfinder.onrender.com`

---

## 🎯 **VANTAGENS DO RENDER:**
- ✅ **100% gratuito**
- ✅ **SSL automático**
- ✅ **Deploy automático via GitHub**
- ✅ **Sem cartão de crédito**
- ✅ **PostgreSQL gratuito**

---

## 🚀 **ALTERNATIVA RÁPIDA - RAILWAY:**
Se preferir algo mais simples:
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```