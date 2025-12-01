# Job Finder - Plataforma de Serviços Domésticos

## Descrição
Job Finder é uma plataforma web completa para conectar clientes a profissionais de serviços domésticos. O sistema permite que clientes busquem e contratem profissionais para diversos tipos de serviços, como reparos, montagem, encanamento, elétrica, limpeza e pintura.

## Visão Geral
O Job Finder é uma solução abrangente que aborda todas as necessidades de um marketplace de serviços domésticos, desde o cadastro de usuários até o processamento de pagamentos. A plataforma oferece uma experiência rica tanto para clientes que buscam serviços quanto para profissionais que os prestam, com recursos avançados de geolocalização, chat em tempo real, sistema de avaliações e muito mais.

## Funcionalidades Principais

## Funcionalidades Principais

### Para Clientes:
- **Busca Avançada**: Encontre profissionais por categoria, localização, preço e avaliação
- **Agendamento Inteligente**: Sistema de agendamento com múltiplas etapas e validação
- **Chat em Tempo Real**: Comunique-se diretamente com os profissionais
- **Histórico de Serviços**: Acompanhe todos os serviços solicitados
- **Sistema de Avaliações**: Avalie e veja avaliações de profissionais
- **Pagamentos Seguros**: Processamento de pagamentos integrado com Stripe
- **Geolocalização**: Visualize profissionais próximos em mapas interativos
- **Serviços Personalizados**: Solicite serviços fora das categorias padrão
- **Modo Escuro**: Interface moderna com suporte a modo escuro automático

### Para Profissionais:
- **Painel de Controle**: Dashboard completo para gerenciar serviços
- **Perfil Profissional**: Perfil personalizável com fotos e descrições detalhadas
- **Sistema de Avaliações**: Construa sua reputação com avaliações de clientes
- **Estatísticas de Desempenho**: Acompanhe seu desempenho com métricas detalhadas
- **Gerenciamento de Serviços**: Organize e acompanhe seus serviços agendados
- **Visualização de Mapas**: Veja onde seus clientes estão localizados
- **Modo Escuro**: Interface moderna com suporte a modo escuro automático

### Para Administradores:
- **Dashboard Analítico**: Métricas completas do sistema com gráficos interativos
- **Gestão de Usuários**: Administre clientes, profissionais e administradores
- **Monitoramento de Pedidos**: Acompanhe todos os pedidos em tempo real
- **Análise de Dados com IA**: Insights avançados com inteligência artificial
- **Sistema de Parceiros**: Gerencie sponsors e programas de parceria
- **Ferramentas de Manutenção**: Comandos de gerenciamento para manutenção do sistema
- **Modo Escuro**: Interface moderna com suporte a modo escuro automático

### Recursos de Acessibilidade:
- **Assistente de Acessibilidade**: Ferramenta integrada com opções de contraste, tamanho de fonte e Libras
- **Modo Escuro**: Suporte completo a modo escuro para reduzir fadiga visual
- **Compatibilidade com Leitores de Tela**: Marcações semânticas para leitores de tela
- **Navegação por Teclado**: Navegação completa usando apenas o teclado

## Tecnologias Utilizadas

### Backend:
- **Python 3.8+**: Linguagem de programação principal
- **Django 5.2.6**: Framework web robusto e escalável
- **SQLite**: Banco de dados de desenvolvimento
- **Stripe**: Processamento de pagamentos seguro
- **Pillow**: Processamento de imagens para avatares
- **Gunicorn**: Servidor WSGI para produção
- **psycopg2**: Conector para PostgreSQL (para produção)

### Frontend:
- **HTML5**: Estrutura semântica das páginas
- **CSS3**: Estilização com Bootstrap 5 e estilos personalizados
- **JavaScript**: Interatividade e funcionalidades dinâmicas
- **Font Awesome**: Ícones vetoriais e sociais
- **Google Maps JavaScript API**: Integração com mapas e geolocalização
- **Chart.js**: Visualização de dados em gráficos
- **Tailwind CSS**: Framework CSS para componentes React

### Inteligência Artificial:
- **WebsiteOptimizer**: Analisa comportamento do usuário e sugere melhorias
- **PersonalizationEngine**: Personaliza conteúdo com base no histórico
- **ContentGenerator**: Gera descrições de serviços e conteúdo automaticamente
- **Chat AI Assistant**: Assistente de chat com inteligência artificial
- **ML Analytics**: Análise preditiva e recomendações

## Instalação

### Pré-requisitos:
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Passos de instalação:

1. Clone o repositório:
```
git clone <url-do-repositorio>
cd Pi_mobile
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente (crie um arquivo `.env` baseado no `.env.example`):
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

6. Execute as migrações do banco de dados:
```bash
python manage.py migrate
```

7. Crie um superusuário (administrador):
```bash
python manage.py createsuperuser
```

8. (Opcional) Popule o banco de dados com dados de exemplo:
```bash
python manage.py import_sample_data
```

9. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

10. Acesse a aplicação em `http://127.0.0.1:8000/`

## Modo Escuro

O Job Finder inclui um modo escuro moderno que pode ser ativado de várias maneiras:

1. **Detecção Automática**: O sistema detecta automaticamente a preferência do sistema operacional
2. **Botão de Alternância**: Use o botão de lua/sol na barra de navegação
3. **Painel de Acessibilidade**: Acesse através do assistente de acessibilidade

### Recursos do Modo Escuro:
- Paleta de cores cuidadosamente selecionada para reduzir fadiga visual
- Contraste adequado para legibilidade
- Suporte completo a todos os componentes da interface
- Transições suaves entre modos claro e escuro
- Persistência da preferência do usuário

### Personalização:
Os desenvolvedores podem personalizar as cores do modo escuro modificando as variáveis CSS no arquivo `static/css/dark-mode.css`.

## Estrutura do Projeto

```
Pi_mobile/
├── home_services/          # Configurações do projeto Django
├── services/               # Aplicação principal
│   ├── migrations/         # Migrações do banco de dados
│   ├── templates/          # Templates HTML
│   ├── static/             # Arquivos estáticos (CSS, JS, imagens)
│   ├── models.py           # Modelos do banco de dados
│   ├── views.py            # Views/controllers
│   ├── urls.py             # Rotas da aplicação
│   ├── admin.py            # Configurações do admin Django
│   ├── tests.py            # Testes automatizados
│   ├── chat_views.py       # Views específicas para chat
│   ├── payment.py          # Processamento de pagamentos
│   ├── content_generator.py # Geração de conteúdo com IA
│   ├── personalization.py   # Motor de personalização
│   ├── ml_analytics.py     # Análise de dados com machine learning
│   ├── notifications.py    # Sistema de notificações
│   ├── health.py           # Monitoramento de saúde do sistema
│   ├── ai_context_processor.py # Processador de contexto para IA
│   ├── context_processors.py   # Processadores de contexto
│   ├── middleware.py       # Middleware personalizado
│   ├── ai_middleware.py    # Middleware para IA
│   ├── management/         # Comandos de gerenciamento personalizados
│   └── ...
├── templates/              # Templates globais
├── static/                 # Arquivos estáticos globais
├── docs/                   # Documentação do projeto
├── manage.py               # Script de gerenciamento do Django
├── requirements.txt        # Dependências do projeto
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
└── db.sqlite3              # Banco de dados SQLite
```

## Modelos de Dados Principais

### Service
Representa os serviços padrão oferecidos na plataforma.
- **Atributos**: nome, descrição, categoria, preço base, duração estimada
- **Relacionamentos**: Cada serviço pode ter múltiplos pedidos

### CustomService
Representa serviços personalizados oferecidos por profissionais.
- **Atributos**: nome, descrição, categoria, preço estimado, duração estimada
- **Relacionamentos**: Pertence a um profissional, pode ter múltiplos pedidos

### UserProfile
Extende o modelo de usuário padrão do Django com informações adicionais.
- **Atributos**: tipo de usuário, telefone, endereço, geolocalização, avatar
- **Relacionamentos**: Um para um com User, múltiplos serviços personalizados

### Order
Representa os pedidos/serviços solicitados pelos clientes.
- **Atributos**: status, data agendada, endereço, notas, preço total
- **Relacionamentos**: Pertence a um cliente e opcionalmente a um serviço/profissional

### Chat e Message
Sistema de mensagens entre clientes e profissionais.
- **Chat**: Conecta cliente e profissional, associado a um pedido
- **Message**: Mensagens individuais com suporte a texto, imagens e localização

### Review
Sistema de avaliações de clientes para profissionais.
- **Atributos**: classificação (1-5 estrelas), comentário, status verificado
- **Relacionamentos**: Um para um com Order, pertence a cliente e profissional

### PaymentMethod
Gerenciamento de métodos de pagamento dos usuários.
- **Atributos**: tipo de pagamento, últimos 4 dígitos, nome do titular
- **Relacionamentos**: Pertence a um usuário

### Sponsor
Sistema de patrocinadores e parceiros.
- **Atributos**: nome, descrição, logo, website, status ativo
- **Relacionamentos**: Pode ser associado a múltiplos usuários

## Testes

Para executar os testes automatizados:

```bash
python manage.py test
```

### Tipos de Testes
- **Testes Unitários**: Verificam funcionalidades individuais dos modelos e views
- **Testes de Integração**: Testam a interação entre diferentes componentes
- **Testes de API**: Validam endpoints e respostas da API
- **Testes de Interface**: Verificam a funcionalidade da interface do usuário

### Executando Testes Específicos
```
# Testar apenas a aplicação services
python manage.py test services

# Testar modelos específicos
python manage.py test services.tests.ModelTests

# Testar views específicas
python manage.py test services.tests.ViewTests
```

## Comandos de Gerenciamento

O projeto inclui vários comandos de gerenciamento úteis para desenvolvimento e manutenção:

### Popular dados de exemplo:
```bash
python manage.py populate_data
```

### Processar análises de IA:
```
python manage.py process_ai_analytics
```

### Gerar pedidos de exemplo:
```bash
python manage.py generate_sample_orders --number 20
```

### Limpar mensagens de chat antigas:
```
python manage.py cleanup_chat_messages --days 60
```

### Exportar dados do usuário (conformidade GDPR):
```bash
python manage.py export_user_data --user-id 1 --format json
```

### Backup do banco de dados:
```bash
python manage.py backup_database --include-media --compress
```

### Importar dados de exemplo:
```bash
python manage.py import_sample_data
```

### Resetar o banco de dados (apenas desenvolvimento):
```
python manage.py reset_database --no-input
```

### Inicializar sistema de avaliações:
```
python manage.py initialize_reviews
```

### Inicializar campos de geolocalização:
```
python manage.py initialize_geolocation
```

### Criar serviços de exemplo:
```
python manage.py create_sample_services
```

### Verificar saúde do sistema:
```
python manage.py health_check
```

## Funcionalidades de IA

### WebsiteOptimizer
Analisa o comportamento dos usuários e sugere melhorias para o site.
- **Coleta de Dados**: Monitora cliques, tempo de permanência e padrões de navegação
- **Análise Preditiva**: Identifica áreas de melhoria com base em dados históricos
- **Recomendações**: Sugere otimizações de UI/UX e conteúdo

### PersonalizationEngine
Personaliza o conteúdo com base no histórico de interações do usuário.
- **Perfil do Usuário**: Constrói perfis detalhados com preferências e comportamentos
- **Recomendações Inteligentes**: Sugere serviços e profissionais relevantes
- **Conteúdo Adaptativo**: Ajusta o conteúdo exibido com base no perfil

### ContentGenerator
Gera conteúdo automaticamente para descrições de serviços, depoimentos e FAQs.
- **Descrições de Serviços**: Cria descrições detalhadas e otimizadas
- **Depoimentos Gerados**: Produz depoimentos realistas para marketing
- **FAQ Automática**: Gera perguntas e respostas comuns
- **Respostas de Chat**: Fornece respostas inteligentes no sistema de chat

### Chat AI Assistant
Assistente de chat com inteligência artificial para suporte automatizado.
- **Processamento de Linguagem Natural**: Entende consultas dos usuários
- **Respostas Contextuais**: Fornece respostas relevantes com base no contexto
- **Aprendizado Contínuo**: Melhora as respostas com base em interações

## API Endpoints

### Públicos:
- `GET /` - Página inicial
- `GET /login/` - Página de login
- `GET /register/` - Página de registro
- `GET /search/` - Busca de profissionais
- `GET /map/` - Visualização de mapa com profissionais próximos
- `GET /about/` - Página sobre a empresa
- `GET /contact/` - Página de contato
- `GET /faq/` - Perguntas frequentes
- `GET /terms/` - Termos de serviço
- `GET /privacy/` - Política de privacidade

### Protegidos:
- `GET /profile/` - Perfil do usuário
- `GET /provider-dashboard/` - Painel do profissional
- `GET /admin-dashboard/` - Painel administrativo
- `POST /request-service/` - Solicitação de serviço
- `POST /submit-review/<order_id>/` - Submissão de avaliação
- `GET /professional-reviews/<professional_id>/` - Obtenção de avaliações de profissional
- `POST /api/update-location/` - Atualização de localização do usuário
- `GET /api/nearby-professionals/` - Obtenção de profissionais próximos
- `GET /chat/` - Lista de conversas
- `GET /chat/<chat_id>/` - Sala de chat específica
- `POST /chat/<order_id>/create/` - Criação de chat para um pedido
- `GET /service-history/` - Histórico de serviços
- `GET /payment/<order_id>/` - Processamento de pagamento
- `POST /save-payment-method/` - Salvamento de método de pagamento

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição
- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário
- Verifique se todos os testes passam antes de enviar
- Use mensagens de commit descritivas

### Reportando Issues
- Use o template de issues fornecido
- Inclua informações detalhadas sobre o problema
- Forneça passos para reproduzir o problema
- Inclua screenshots quando relevante

## Licença

Este projeto é privado e destinado apenas para fins educacionais.

## Contato

Para mais informações, entre em contato com a equipe de desenvolvimento.

# Admin Dashboard - React Component

## Overview
This project contains a visually improved React implementation of the Admin Dashboard using Tailwind CSS. The component maintains all existing functionality while significantly enhancing the visual design with improved spacing and breathing room according to the specified requirements.

## Features
- Modern, clean design with enhanced spacing and typography
- Fully responsive layout that works on all device sizes
- Interactive elements with smooth animations and transitions
- Consistent purple/white color scheme with softened gradients
- Comprehensive documentation explaining design decisions
- Improved spacing and breathing room throughout the interface

## Prerequisites
- Node.js (version 14 or higher)
- npm or yarn package manager

## Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd pi_mobile
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
   or
   ```bash
   yarn install
   ```

## Running the Project

To start the development server:

```bash
npm start
```

The application will be available at http://localhost:3000

## Usage Instructions

To use this component in your project:

1. Ensure you have React and Tailwind CSS installed
2. Copy the following files to your project:
   - `src/components/AdminDashboard.jsx`
   - `src/styles/AdminDashboard.css`
3. Import the component in your application:
   ```jsx
   import AdminDashboard from './components/AdminDashboard';
   ```
4. Include the component in your JSX:
   ```jsx
   <AdminDashboard />
   ```

## Key Spacing Improvements
- Enhanced container padding for better visual breathing room
- Increased card padding for more spacious content presentation
- Improved grid gaps between elements
- Better vertical spacing between sections
- Enhanced button sizing for improved touch targets
- Improved modal spacing for better content organization

## Dependencies
- React
- Tailwind CSS
- Font Awesome (for icons)
- Vite (for development server)

## Browser Support
This component works in all modern browsers that support:
- CSS Grid
- Flexbox
- ES6 JavaScript
- React

## Documentation
For detailed information about the visual improvements and implementation, see:
- `REACT_ADMIN_DASHBOARD.md` - Comprehensive documentation of design decisions
- `SPACING_IMPROVEMENTS_SUMMARY.md` - Detailed summary of spacing enhancements
- Code comments in `AdminDashboard.jsx` - Inline explanations of key features

## License
This component is provided as-is for educational and demonstration purposes.
