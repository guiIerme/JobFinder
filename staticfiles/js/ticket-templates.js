// Ticket Templates Functionality
console.log('📋 Ticket Templates Script Loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Inicializando templates de tickets...');

    // Template definitions
    const templates = {
        bug: {
            subject: 'Reportar Bug: ',
            category: 'technical',
            description: `Descrição do Bug:
[Descreva o que aconteceu]

Passos para Reproduzir:
1. 
2. 
3. 

Comportamento Esperado:
[O que deveria acontecer]

Comportamento Atual:
[O que está acontecendo]

Informações Adicionais:
- Navegador: 
- Sistema Operacional: 
- Data/Hora: ${new Date().toLocaleString('pt-BR')}`
        },
        feature: {
            subject: 'Sugestão de Funcionalidade: ',
            category: 'feature_request',
            description: `Descrição da Funcionalidade:
[Descreva a funcionalidade sugerida]

Problema que Resolve:
[Qual problema esta funcionalidade resolveria]

Benefícios:
[Como isso melhoraria a experiência]

Exemplos de Uso:
[Como você usaria esta funcionalidade]`
        },
        account: {
            subject: 'Problema com Conta: ',
            category: 'account',
            description: `Descrição do Problema:
[Descreva o problema com sua conta]

O que você tentou fazer:
[Descreva as ações que você tentou]

Mensagens de Erro:
[Cole aqui qualquer mensagem de erro]

Quando começou:
[Quando você notou o problema pela primeira vez]`
        },
        payment: {
            subject: 'Problema de Pagamento: ',
            category: 'billing',
            description: `Descrição do Problema:
[Descreva o problema com o pagamento]

Método de Pagamento Utilizado:
[Cartão de crédito, PIX, boleto, etc.]

Valor da Transação:
R$ [valor]

Data e Hora da Tentativa:
${new Date().toLocaleString('pt-BR')}

Mensagem de Erro (se houver):
[Cole aqui a mensagem de erro]

Número do Pedido (se aplicável):
[Número do pedido]

Informações Adicionais:
[Qualquer outra informação relevante]`
        },
        service: {
            subject: 'Problema com Serviço: ',
            category: 'service_issue',
            description: `Descrição do Problema:
[Descreva o problema com o serviço]

Serviço Contratado:
[Nome do serviço ou profissional]

Número do Pedido:
[Se aplicável]

Data do Serviço:
[Quando o serviço foi/será realizado]

O que aconteceu:
[Descreva detalhadamente o problema]

Expectativa:
[O que você esperava que acontecesse]

Solução Desejada:
[Como você gostaria que o problema fosse resolvido]`
        },
        other: {
            subject: 'Dúvida/Questão: ',
            category: 'general',
            description: `Assunto:
[Sobre o que é sua dúvida ou questão]

Descrição Detalhada:
[Descreva sua dúvida ou questão em detalhes]

Contexto:
[Forneça contexto adicional se necessário]

O que você já tentou:
[Se aplicável, descreva o que você já tentou]

Informações Adicionais:
[Qualquer outra informação que possa ajudar]`
        }
    };

    // Get form elements
    const subjectInput = document.getElementById('subject');
    const categorySelect = document.getElementById('category');
    const descriptionInput = document.getElementById('description');

    // Setup template cards
    const templateCards = document.querySelectorAll('.template-card[data-template]');
    console.log('📋 Template cards encontrados:', templateCards.length);

    templateCards.forEach((card, index) => {
        const templateType = card.getAttribute('data-template');
        console.log(`✅ Card ${index + 1}: ${templateType}`);

        card.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            console.log('🎯 Template clicado:', templateType);

            const template = templates[templateType];
            if (!template) {
                console.error('❌ Template não encontrado:', templateType);
                return;
            }

            // Remove previous selections
            templateCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');

            // Fill form
            if (subjectInput) subjectInput.value = template.subject;
            if (categorySelect) categorySelect.value = template.category;
            if (descriptionInput) descriptionInput.value = template.description;

            console.log('✅ Formulário preenchido com sucesso!');

            // Scroll to form
            setTimeout(() => {
                const formCard = document.querySelector('.glass-card');
                if (formCard) {
                    formCard.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }

                // Focus on subject
                setTimeout(() => {
                    if (subjectInput) {
                        subjectInput.focus();
                        subjectInput.setSelectionRange(subjectInput.value.length, subjectInput.value.length);
                    }
                }, 500);
            }, 100);
        });
    });

    console.log('✅ Ticket Templates inicializado com sucesso!');
});