#!/bin/bash

# Deploy da Correção do Campo Username para o Render
# Este script automatiza o processo de deploy das correções

echo "🔧 Deploy da Correção do Campo Username no Mobile"
echo "================================================"

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto Django"
    exit 1
fi

# Verificar se os arquivos de correção existem
echo "📋 Verificando arquivos de correção..."

files_to_check=(
    "static/css/username-field-mobile-fix.css"
    "static/js/username-field-fix.js"
    "templates/registration/clean_register.html"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - OK"
    else
        echo "❌ $file - FALTANDO"
        exit 1
    fi
done

# Testar coleta de arquivos estáticos localmente
echo ""
echo "🗃️ Testando coleta de arquivos estáticos..."
python manage.py collectstatic --noinput --dry-run > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Coleta de arquivos estáticos - OK"
else
    echo "❌ Erro na coleta de arquivos estáticos"
    exit 1
fi

# Verificar status do Git
echo ""
echo "📝 Verificando status do Git..."
git status --porcelain > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Erro: Este não é um repositório Git"
    exit 1
fi

# Mostrar arquivos modificados
modified_files=$(git status --porcelain)
if [ -n "$modified_files" ]; then
    echo "📄 Arquivos modificados:"
    echo "$modified_files"
else
    echo "ℹ️ Nenhum arquivo modificado encontrado"
fi

# Perguntar se deve continuar com o commit
echo ""
read -p "🤔 Deseja fazer commit e push das alterações? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Adicionar todos os arquivos
    echo "📦 Adicionando arquivos ao Git..."
    git add .
    
    # Fazer commit
    echo "💾 Fazendo commit..."
    git commit -m "Fix: Correção do campo username não aparecer no mobile

- Adicionado CSS específico para forçar visibilidade do campo username
- JavaScript de monitoramento automático para garantir visibilidade
- Estilos inline no template com alta prioridade (!important)
- Arquivos de teste para verificação e debug
- Compatibilidade com todos os navegadores mobile
- Suporte a mudanças de orientação e redimensionamento
- Múltiplas estratégias de correção para máxima compatibilidade

Arquivos modificados:
- templates/registration/clean_register.html
- static/css/username-field-mobile-fix.css (novo)
- static/js/username-field-fix.js (novo)
- test_username_field_mobile.html (novo)
- test_simple_username.html (novo)"

    if [ $? -eq 0 ]; then
        echo "✅ Commit realizado com sucesso"
        
        # Fazer push
        echo "🚀 Fazendo push para o repositório..."
        git push origin main
        
        if [ $? -eq 0 ]; then
            echo "✅ Push realizado com sucesso"
            echo ""
            echo "🎉 Deploy iniciado!"
            echo "📱 O Render detectará as mudanças e iniciará o build automaticamente"
            echo ""
            echo "🔍 Para acompanhar o progresso:"
            echo "   1. Acesse o dashboard do Render"
            echo "   2. Vá na seção 'Logs' do seu serviço"
            echo "   3. Aguarde o build e deploy completarem"
            echo ""
            echo "🧪 Para testar após o deploy:"
            echo "   1. Acesse sua URL do Render + /register/"
            echo "   2. Teste no mobile ou DevTools mobile"
            echo "   3. Verifique se o campo 'Nome de Usuário' está visível"
            echo ""
            echo "🐛 Para debug (se necessário):"
            echo "   - Abra o console do navegador"
            echo "   - Execute: window.debugUsernameField()"
            echo "   - Ou acesse: sua-url/test_username_field_mobile.html"
        else
            echo "❌ Erro no push. Verifique sua conexão e permissões"
            exit 1
        fi
    else
        echo "❌ Erro no commit"
        exit 1
    fi
else
    echo "⏸️ Deploy cancelado pelo usuário"
    echo "ℹ️ Para fazer o deploy manualmente:"
    echo "   git add ."
    echo "   git commit -m 'Fix: Correção campo username mobile'"
    echo "   git push origin main"
fi

echo ""
echo "📋 Resumo das correções implementadas:"
echo "   ✅ CSS específico para mobile com !important"
echo "   ✅ JavaScript de monitoramento automático"
echo "   ✅ Estilos inline no template"
echo "   ✅ Arquivos de teste para debug"
echo "   ✅ Compatibilidade multi-navegador"
echo "   ✅ Suporte a orientação landscape/portrait"
echo ""
echo "🏁 Processo concluído!"