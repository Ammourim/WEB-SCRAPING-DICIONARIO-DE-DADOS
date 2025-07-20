import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib3.exceptions import InsecureRequestWarning
import warnings
import os # Importado para acessar variáveis de ambiente
from dotenv import load_dotenv # Importado para carregar variáveis do .env

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Suprimir avisos de requisições inseguras
warnings.simplefilter('ignore', InsecureRequestWarning)

# --- Configurações de Acesso ao Site (agora lidas do .env) ---
BASE_URL = os.getenv("BASE_URL")
URL_PAGINA_INICIAL_DICIONARIO = BASE_URL + "dd.php"
URL_PARA_POST_LOGIN = BASE_URL + "login.php"
URL_PARA_GET_LOGIN_FORM = BASE_URL 

# !! ATENÇÃO: USUÁRIO E SENHA SÃO LIDOS DO .ENV !!
USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")

# Configurações de saída e pausa (também lidas do .env)
ARQUIVO_SAIDA_CSV = os.getenv("ARQUIVO_SAIDA_CSV", "dicionario_dados_smart_completo.csv") # Valor padrão caso não esteja no .env
PAUSA_ENTRE_REQUISICOES = float(os.getenv("PAUSA_ENTRE_REQUISICOES", 0.5)) # Converte para float, com valor padrão

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

todos_dados_colunas = []

print("Iniciando o processo de extração do dicionário de dados.\n")

session = requests.Session()
session.verify = False 
session.headers.update(HEADERS) 

# --- Passo 1: Realizar o Login ---
try:
    print(f"Tentando obter o formulário de login em: {URL_PARA_GET_LOGIN_FORM}...")
    response_get_login_form = session.get(URL_PARA_GET_LOGIN_FORM)
    response_get_login_form.raise_for_status()

    login_data = {
        'login': USUARIO,
        'senha': SENHA,
        'redirec': 'dd.php',
        'cb_ok': 'OK'
    }

    print(f"Enviando credenciais de login para: {URL_PARA_POST_LOGIN}...")
    response_login_post = session.post(URL_PARA_POST_LOGIN, data=login_data, allow_redirects=True)
    response_login_post.raise_for_status()

    if URL_PAGINA_INICIAL_DICIONARIO in response_login_post.url:
        print("Login bem-sucedido! Acessando o dicionário de dados...\n")
    else:
        print("Falha no login ou redirecionamento inesperado após POST.")
        print(f"URL final após tentativa de login: {response_login_post.url}")
        print("Conteúdo da página após POST (primeiras 500 chars para debug):")
        print(response_login_post.text[:500])
        exit()

except requests.exceptions.RequestException as e:
    print(f"Erro durante o processo de login: {e}")
    exit()
except Exception as e:
    print(f"Ocorreu um erro inesperado no login: {e}")
    exit()

# --- Passo 2: Obter a página inicial do dicionário (agora autenticado) ---
try:
    print(f"Acessando a página inicial do dicionário: {URL_PAGINA_INICIAL_DICIONARIO}")
    response_inicial_autenticada = session.get(URL_PAGINA_INICIAL_DICIONARIO)
    response_inicial_autenticada.raise_for_status()
    soup_inicial = BeautifulSoup(response_inicial_autenticada.text, 'html.parser')

    tabela_listagem_tabelas = soup_inicial.find('table', id='tab_tabelas')
    if not tabela_listagem_tabelas:
        print("Erro: Tabela de listagem de tabelas (id='tab_tabelas') não encontrada na página inicial do dicionário.")
        exit()

    links_tabelas_originais = tabela_listagem_tabelas.find_all('a', href=lambda href: href and 'detalhe.php?tabela=' in href)
    
    links_tabelas = links_tabelas_originais 

    print(f"Total de tabelas encontradas para processar: {len(links_tabelas)}\n")

except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar a página inicial do dicionário (após login): {e}")
    exit()
except Exception as e:
    print(f"Ocorreu um erro inesperado ao processar a página inicial após login: {e}")
    exit()

# --- Passo 3: Iterar sobre todas as tabelas e extrair os detalhes das colunas ---
for i, link_tag in enumerate(links_tabelas):
    nome_tabela_curto = link_tag.text.strip()
    caminho_detalhe = link_tag['href']
    url_detalhe_tabela = requests.compat.urljoin(BASE_URL, caminho_detalhe)

    print(f"[{i+1}/{len(links_tabelas)}] Processando detalhes da tabela: '{nome_tabela_curto}' ({url_detalhe_tabela})...")

    time.sleep(PAUSA_ENTRE_REQUISICOES)

    try:
        response_detalhe = session.get(url_detalhe_tabela)
        response_detalhe.raise_for_status()
        soup_detalhe = BeautifulSoup(response_detalhe.text, 'html.parser')

        titulo_pagina_tag = soup_detalhe.find('h3')
        if titulo_pagina_tag:
            nome_completo_tabela = titulo_pagina_tag.text.strip()
        else:
            nome_completo_tabela = nome_tabela_curto

        tabela_colunas = None
        header_row_in_tbody = None

        for table_element in soup_detalhe.find_all('table', class_='table'):
            if table_element.find('tbody'):
                for tr_in_tbody in table_element.find('tbody').find_all('tr'):
                    ths = tr_in_tbody.find_all('th')
                    if ths:
                        headers_text = [th.text.strip() for th in ths]
                        expected_headers = ["Coluna", "Permite Null", "Tipo", "Tamanho Maximo", "Descricao"]
                        if all(h in headers_text for h in expected_headers):
                            header_row_in_tbody = tr_in_tbody
                            tabela_colunas = table_element
                            break
                if tabela_colunas:
                    break

        if tabela_colunas and header_row_in_tbody:
            headers_colunas = [th.text.strip() for th in header_row_in_tbody.find_all('th')]

            try:
                coluna_idx = headers_colunas.index("Coluna")
                permite_nulo_idx = headers_colunas.index("Permite Null")
                tipo_idx = headers_colunas.index("Tipo")
                tamanho_maximo_idx = headers_colunas.index("Tamanho Maximo")
                descricao_idx = headers_colunas.index("Descricao")
            except ValueError as ve:
                print(f"   Erro: Cabeçalho de coluna não encontrado conforme esperado para '{nome_tabela_curto}'. Erro: {ve}. Pulando esta tabela.")
                continue

            all_data_rows = tabela_colunas.find('tbody').find_all('tr')
            start_index_for_data = all_data_rows.index(header_row_in_tbody) + 1

            for linha_dado in all_data_rows[start_index_for_data:]:
                celulas = linha_dado.find_all('td')
                
                if len(celulas) == len(headers_colunas):
                    col_name_raw = celulas[coluna_idx].text.strip()
                    coluna_nome_limpo = col_name_raw.replace("PK", "").replace("FK", "").replace("img", "").replace("Img", "").strip()

                    dados_coluna = {
                        "Tabela_Nome": nome_completo_tabela,
                        "Tabela_Sigla": nome_tabela_curto,
                        "Coluna_Nome": coluna_nome_limpo,
                        "Permite_Nulo": celulas[permite_nulo_idx].text.strip(),
                        "Tipo": celulas[tipo_idx].text.strip(),
                        "Tamanho_Maximo": celulas[tamanho_maximo_idx].text.strip(),
                        "Descricao": celulas[descricao_idx].text.strip()
                    }
                    todos_dados_colunas.append(dados_coluna)
        else:
            print(f"   Aviso: Tabela de detalhes das colunas (classe 'table' com cabeçalhos esperados) não encontrada para '{nome_tabela_curto}'. Pulando.")

    except requests.exceptions.RequestException as e:
        print(f"   Erro de rede ou HTTP ao acessar a página de detalhe da tabela '{nome_tabela_curto}': {e}")
    except Exception as e:
        print(f"   Ocorreu um erro inesperado ao processar a tabela '{nome_tabela_curto}': {e}")

# --- Passo 4: Organizar e exportar os dados para CSV ---
if todos_dados_colunas:
    df = pd.DataFrame(todos_dados_colunas)
    df = df[['Tabela_Sigla', 'Tabela_Nome', 'Coluna_Nome', 'Tipo', 'Tamanho_Maximo', 'Permite_Nulo', 'Descricao']]
    
    df.to_csv(ARQUIVO_SAIDA_CSV, index=False, encoding='utf-8-sig')
    print(f"\nExtração concluída! Dados salvos em: '{ARQUIVO_SAIDA_CSV}'")
else:
    print("\nNenhum dado de colunas foi extraído. Verifique as credenciais de login, URLs, seletores ou a estrutura HTML do site.")
