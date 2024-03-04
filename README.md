# Currency Converter API

API de conversão de moedas feita com Python, MongoDB e FastAPI

## Como rodar o projeto?

Clonar o repositório:
```shell
git clone https://github.com/lucasnunesg/currency-converter.git
```
Navegar para a pasta do projeto:
```shell
cd currency-converter
```

Executar o docker-compose:
```
docker-compose up --build
```

É necessário incluir dois arquivos no diretório raiz do projeto: `.env`, com as variáveis de ambiente para inicialização do PostgreSQL e `.env.dev` com a DATABASE_URL do banco de dados para ser lido pelo arquivo de configurações do pydantic:

Arquivo `.env`:
```shell
POSTGRES_DB=app_db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
```

Arquivo `.env.dev`:
```shell
DATABASE_URL="postgresql://app_user:app_password@postgres:5432/app_db"
```


## Versões

### V1
Implementação com o MongoDB (NoSQL) e pymongo.

### V2
Implementação com PostgreSQL e SQLAlchemy.


## Como acessar a documentação?

Basta acessar o endpoint `/docs`: http://0.0.0.0:8000/docs. A documentação informa todos os endpoints bem como seus parâmetros e tipos de retorno.

## Como são feitas as conversões?

As conversões são atualizadas a cada 30 segundos utilizando a [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas).
Existem moedas previamente adicionadas mas o usuário tem a opção de adicionar novas moedas sejam elas existentes no mundo real (cujo valor será atualizado automaticamente) ou não (cujo valor deverá ser informado e, caso houver necessidade, atualizado posteriormente pelo próprio usuário).

Todas as conversões são feitas tendo o dólar americano (USD) como moeda de lastro, e, havendo necessidade de cadastrar uma moeda fictícia, o usuário precisa informar a taxa de conversão dela para USD.


## Como rodar os testes?

*OBS*: necessário que o contêiner esteja em execução

### Teste de de estresse

Estando na pasta do projeto (`currency-converter/`), basta executar o seguinte comando:
```shell
python3 app/tests/load_test.py
```

### Demais testes

Executar o seguinte comando:
```shell
docker-compose exec web pytest -v
```

## Melhorias futuras
1) Implementação de uma ODM (como por exemplo [ODMantic](https://art049.github.io/odmantic/) ou [MongoEngine](http://mongoengine.org/)) e bibliotecas auxiliares (como por exemplo [marshmallow](https://marshmallow.readthedocs.io/en/stable/)) para otimizar processos de serialização e comunicação direta com a API sem necessidade de manipular detalhes dos documentos.
2) Testes de integração para `v2`.