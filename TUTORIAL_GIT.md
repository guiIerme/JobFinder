# 📚 Tutorial Git - JobFinder Project

Guia completo para usar Git no CMD/PowerShell para gerenciar o projeto JobFinder.

---

## 📋 Índice

1. [Configuração Inicial](#configuração-inicial)
2. [Comandos Básicos do Dia a Dia](#comandos-básicos-do-dia-a-dia)
3. [Enviando Alterações para o GitHub](#enviando-alterações-para-o-github)
4. [Baixando Alterações do GitHub](#baixando-alterações-do-github)
5. [Visualizando Histórico e Alterações](#visualizando-histórico-e-alterações)
6. [Trabalhando em Equipe](#trabalhando-em-equipe)
7. [Resolvendo Problemas Comuns](#resolvendo-problemas-comuns)
8. [Comandos de Emergência](#comandos-de-emergência)

---

## 🚀 Configuração Inicial

### Primeira vez usando Git? Configure seu nome e email:

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

**Exemplo:**
```bash
git config --global user.name "Guilherme Beserra"
git config --global user.email "guilherme@senac.com"
```

### Verificar configuração:
```bash
git config --list
```

---

## 💻 Comandos Básicos do Dia a Dia

### 1. Abrir terminal na pasta do projeto

**Opção 1 (Mais Fácil):**
- Abra a pasta do projeto no Explorador de Arquivos
- Na barra de endereço, digite `cmd` e pressione Enter

**Opção 2:**
```bash
cd "C:\Users\guilherme54222106\OneDrive - SENAC DF\projeto_integrador"
```

### 2. Verificar status do projeto
```bash
git status
```
**O que mostra:**
- Arquivos modificados (em vermelho)
- Arquivos prontos para commit (em verde)
- Branch atual

### 3. Ver o que mudou nos arquivos
```bash
git diff
```
**Ver mudanças de um arquivo específico:**
```bash
git diff templates/services/about.html
```

---

## 📤 Enviando Alterações para o GitHub

### Fluxo completo (use sempre nesta ordem):

#### Passo 1: Ver o que mudou
```bash
git status
```

#### Passo 2: Adicionar arquivos modificados
```bash
# Adicionar TODOS os arquivos
git add .

# OU adicionar arquivo específico
git add templates/services/about.html
```

#### Passo 3: Fazer commit (salvar localmente)
```bash
git commit -m "Descrição clara do que foi feito"
```

**Exemplos de boas mensagens:**
```bash
git commit -m "Atualizar fotos da equipe para formato JPEG"
git commit -m "Corrigir bug no formulário de login"
git commit -m "Adicionar página de contato"
git commit -m "Melhorar responsividade do menu"
```

#### Passo 4: Enviar para o GitHub
```bash
git push
```

### ⚡ Atalho rápido (3 comandos em sequência):
```bash
git add . & git commit -m "Sua mensagem aqui" & git push
```

---

## 📥 Baixando Alterações do GitHub

### Quando outra pessoa fez mudanças no GitHub:

```bash
git pull
```

**O que faz:** Baixa e mescla as alterações do GitHub com seu código local.

### Antes de começar a trabalhar (boa prática):
```bash
# 1. Ver status atual
git status

# 2. Baixar atualizações
git pull

# 3. Agora pode trabalhar tranquilo!
```

---

## 🔍 Visualizando Histórico e Alterações

### Ver histórico de commits
```bash
# Histórico completo
git log

# Histórico resumido (1 linha por commit)
git log --oneline

# Últimos 5 commits
git log -5

# Histórico com gráfico
git log --graph --oneline --all
```

**Dica:** Pressione `q` para sair da visualização do log.

### Ver detalhes do último commit
```bash
git show
```

### Ver quem modificou cada linha de um arquivo
```bash
git blame templates/services/about.html
```

### Ver diferença entre local e GitHub
```bash
git diff origin/main
```

### Ver apenas nomes dos arquivos modificados
```bash
git diff --name-only
```

### Ver estatísticas de mudanças
```bash
git diff --stat
```

---

## 👥 Trabalhando em Equipe

### Fluxo recomendado para trabalho em equipe:

#### Antes de começar a trabalhar:
```bash
# 1. Baixar últimas alterações
git pull

# 2. Ver status
git status

# 3. Trabalhar no código...
```

#### Depois de terminar:
```bash
# 1. Ver o que mudou
git status

# 2. Adicionar alterações
git add .

# 3. Fazer commit
git commit -m "Descrição do que fez"

# 4. Baixar possíveis mudanças dos colegas
git pull

# 5. Enviar suas mudanças
git push
```

### Se houver conflito ao fazer pull:

Git vai avisar quais arquivos têm conflito. Abra o arquivo e procure por:

```
<<<<<<< HEAD
Seu código
=======
Código do colega
>>>>>>> branch-name
```

**Resolva manualmente:**
1. Escolha qual código manter (ou combine os dois)
2. Remova as marcações `<<<<<<<`, `=======`, `>>>>>>>`
3. Salve o arquivo
4. Faça commit:

```bash
git add .
git commit -m "Resolver conflito em [nome do arquivo]"
git push
```

---

## 🆘 Resolvendo Problemas Comuns

### Problema 1: "fatal: not a git repository"
**Solução:** Você não está na pasta do projeto.
```bash
cd "C:\Users\guilherme54222106\OneDrive - SENAC DF\projeto_integrador"
```

### Problema 2: Esqueci de fazer pull antes de trabalhar
```bash
# 1. Salvar suas mudanças temporariamente
git stash

# 2. Baixar mudanças do GitHub
git pull

# 3. Recuperar suas mudanças
git stash pop
```

### Problema 3: Quero desfazer mudanças em um arquivo
```bash
# Desfazer mudanças NÃO commitadas
git checkout -- templates/services/about.html

# Desfazer TODAS as mudanças não commitadas
git checkout -- .
```

### Problema 4: Fiz commit errado, quero voltar
```bash
# Voltar 1 commit (mantém as mudanças nos arquivos)
git reset --soft HEAD~1

# Voltar 1 commit (DESCARTA as mudanças)
git reset --hard HEAD~1
```

### Problema 5: Senha do GitHub não funciona
Use um **Personal Access Token**:

1. Acesse: https://github.com/settings/tokens
2. "Generate new token" → "Generate new token (classic)"
3. Nome: "JobFinder Project"
4. Marque: **repo** (todas as opções)
5. "Generate token"
6. Copie o token (começa com `ghp_`)
7. Use como senha no git push

### Problema 6: Quero ver o que tem no GitHub sem baixar
```bash
git fetch
git diff origin/main
```

---

## 🚨 Comandos de Emergência

### Cancelar git add (antes do commit)
```bash
git reset
```

### Desfazer TODAS as mudanças locais (CUIDADO!)
```bash
git reset --hard HEAD
```

### Baixar versão do GitHub e sobrescrever tudo local (CUIDADO!)
```bash
git fetch origin
git reset --hard origin/main
```

### Ver histórico de TODOS os comandos git que você executou
```bash
git reflog
```

### Recuperar commit "perdido"
```bash
# 1. Ver histórico completo
git reflog

# 2. Encontrar o código do commit (ex: a1b2c3d)
# 3. Voltar para ele
git reset --hard a1b2c3d
```

---

## 📊 Comandos Úteis para Análise

### Ver quantas linhas cada pessoa adicionou/removeu
```bash
git log --shortstat --author="Guilherme"
```

### Ver commits de hoje
```bash
git log --since="today"
```

### Ver commits da última semana
```bash
git log --since="1 week ago"
```

### Ver arquivos que mais mudaram
```bash
git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -10
```

### Ver tamanho do repositório
```bash
git count-objects -vH
```

---

## 🎯 Workflow Recomendado para Este Projeto

### Rotina Diária:

```bash
# 1. MANHÃ - Antes de começar
cd "C:\Users\guilherme54222106\OneDrive - SENAC DF\projeto_integrador"
git pull
git status

# 2. DURANTE O DIA - Trabalhe normalmente no código

# 3. TARDE/NOITE - Ao terminar
git status                                    # Ver o que mudou
git diff                                      # Ver detalhes das mudanças
git add .                                     # Adicionar tudo
git commit -m "Descrição do que fez hoje"    # Salvar
git pull                                      # Baixar mudanças dos colegas
git push                                      # Enviar suas mudanças
```

### Commits Frequentes (Recomendado):

Faça commits pequenos e frequentes, não espere o dia todo:

```bash
# Exemplo: Terminou uma funcionalidade
git add .
git commit -m "Adicionar validação no formulário de cadastro"
git push

# Exemplo: Corrigiu um bug
git add .
git commit -m "Corrigir erro de validação de email"
git push

# Exemplo: Melhorou o CSS
git add .
git commit -m "Melhorar responsividade da navbar"
git push
```

---

## 🔗 Links Úteis

- **Repositório do Projeto:** https://github.com/guiIerme/JobFinder
- **GitHub Desktop (Interface Gráfica):** https://desktop.github.com/
- **Git Documentation:** https://git-scm.com/doc
- **GitHub Guides:** https://guides.github.com/

---

## 📝 Dicas Finais

1. **Sempre faça `git pull` antes de começar a trabalhar**
2. **Faça commits pequenos e frequentes**
3. **Use mensagens de commit claras e descritivas**
4. **Não commite arquivos sensíveis (.env, senhas)**
5. **Use `git status` constantemente para saber o que está acontecendo**
6. **Quando em dúvida, pergunte antes de usar comandos com `--hard`**
7. **Mantenha o `.gitignore` atualizado**

---

## 🎓 Comandos Mais Usados (Resumo)

```bash
git status              # Ver status
git pull                # Baixar do GitHub
git add .               # Adicionar tudo
git commit -m "msg"     # Salvar com mensagem
git push                # Enviar para GitHub
git log --oneline       # Ver histórico
git diff                # Ver mudanças
```

---

**Criado para o Projeto Integrador SENAC - JobFinder**  
**Equipe:** Guilherme, Felipe, Anna, Isabelle, Mariana, Isaque  
**Última atualização:** Dezembro 2024
