# 🌟 RENDER - Deploy AGORA (Railway não funcionou)

## 📋 **PASSO 1: GitHub**

### Se não tem repositório GitHub:
1. Vá em: https://github.com
2. Clique "New repository"
3. Nome: `projeto-integrador`
4. Clique "Create repository"

### Comandos:
```bash
# Adicionar remote GitHub (substitua SEU-USUARIO)
git remote add origin https://github.com/SEU-USUARIO/projeto-integrador.git

# Enviar código
git push -u origin main
```

## 📋 **PASSO 2: Render Deploy**

1. **Acesse:** https://render.com
2. **Clique:** "Get Started for Free"
3. **Faça login** com GitHub
4. **Clique:** "New +" → "Web Service"
5. **Conecte** seu repositório `projeto-integrador`

## 📋 **PASSO 3: Configurações**

### Configurações básicas:
- **Name:** `jobfinder`
- **Region:** `Oregon (US West)`
- **Branch:** `main`
- **Runtime:** `Python 3`

### Comandos:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python manage.py runserver 0.0.0.0:$PORT`

### Variáveis de ambiente:
- `DEBUG` = `False`
- `DJANGO_SETTINGS_MODULE` = `home_services.settings`

## 📋 **PASSO 4: Deploy**

1. **Clique:** "Create Web Service"
2. **Aguarde** o build (5-10 minutos)
3. **Seu site estará em:** `https://jobfinder.onrender.com`

## 🎉 **VANTAGENS DO RENDER:**

- ✅ **100% gratuito**
- ✅ **SSL automático**
- ✅ **Mais estável que Railway**
- ✅ **Deploy automático via GitHub**
- ✅ **PostgreSQL gratuito**
- ✅ **Sem problemas de porta**

## 🆘 **SE DER PROBLEMA:**

1. Verifique os logs no Render
2. Certifique-se que o código está no GitHub
3. Verifique as variáveis de ambiente

**O Render é MUITO mais confiável que o Railway!**