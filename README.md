# Extrator de Dicionário de Dados Web (MaxDB Extranet)

## Visão Geral do Projeto

Este projeto consiste em um script Python para realizar web scraping em uma extranet específica (Pixeon) e extrair o dicionário de dados de tabelas e colunas de um sistema, que é baseado em MaxDB. O objetivo é automatizar a coleta de metadados de banco de dados que estão disponíveis apenas via interface web, facilitando a documentação e análise.

## Funcionalidades

* **Autenticação:** Realiza login na extranet utilizando credenciais fornecidas de forma segura via variáveis de ambiente.
* **Navegação:** Percorre a lista de tabelas disponíveis na página do dicionário de dados.
* **Extração Detalhada:** Para cada tabela, acessa sua página de detalhes e extrai informações sobre as colunas, incluindo nome, tipo, tamanho máximo, permissão de nulos e descrição.
* **Exportação:** Consolida todos os dados extraídos em um arquivo CSV para fácil análise e uso.
* **Gerenciamento Seguro de Credenciais:** Utiliza arquivos `.env` para armazenar informações sensíveis (usuário, senha, URLs) fora do código-fonte versionado.

## Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **Requests:** Para realizar requisições HTTP (GET e POST) e gerenciar sessões.
* **BeautifulSoup4 (bs4):** Para parsing de HTML e extração de dados.
* **Pandas:** Para manipulação e exportação de dados para CSV.
* **python-dotenv:** Para carregar variáveis de ambiente de um arquivo `.env`.
* **time:** Para adicionar pausas entre as requisições, evitando sobrecarga no servidor e bloqueios.
* **Git:** Para controle de versão do código.

## Como Executar o Projeto

1.  **Pré-requisitos:**
    * Python 3.x instalado.
    * **Bibliotecas Python:** `pip install requests beautifulsoup4 pandas python-dotenv`

2.  **Configuração de Acesso:**
    * Crie um arquivo na raiz do projeto chamado `.env`.
    * Adicione as seguintes variáveis de ambiente, substituindo pelos seus dados reais de acesso e configurações:
        ```
        BASE_URL=
        USUARIO=
        SENHA=
        ARQUIVO_SAIDA_CSV=
        PAUSA_ENTRE_REQUISICOES=0.5
        ```
    * **Importante:** Certifique-se de que o arquivo `.env` está listado no seu `.gitignore` e **não seja enviado para o GitHub**.

3.  **Execução:**
    * Navegue até o diretório do projeto no terminal.
    * Execute o script: `python seu_script_scraping.py` (substitua `seu_script_scraping.py` pelo nome real do seu arquivo Python).
    * **Alternativa (Executável):** Se você gerou o executável com PyInstaller (na pasta `dist`), você pode executar o programa diretamente clicando duas vezes no arquivo `.exe` (no Windows) ou equivalente no seu sistema operacional, sem a necessidade de usar o terminal. Certifique-se de que o arquivo `.env` esteja na mesma pasta do executável.

## Contribuições

Sinta-se à vontade para explorar o código, sugerir melhorias ou relatar problemas.

## Autor

**Alan Amorim Porto**

* [Link para seu GitHub] (Se você tiver outros repositórios)
