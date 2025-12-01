# Testes - Job Finder

## Visão Geral

O Job Finder utiliza o framework de testes do Django para garantir a qualidade do código e a funcionalidade correta da aplicação.

## Estrutura de Testes

Os testes estão localizados em `services/tests.py` e são organizados em classes de teste:

1. **ServiceModelTest** - Testes para o modelo Service
2. **UserProfileModelTest** - Testes para o modelo UserProfile
3. **CustomServiceModelTest** - Testes para o modelo CustomService
4. **ViewTests** - Testes para as views
5. **AuthenticationTests** - Testes para autenticação
6. **ChatModelTest** - Testes para o modelo Chat
7. **MessageModelTest** - Testes para o modelo Message

## Comandos de Gerenciamento

O projeto inclui comandos de gerenciamento para testes e desenvolvimento:

1. **generate_sample_orders** - Gera pedidos de exemplo para testes
2. **cleanup_chat_messages** - Limpa mensagens de chat antigas
3. **export_user_data** - Exporta dados do usuário para conformidade
4. **backup_database** - Cria backup do banco de dados
5. **import_sample_data** - Importa dados de exemplo
6. **reset_database** - Reseta o banco de dados (apenas desenvolvimento)
7. **populate_data** - Popula dados de exemplo (já existente)
8. **process_ai_analytics** - Processa análises de IA (já existente)

## Executando Testes

### Todos os testes

```bash
python manage.py test
```

### Testes específicos

```bash
# Executar testes de um app específico
python manage.py test services

# Executar testes de uma classe específica
python manage.py test services.tests.ServiceModelTest

# Executar um teste específico
python manage.py test services.tests.ServiceModelTest.test_service_creation
```

### Comandos de gerenciamento para testes

```bash
# Gerar dados de teste
python manage.py generate_sample_orders --number 5

# Importar dados de exemplo completos
python manage.py import_sample_data

# Limpar dados antigos (apenas desenvolvimento)
python manage.py import_sample_data --clear-existing

# Testar backup
python manage.py backup_database

# Testar exportação de dados
python manage.py export_user_data --user-id 1 --format json
```

### Com opções adicionais

```bash
# Verboso
python manage.py test -v 2

# Parar na primeira falha
python manage.py test --failfast

# Ver cobertura de testes
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Tipos de Testes

### Testes Unitários

Testam unidades individuais de código, como modelos e funções.

### Testes de Integração

Testam a interação entre diferentes componentes da aplicação.

### Testes de Views

Testam as views e garantem que as páginas sejam carregadas corretamente.

### Testes de API

Testam os endpoints da API.

## Cobertura de Testes

Atualmente, os testes cobrem:

- ✅ Modelos de dados
- ✅ Views principais
- ✅ Autenticação
- ✅ Funcionalidades de chat
- ✅ Criação de pedidos

## Adicionando Novos Testes

Para adicionar novos testes:

1. Abra `services/tests.py`
2. Crie uma nova classe de teste herdando de `TestCase`
3. Adicione métodos de teste seguindo o padrão `test_nome_do_teste`
4. Execute os testes para verificar se estão funcionando

### Exemplo de teste:

```python
class ExampleTest(TestCase):
    def setUp(self):
        # Configuração inicial para os testes
        pass
    
    def test_example_functionality(self):
        # Teste específico
        self.assertEqual(1 + 1, 2)
```

## Melhores Práticas

1. **Nomes descritivos** - Use nomes claros para os testes
2. **Testes independentes** - Cada teste deve funcionar independentemente
3. **Cobertura adequada** - Teste casos normais e casos de erro
4. **Dados de teste** - Use dados realistas mas controlados
5. **Assertivas claras** - Use assertivas que expressem claramente a intenção

## Relatórios de Teste

Para gerar relatórios detalhados:

```bash
# Instalar coverage
pip install coverage

# Executar testes com coverage
coverage run --source='.' manage.py test

# Gerar relatório
coverage report

# Gerar relatório HTML
coverage html
```

## Integração Contínua

O projeto pode ser configurado com sistemas de CI como GitHub Actions, GitLab CI, ou Jenkins para executar testes automaticamente em cada push.

## Troubleshooting

### Problemas comuns:

1. **Database locked**: Reinicie o servidor de teste
2. **Import errors**: Verifique se todas as dependências estão instaladas
3. **Permission denied**: Verifique permissões de arquivo

### Debugando testes:

```bash
# Executar com mais detalhes
python manage.py test -v 2

# Usar o modo de debug
python manage.py test --debug-mode
```