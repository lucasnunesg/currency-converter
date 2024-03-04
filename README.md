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

## Como acessar a documentação?

Basta acessar o endpoint `/docs`: http://0.0.0.0:8000/docs
A documentação informa todos os endpoints bem como seus parâmetros e tipos de retorno.

## Como são feitas as conversões?

As conversões são atualizadas a cada 30 segundos utilizando a [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas).
Existem moedas previamente adicionadas mas o usuário tem a opção de adicionar novas moedas sejam elas existentes no mundo real (cujo valor será atualizado automaticamente) ou não (cujo valor deverá ser informado e, caso houver necessidade, atualizado posteriormente pelo próprio usuário).

Todas as conversões são feitas tendo o dólar americano (USD) como moeda de lastro, e, havendo necessidade de cadastrar uma moeda fictícia, o usuário precisa informar a taxa de conversão dela para USD.


