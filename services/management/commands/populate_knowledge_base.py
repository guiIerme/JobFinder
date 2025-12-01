"""
Management command to populate the knowledge base with initial data.

This command seeds the knowledge base with service information, FAQs,
navigation guides, policies, and troubleshooting content for the AI assistant.

Requirements: 2.2
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from services.chat_models import KnowledgeBaseEntry
from services.models import Service


class Command(BaseCommand):
    help = 'Populate knowledge base with initial service information, FAQs, and navigation guides'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing knowledge base entries before populating',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting knowledge base population...')
        
        if options['clear']:
            self.stdout.write('Clearing existing knowledge base entries...')
            KnowledgeBaseEntry.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing entries'))
        
        with transaction.atomic():
            # Populate service information
            self._populate_service_info()
            
            # Populate FAQs
            self._populate_faqs()
            
            # Populate navigation guides
            self._populate_navigation_guides()
            
            # Populate policies
            self._populate_policies()
            
            # Populate troubleshooting
            self._populate_troubleshooting()
        
        total_entries = KnowledgeBaseEntry.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated knowledge base with {total_entries} entries'
            )
        )

    def _populate_service_info(self):
        """Populate service-related information"""
        self.stdout.write('Populating service information...')
        
        service_entries = [
            {
                'title': 'Serviços de Limpeza',
                'content': '''Oferecemos diversos serviços de limpeza:
                
- Limpeza residencial completa
- Limpeza de apartamentos
- Limpeza pós-obra
- Limpeza de escritórios
- Limpeza profunda

Nossos profissionais são treinados e utilizam produtos de qualidade. 
O preço varia de acordo com o tamanho do ambiente e tipo de limpeza necessária.''',
                'keywords': ['limpeza', 'faxina', 'cleaning', 'limpar', 'casa', 'apartamento']
            },
            {
                'title': 'Serviços de Encanamento',
                'content': '''Serviços de encanamento disponíveis:
                
- Conserto de vazamentos
- Desentupimento de pias e ralos
- Instalação de torneiras e registros
- Troca de tubulações
- Manutenção preventiva

Atendimento rápido para emergências. Profissionais qualificados com ferramentas adequadas.''',
                'keywords': ['encanamento', 'encanador', 'vazamento', 'cano', 'torneira', 'pia', 'ralo']
            },
            {
                'title': 'Serviços Elétricos',
                'content': '''Serviços elétricos oferecidos:
                
- Instalação de tomadas e interruptores
- Troca de disjuntores
- Instalação de luminárias
- Manutenção elétrica preventiva
- Diagnóstico de problemas elétricos

Todos os profissionais são certificados e seguem normas de segurança.''',
                'keywords': ['eletrica', 'eletricista', 'tomada', 'interruptor', 'luz', 'energia', 'disjuntor']
            },
            {
                'title': 'Serviços de Pintura',
                'content': '''Serviços de pintura disponíveis:
                
- Pintura interna e externa
- Pintura de apartamentos e casas
- Pintura comercial
- Textura e grafiato
- Preparação de superfícies

Utilizamos tintas de qualidade e garantimos acabamento profissional.''',
                'keywords': ['pintura', 'pintor', 'tinta', 'parede', 'pintar']
            },
            {
                'title': 'Serviços de Marcenaria',
                'content': '''Serviços de marcenaria oferecidos:
                
- Montagem de móveis
- Conserto de móveis
- Móveis planejados
- Instalação de prateleiras
- Trabalhos em madeira personalizados

Profissionais experientes com ferramentas profissionais.''',
                'keywords': ['marcenaria', 'marceneiro', 'moveis', 'madeira', 'montagem']
            },
        ]
        
        for entry_data in service_entries:
            entry, created = KnowledgeBaseEntry.objects.get_or_create(
                title=entry_data['title'],
                category='service',
                defaults={
                    'content': entry_data['content'],
                    'keywords': entry_data['keywords'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created: {entry.title}')

    def _populate_faqs(self):
        """Populate frequently asked questions"""
        self.stdout.write('Populating FAQs...')
        
        faq_entries = [
            {
                'title': 'Como solicitar um serviço?',
                'content': '''Para solicitar um serviço:

1. Navegue até a página de serviços
2. Escolha o serviço desejado
3. Clique em "Solicitar Serviço"
4. Preencha os dados de contato e endereço
5. Escolha data e horário preferidos
6. Selecione a forma de pagamento
7. Confirme a solicitação

Você receberá uma confirmação por email e poderá acompanhar o status na página "Meus Pedidos".''',
                'keywords': ['solicitar', 'pedir', 'contratar', 'como', 'serviço', 'pedido']
            },
            {
                'title': 'Como acompanhar meus pedidos?',
                'content': '''Para acompanhar seus pedidos:

1. Faça login na sua conta
2. Acesse o menu "Meus Pedidos"
3. Visualize todos os seus pedidos e status
4. Clique em um pedido para ver detalhes

Você pode ver o histórico completo, status atual e informações do profissional designado.''',
                'keywords': ['pedidos', 'acompanhar', 'status', 'meus pedidos', 'historico']
            },
            {
                'title': 'Quais formas de pagamento são aceitas?',
                'content': '''Aceitamos as seguintes formas de pagamento:

- Dinheiro (pagamento direto ao profissional)
- Cartão de débito
- Cartão de crédito (parcelamento disponível)
- PIX
- Transferência bancária

A forma de pagamento é escolhida no momento da solicitação do serviço.''',
                'keywords': ['pagamento', 'pagar', 'dinheiro', 'cartao', 'pix', 'transferencia']
            },
            {
                'title': 'Como me tornar um prestador de serviços?',
                'content': '''Para se tornar um prestador:

1. Crie uma conta na plataforma
2. Acesse "Meu Perfil"
3. Altere o tipo de conta para "Profissional"
4. Preencha suas informações profissionais
5. Adicione suas especialidades e experiência
6. Aguarde a verificação da conta

Após aprovação, você poderá receber e aceitar solicitações de serviço.''',
                'keywords': ['prestador', 'profissional', 'trabalhar', 'cadastro', 'tornar']
            },
            {
                'title': 'Como funciona a avaliação dos profissionais?',
                'content': '''Sistema de avaliação:

- Após a conclusão do serviço, você pode avaliar o profissional
- Avaliações vão de 1 a 5 estrelas
- Você pode deixar comentários sobre o serviço
- As avaliações são públicas e ajudam outros usuários
- Profissionais bem avaliados têm destaque na plataforma

Avaliações honestas ajudam a manter a qualidade dos serviços.''',
                'keywords': ['avaliacao', 'avaliar', 'nota', 'estrelas', 'review', 'comentario']
            },
            {
                'title': 'Posso cancelar uma solicitação?',
                'content': '''Sim, você pode cancelar uma solicitação:

- Acesse "Meus Pedidos"
- Selecione o pedido que deseja cancelar
- Clique em "Cancelar Pedido"
- Informe o motivo do cancelamento

Importante: Cancelamentos após a confirmação do profissional podem estar sujeitos a taxas. 
Recomendamos cancelar com antecedência sempre que possível.''',
                'keywords': ['cancelar', 'cancelamento', 'desistir', 'remover']
            },
        ]
        
        for entry_data in faq_entries:
            entry, created = KnowledgeBaseEntry.objects.get_or_create(
                title=entry_data['title'],
                category='faq',
                defaults={
                    'content': entry_data['content'],
                    'keywords': entry_data['keywords'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created: {entry.title}')

    def _populate_navigation_guides(self):
        """Populate navigation guides"""
        self.stdout.write('Populating navigation guides...')
        
        navigation_entries = [
            {
                'title': 'Navegação - Página Inicial',
                'content': '''Na página inicial você encontra:

- Busca rápida de serviços
- Categorias de serviços disponíveis
- Profissionais em destaque
- Depoimentos de clientes
- Informações sobre a plataforma

Use o menu superior para acessar outras seções do site.''',
                'keywords': ['home', 'inicio', 'principal', 'pagina inicial']
            },
            {
                'title': 'Navegação - Serviços',
                'content': '''Na página de serviços:

- Visualize todos os serviços disponíveis
- Filtre por categoria
- Veja preços e descrições
- Compare profissionais
- Solicite serviços diretamente

Use os filtros para encontrar exatamente o que precisa.''',
                'keywords': ['servicos', 'services', 'lista', 'catalogo']
            },
            {
                'title': 'Navegação - Meu Perfil',
                'content': '''No seu perfil você pode:

- Atualizar informações pessoais
- Alterar foto de perfil
- Gerenciar endereços
- Configurar notificações
- Alterar senha
- Mudar tipo de conta (Cliente/Profissional)

Mantenha seus dados atualizados para melhor experiência.''',
                'keywords': ['perfil', 'profile', 'conta', 'dados', 'configuracoes']
            },
            {
                'title': 'Navegação - Meus Pedidos',
                'content': '''Na página de pedidos:

- Veja todos os seus pedidos
- Acompanhe o status em tempo real
- Acesse detalhes de cada pedido
- Entre em contato com profissionais
- Avalie serviços concluídos
- Cancele pedidos se necessário

Mantenha-se informado sobre seus serviços.''',
                'keywords': ['pedidos', 'orders', 'solicitacoes', 'meus pedidos']
            },
            {
                'title': 'Navegação - Dashboard do Prestador',
                'content': '''No dashboard do prestador:

- Visualize solicitações recebidas
- Aceite ou recuse pedidos
- Gerencie sua agenda
- Acompanhe ganhos
- Veja suas avaliações
- Atualize disponibilidade

Gerencie seu negócio de forma eficiente.''',
                'keywords': ['dashboard', 'prestador', 'profissional', 'painel']
            },
        ]
        
        for entry_data in navigation_entries:
            entry, created = KnowledgeBaseEntry.objects.get_or_create(
                title=entry_data['title'],
                category='navigation',
                defaults={
                    'content': entry_data['content'],
                    'keywords': entry_data['keywords'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created: {entry.title}')

    def _populate_policies(self):
        """Populate policy information"""
        self.stdout.write('Populating policies...')
        
        policy_entries = [
            {
                'title': 'Política de Privacidade',
                'content': '''Nossa política de privacidade:

- Seus dados pessoais são protegidos
- Não compartilhamos informações com terceiros sem consentimento
- Você pode solicitar exclusão de dados a qualquer momento
- Usamos cookies para melhorar a experiência
- Dados de pagamento são criptografados

Para mais detalhes, consulte nossa política completa de privacidade.''',
                'keywords': ['privacidade', 'dados', 'lgpd', 'protecao', 'informacoes']
            },
            {
                'title': 'Termos de Uso',
                'content': '''Termos de uso da plataforma:

- Usuários devem ter 18 anos ou mais
- Proibido uso indevido da plataforma
- Respeite outros usuários e profissionais
- Informações falsas podem resultar em banimento
- A plataforma não se responsabiliza por danos durante o serviço

Ao usar a plataforma, você concorda com estes termos.''',
                'keywords': ['termos', 'uso', 'regras', 'condicoes']
            },
            {
                'title': 'Política de Reembolso',
                'content': '''Política de reembolso:

- Reembolso disponível em caso de não prestação do serviço
- Solicitação deve ser feita em até 7 dias
- Análise caso a caso pela equipe
- Reembolso processado em até 10 dias úteis
- Disputas podem ser mediadas pela plataforma

Entre em contato com o suporte para solicitar reembolso.''',
                'keywords': ['reembolso', 'devolucao', 'estorno', 'dinheiro']
            },
        ]
        
        for entry_data in policy_entries:
            entry, created = KnowledgeBaseEntry.objects.get_or_create(
                title=entry_data['title'],
                category='policy',
                defaults={
                    'content': entry_data['content'],
                    'keywords': entry_data['keywords'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created: {entry.title}')

    def _populate_troubleshooting(self):
        """Populate troubleshooting guides"""
        self.stdout.write('Populating troubleshooting guides...')
        
        troubleshooting_entries = [
            {
                'title': 'Não consigo fazer login',
                'content': '''Se você não consegue fazer login:

1. Verifique se o email está correto
2. Tente redefinir sua senha
3. Limpe o cache do navegador
4. Tente usar outro navegador
5. Verifique sua conexão com a internet

Se o problema persistir, entre em contato com o suporte.''',
                'keywords': ['login', 'entrar', 'senha', 'acesso', 'problema']
            },
            {
                'title': 'Não recebi confirmação do pedido',
                'content': '''Se não recebeu confirmação:

1. Verifique sua caixa de spam
2. Confirme se o email está correto no perfil
3. Acesse "Meus Pedidos" para verificar o status
4. Aguarde alguns minutos (pode haver atraso)

Se ainda não recebeu, entre em contato com o suporte.''',
                'keywords': ['confirmacao', 'email', 'nao recebi', 'pedido']
            },
            {
                'title': 'Erro ao solicitar serviço',
                'content': '''Se encontrou erro ao solicitar:

1. Verifique se todos os campos estão preenchidos
2. Confirme se a data escolhida é válida
3. Tente atualizar a página
4. Limpe o cache do navegador
5. Tente novamente em alguns minutos

Se o erro persistir, anote a mensagem e contate o suporte.''',
                'keywords': ['erro', 'problema', 'solicitar', 'bug', 'nao funciona']
            },
            {
                'title': 'Página não carrega',
                'content': '''Se a página não carrega:

1. Verifique sua conexão com a internet
2. Atualize a página (F5)
3. Limpe o cache do navegador
4. Tente usar modo anônimo
5. Verifique se o site está em manutenção

Se o problema continuar, tente acessar mais tarde ou contate o suporte.''',
                'keywords': ['carrega', 'lento', 'nao abre', 'travado', 'loading']
            },
        ]
        
        for entry_data in troubleshooting_entries:
            entry, created = KnowledgeBaseEntry.objects.get_or_create(
                title=entry_data['title'],
                category='troubleshooting',
                defaults={
                    'content': entry_data['content'],
                    'keywords': entry_data['keywords'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created: {entry.title}')
