# 🔥 HEROKU - Deploy Completo do Zero

## 📋 PRÉ-REQUISITOS

### 1. **Criar conta no Heroku:**
- Acesse: https://heroku.com
- Clique "Sign up for free"
- Confirme seu email

### 2. **Instalar Heroku CLI:**
- Windows: https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli
- Baixe o instalador e execute

### 3. **Verificar instalação:**
```bash
heroku --version
git --version
```

---

## 🚀 PASSO A PASSO

### **PASSO 1: Login no Heroku**
```bash
heroku login
```
- Uma página web abrirá para login
- Faça login com sua conta

### **PASSO 2: Preparar o projeto**
```bash
# Navegar para pasta do projeto
cd caminho/para/seu/projeto

# Inicializar Git (se não tiver)
git init

# Adicionar todos os arquivos
git add .

# Fazer commit inicial
git commit -m "Preparando para deploy no Heroku"
```

### **PASSO 3: Criar app no Heroku**
```bash
# Criar app (substitua pelo nome que quiser)
heroku create meu-site-servicos

# Ou deixar o Heroku escolher um nome aleatório
heroku create
```

### **PASSO 4: Adicionar banco de dados**
```bash
# Adicionar PostgreSQL (gratuito)
heroku addons:create heroku-postgresql:mini
```

### **PASSO 5: Adicionar Redis (para chat)**
```bash
# Adicionar Redis (gratuito)
heroku addons:create heroku-redis:mini
```

### **PASSO 6: Configurar variáveis de ambiente**
```bash
# Configurar Django para produção
heroku config:set DEBUG=False
heroku config:set DJANGO_SETTINGS_MODULE=home_services.settings
```

### **PASSO 7: Fazer deploy**
```bash
# Enviar código para Heroku
git push heroku main

# Se der erro de branch, tente:
git push heroku master
```

### **PASSO 8: Configurar banco de dados**
```bash
# Executar migrações
heroku run python manage.py migrate

# Coletar arquivos estáticos
heroku run python manage.py collectstatic --noinput
```

### **PASSO 9: Criar usuário admin**
```bash
# Criar superusuário
heroku run python manage.py createsuperuser
```

### **PASSO 10: Abrir seu site**
```bash
# Abrir no navegador
heroku open

# Ou ver a URL
heroku info
```

---

## 🎉 PRONTO!

Seu site estará disponível em:
`https://nome-do-seu-app.herokuapp.com`

---

## 🔧 COMANDOS ÚTEIS

```bash
# Ver logs em tempo real
heroku logs --tail

# Ver status do app
heroku ps

# Ver variáveis de ambiente
heroku config

# Reiniciar app
heroku restart

# Executar comandos no servidor
heroku run python manage.py shell
```

---

## 🆘 PROBLEMAS COMUNS

**Erro de build:**
- Verifique se `requirements.txt` está correto
- Verifique se `Procfile` existe

**Erro 500:**
- Execute: `heroku logs --tail`
- Verifique as migrações: `heroku run python manage.py migrate`

**Arquivos estáticos não carregam:**
- Execute: `heroku run python manage.py collectstatic --noinput`

---

## 📱 PRÓXIMOS PASSOS

1. ✅ Teste todas as funcionalidades
2. 🔧 Configure domínio personalizado (opcional)
3. 📊 Monitore performance
4. 🔒 Configure SSL (automático no Heroku)
5. 🌍 Compartilhe seu site!