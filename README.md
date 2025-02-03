# Bem vindo ao Finanpe

Este projeto foi desenvolvido para fins de aprendizado do framework Django.
É uma aplicação destinada ao controle de finanças pessoais, tendo por base a minha planilha pessoal de controle.


## Instalação


Pré-requisitos:

* Python3 + pip instalados
* Ambiente virtual criado
* Django instalado - requirements.txt
* SQLite3 instalado - para usar outro banco, necessita configurar


Clone o projeto do github:

> git clone <projeto>

Crie as tabelas do banco de dados:

> python3 manage.py makemigrations

> python3 manage.py migrate

Crie um super usuário para acessar o ambiente admin:

> python3 manage.py createsuperuser

Rode o servidor:

> python3 manage.py runserver


## Carregar dados

Se desejar popular o banco de dados com algumas informações, use o comando:

``` ./manage.py loaddata db.json```



# Conteúdo

A seguir, o conteúdo, com uma breve descrição de seu propósito.


## Administração

Esta área foi desenvolvida utilizando o Django Admin, sem modificar o layout.


### Configuração

1. Categorias - para localizar onde estou gastando mais: Mercado, Casa, Pet, Entretenimento etc...
2. Centros de custo - identifica qual meio usado nas saídas: Cartão de crédito, Débito, Pix, etc...
3. Contas - similar a contas bancárias e também diferenciar cartões: Itau, Nubank, VISA Itaú, MASTER Nubank, etc...
4. Formas de pagamento - as formas utilizadas no mundo real: Pix, Débito em conta, Boleto, Cartão de Débito, Cartão de Crédito, Cheque, Dinheiro, etc...
5. Movimento entre contas: registro de entradas e de transferência de fundos entre as contas.
6. Fórmulas Centro de custo x Forma pagamento - define agrupamento das formas de pagamento por centro de custo, para visualização do resumo
7. Lançamentos: registro do consumo, para onde foi o dinheiro: compras, transferências, investimentos, etc...


## Site

Nesta área, alguns resumos de dados, com gráficos para complementar.


### Visualizações

1. Resumo por centro de custo: total de gastos e saldo no mês (entradas x saídas)
2. Resumo por categorias: percentual de gastos por categoria no mês
3. Resumo por tipo de operação: total a vista, parcelado e recorrente
4. Saldo de contas: posição final, ou o que sobrou em cada conta.


## Mais informações..

* Para usar a função "Criar próximo lançamento" no cadastro de Recorrentes (Adminitração), crie o primeiro lançamento em Transações e atualize a data da recorrência (Recorrentes) para o próximo período (mensal, semestral, anual, etc...).
* O saldo das contas deve ser atualizado manualmente.


## Últimas atualizações

```v.1.1.0```

1. Adição de função para "clonar" transações para o mês seguinte - em admin/Lançamentos
2. Adição de função para atualizar saldo de contas - em admin/Contas
3. Adição de função para gerar lançamentos recorrente para o próximo período - em admin/Recorrentes
4. Autenticação no site - precisa logar para ver qualquer coisa.