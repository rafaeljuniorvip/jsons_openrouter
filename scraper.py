#!/usr/bin/env python3
"""
Scraper para coletar modelos da página OpenRouter usando Selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import re


def extract_company_and_model(full_name, url=None):
    """
    Extrai a empresa e o nome do modelo do nome completo.
    Se a URL for fornecida, usa ela para extrair o ID correto.

    Args:
        full_name: Nome completo do modelo (ex: "Qwen: Qwen3 VL 32B Instructqwen/qwen3-vl-32b-instruct")
        url: URL do modelo (ex: "/qwen/qwen3-vl-32b-instruct")

    Returns:
        tuple: (company, model_name, model_id)
    """
    if not full_name:
        return None, None, None

    # Se temos a URL, usar ela para extrair o ID (mais confiável)
    if url:
        # URL está no formato "/empresa/modelo-id" ou "/empresa-parte/modelo-id"
        url = url.strip('/')
        model_id = url

        # Extrair empresa do ID
        company_from_id = url.split('/')[0]
        company_formatted = company_from_id.replace('-', ' ').title()

        # Remover o ID do full_name para obter o nome do modelo
        # O ID pode aparecer de diferentes formas no nome
        # Verificar se há "Empresa: " no início do nome
        company_match = re.match(r'^([^:]+):\s*(.+)$', full_name)

        if company_match:
            # Tem o padrão "Empresa: Nome do Modelo..."
            company = company_match.group(1).strip()
            rest = company_match.group(2).strip()

            # Remover a parte do ID que pode estar colada no final
            # Procurar pela parte que corresponde ao ID
            # Exemplo: "Qwen3 VL 32B Instructqwen/qwen3..." -> queremos "Qwen3 VL 32B Instruct"
            # O ID "qwen/..." pode estar no final
            if model_id in rest:
                model_name = rest.replace(model_id, '').strip()
            else:
                # Tentar remover só a parte após o último espaço se ela se parece com o ID
                parts = rest.rsplit(' ', 1)
                if len(parts) == 2 and model_id.split('/')[0] in parts[1].lower():
                    model_name = parts[0]
                else:
                    # Como último recurso, apenas pegar tudo antes da primeira minúscula+/
                    id_pattern = f"{model_id.split('/')[0]}/"
                    idx = rest.lower().find(id_pattern)
                    if idx > 0:
                        model_name = rest[:idx].strip()
                    else:
                        model_name = rest
        else:
            # Sem "Empresa:", tentar extrair o nome
            company = company_formatted
            # Remover o ID do nome
            if model_id in full_name:
                model_name = full_name.replace(model_id, '').strip()
            else:
                # Tentar por partes
                id_pattern = f"{model_id.split('/')[0]}/"
                idx = full_name.lower().find(id_pattern)
                if idx > 0:
                    model_name = full_name[:idx].strip()
                else:
                    model_name = full_name

        return company, model_name, model_id

    # Fallback: sem URL, tentar extrair do nome (menos confiável)
    model_id_match = re.search(r'([a-z][\w\-]*/[\w\-\.]+)$', full_name)
    if not model_id_match:
        return None, full_name, None

    model_id = model_id_match.group(1)
    name_without_id = full_name[:model_id_match.start()].strip()

    company_match = re.match(r'^([^:]+):\s*(.+)$', name_without_id)
    if company_match:
        company = company_match.group(1).strip()
        model_name = company_match.group(2).strip()
    else:
        company_from_id = model_id.split('/')[0]
        company = company_from_id.replace('-', ' ').title()
        model_name = name_without_id.strip()

    return company, model_name, model_id


def scrape_openrouter_models():
    """Faz scraping da página de modelos do OpenRouter"""
    url = "https://openrouter.ai/models?fmt=table"

    print(f"Acessando {url}...")

    # Configurar Chrome headless
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        # Aguardar a tabela carregar
        print("Aguardando a página carregar...")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Aguardar um pouco mais para garantir que os dados foram carregados
        time.sleep(3)

        # Scroll para carregar todo o conteúdo (se houver lazy loading)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Obter o HTML da página
        page_source = driver.page_source

        # Parse com BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        models = []

        # Procurar pela tabela de modelos
        table = soup.find('table')

        if not table:
            print("Tabela não encontrada. Salvando HTML para análise...")
            with open('page_debug_selenium.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            return models

        # Extrair headers da tabela
        headers_row = table.find('thead')
        if headers_row:
            headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
        else:
            headers = []

        print(f"Headers encontrados: {headers}")

        # Extrair dados das linhas
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"Total de linhas encontradas: {len(rows)}")

            for row in rows:
                cells = row.find_all('td')
                if cells:
                    model_data = {}
                    full_model_name = None

                    # Mapear células para headers se disponíveis
                    for i, cell in enumerate(cells):
                        header = headers[i] if i < len(headers) else f'column_{i}'
                        # Pegar o texto e também atributos úteis
                        text = cell.get_text(strip=True)
                        model_data[header] = text

                        # Se for a coluna do modelo (primeira coluna)
                        if i == 0:
                            full_model_name = text
                            link = cell.find('a')
                            if link and link.get('href'):
                                model_data['url'] = link.get('href')

                    # Extrair empresa e nome do modelo
                    if full_model_name:
                        url = model_data.get('url')
                        company, model_name, model_id = extract_company_and_model(full_model_name, url)
                        model_data['company'] = company
                        model_data['model_name'] = model_name
                        model_data['model_id'] = model_id

                    models.append(model_data)

        return models

    finally:
        driver.quit()


def save_to_json(data, filename='openrouter_models.json'):
    """Salva os dados em arquivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Dados salvos em {filename}")


def main():
    try:
        models = scrape_openrouter_models()

        if models:
            print(f"\n{len(models)} modelos coletados!")
            print("\nPrimeiro modelo de exemplo:")
            print(json.dumps(models[0], indent=2, ensure_ascii=False))

            save_to_json(models)
        else:
            print("Nenhum modelo encontrado. Verifique o arquivo page_debug.html")

    except Exception as e:
        print(f"Erro durante o scraping: {e}")
        raise


if __name__ == "__main__":
    main()
