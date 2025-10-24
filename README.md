# OpenRouter Models JSON

Scraper automatizado para coletar informações sobre modelos de IA disponíveis no [OpenRouter](https://openrouter.ai/models).

## 📊 Dados Disponíveis

O arquivo `openrouter_models.json` contém informações atualizadas sobre **553+ modelos** de **113+ empresas** diferentes, incluindo:

- **Empresa/Provider** (ex: OpenAI, Anthropic, Google, Meta)
- **Nome do Modelo** (ex: GPT-4, Claude 3.5 Sonnet)
- **Model ID** (identificador único no formato `empresa/modelo-id`)
- **Preços** (input e output por 1M tokens)
- **Tamanho do Contexto** (em tokens)
- **URL** (link para detalhes no OpenRouter)

## 🚀 Como Usar os Dados

### Consumir o JSON diretamente via URL

Você pode consumir o JSON atualizado diretamente do GitHub em seus aplicativos:

```javascript
// JavaScript/TypeScript
const response = await fetch('https://raw.githubusercontent.com/rafaeljuniorvip/jsons_openrouter/main/openrouter_models.json');
const models = await response.json();
console.log(models);
```

```python
# Python
import requests

url = 'https://raw.githubusercontent.com/rafaeljuniorvip/jsons_openrouter/main/openrouter_models.json'
response = requests.get(url)
models = response.json()
print(f"Total de modelos: {len(models)}")
```

```bash
# Shell/curl
curl https://raw.githubusercontent.com/rafaeljuniorvip/jsons_openrouter/main/openrouter_models.json
```

### Estrutura dos Dados

Cada modelo tem a seguinte estrutura:

```json
{
  "Model Name & ID": "OpenAI: GPT-4o Miniopenai/gpt-4o-mini",
  "url": "/openai/gpt-4o-mini",
  "Input ($/1M tokens)": "$0,15",
  "Output ($/1M tokens)": "$0,60",
  "Context (tokens)": "128.000",
  "company": "OpenAI",
  "model_name": "GPT-4o Mini",
  "model_id": "openai/gpt-4o-mini"
}
```

### Exemplos de Filtros

```python
import requests

# Buscar todos os modelos
url = 'https://raw.githubusercontent.com/rafaeljuniorvip/jsons_openrouter/main/openrouter_models.json'
models = requests.get(url).json()

# Filtrar por empresa
openai_models = [m for m in models if m['company'] == 'OpenAI']
print(f"Modelos OpenAI: {len(openai_models)}")

# Filtrar modelos gratuitos
free_models = [m for m in models if m['Input ($/1M tokens)'] == '$0']
print(f"Modelos gratuitos: {len(free_models)}")

# Buscar por nome
gpt_models = [m for m in models if 'GPT' in m['model_name']]
```

## 🛠️ Executar o Scraper

### Requisitos

- Python 3.8+
- Google Chrome ou Chromium instalado

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/rafaeljuniorvip/jsons_openrouter.git
cd jsons_openrouter

# Instalar dependências
pip install -r requirements.txt
```

### Executar

```bash
python3 scraper.py
```

O script irá:
1. Acessar a página de modelos do OpenRouter
2. Aguardar o carregamento completo (JavaScript)
3. Extrair todos os dados da tabela
4. Gerar o arquivo `openrouter_models.json`

## 📈 Estatísticas

- **Total de Modelos**: 553
- **Total de Empresas**: 113
- **Top Providers**:
  - Qwen: 59 modelos
  - OpenAI: 57 modelos
  - Google: 42 modelos
  - Mistral: 33 modelos
  - Meta: 26 modelos

## 🔄 Atualização

Os dados são atualizados periodicamente executando o scraper. Para obter a versão mais recente, sempre use o link raw do GitHub.

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## ⚠️ Aviso

Este scraper é para fins educacionais e de pesquisa. Respeite os termos de serviço do OpenRouter ao usar os dados.
