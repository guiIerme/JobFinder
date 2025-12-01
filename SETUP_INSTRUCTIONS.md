# Instruções de Setup - Projeto Home Services

## Requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## Passo a Passo para Configurar o Projeto

### 1. Clone o repositório
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd [NOME_DA_PASTA]
```

### 2. Crie um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Copie o arquivo `.env.example` para `.env` e configure as variáveis necessárias:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edite o arquivo `.env` com suas configurações.

### 5. Execute as migrações (se necessário)
```bash
python manage.py migrate
```

### 6. Inicie o servidor
```bash
python manage.py runserver
```

O projeto estará disponível em: http://127.0.0.1:8000/

## Banco de Dados
O banco de dados SQLite (`db.sqlite3`) está incluído no repositório com dados de exemplo.

## Arquivos de Mídia
Os arquivos de mídia (avatares, imagens) estão incluídos na pasta `media/`.

## Credenciais de Teste
[Adicione aqui usuários de teste se houver]

## Problemas Comuns

### Erro de dependências
Se houver erro ao instalar dependências, tente:
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Porta já em uso
Se a porta 8000 estiver em uso, use outra porta:
```bash
python manage.py runserver 8080
```

## Suporte
Para dúvidas ou problemas, abra uma issue no repositório.
