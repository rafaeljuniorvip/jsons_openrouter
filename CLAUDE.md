# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based web scraper that collects AI model information from OpenRouter's model catalog page. The scraper uses Selenium with headless Chrome to handle JavaScript-rendered content and BeautifulSoup for HTML parsing. The output is a JSON file containing structured data about 553+ AI models from 113+ providers.

## Architecture

### Core Components

**scraper.py** - Main scraping logic with four key functions:
- `extract_company_and_model()` - Complex parsing logic to extract company name, model name, and model ID from compound strings. Uses URL paths as the authoritative source for model IDs (format: `/company/model-id`). Handles edge cases where model IDs may be concatenated with model names without spaces.
- `scrape_openrouter_models(url, driver)` - Selenium-based scraper that accepts a URL and optional shared driver instance:
  1. Launches headless Chrome with specific user agent and window size (if driver not provided)
  2. Navigates to the specified OpenRouter models URL
  3. Waits for table rendering (20s timeout + 3s buffer)
  4. Scrolls to trigger lazy loading
  5. Parses table HTML with BeautifulSoup
  6. Maps table cells to headers dynamically
  7. Extracts model data including URLs from `<a>` tags
- `scrape_all_models_with_capabilities()` - Orchestrates multiple scraping passes to collect capability data:
  1. Scrapes base URL to get all 554+ models
  2. Creates dictionary indexed by `model_id` for efficient lookups
  3. Initializes capability fields: `input_modalities` (array), `output_modalities` (array), `supports_tools` (boolean)
  4. Scrapes 6 filtered URLs to identify model capabilities
  5. Marks each model with its supported capabilities
  6. Returns unified list with all capability data
- `save_to_json()` - Writes output with UTF-8 encoding and pretty printing

**openrouter_models.json** - Generated output file with structure:
```json
{
  "Model Name & ID": "Company: Model Namecompany/model-id",
  "url": "/company/model-id",
  "Input ($/1M tokens)": "$X.XX",
  "Output ($/1M tokens)": "$X.XX",
  "Context (tokens)": "XXX.XXX",
  "company": "Company",
  "model_name": "Model Name",
  "model_id": "company/model-id",
  "input_modalities": ["text", "image", "audio", "file"],
  "output_modalities": ["text", "image"],
  "supports_tools": true
}
```

Capability fields:
- `input_modalities`: Array of supported input types (text, image, audio, file)
- `output_modalities`: Array of supported output types (text, image)
- `supports_tools`: Boolean indicating function calling support

### Data Flow

1. **Initial scrape** - Collects all models from base URL
   - Selenium loads `https://openrouter.ai/models?fmt=table`
   - WebDriverWait ensures table exists before parsing
   - Scroll triggers any lazy-loaded content
   - BeautifulSoup extracts table headers and rows
   - Each row's first cell contains model name + ID; extract URL from `<a>` tag
   - `extract_company_and_model()` parses compound strings using URL as source of truth
   - Creates dictionary indexed by `model_id` with capability fields initialized

2. **Capability detection** - Scrapes 6 filtered URLs to mark capabilities:
   - `input_modalities=image` - Models accepting image input
   - `input_modalities=audio` - Models accepting audio input
   - `input_modalities=file` - Models accepting file input
   - `input_modalities=text` - Models accepting text input
   - `output_modalities=image` - Models generating image output
   - `supported_parameters=tools` - Models supporting function calling

3. **Merging** - For each filtered result:
   - Looks up model in dictionary by `model_id`
   - Appends capability to appropriate array or sets boolean flag
   - Reuses same Selenium driver across all requests for efficiency

4. **Output** - Saves unified JSON with all models and their capabilities

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

Requirements:
- Python 3.8+
- Google Chrome or Chromium installed (required for Selenium WebDriver)

### Run Scraper
```bash
python3 scraper.py
```

This will:
- Connect to OpenRouter's models page
- Wait for JavaScript to render the table
- Extract all model data
- Save to `openrouter_models.json`

### Debug
If scraping fails, a debug HTML file is saved at `page_debug_selenium.html` for inspection.

## Key Implementation Details

### String Parsing Logic
The `extract_company_and_model()` function handles multiple patterns:
- `"Company: Model Namecompany/model-id"` - Most common format
- URL path is the authoritative model ID source
- Regex patterns handle cases where ID is concatenated without spaces
- Falls back to multiple parsing strategies if primary method fails

### Selenium Configuration
Critical Chrome options for reliable scraping:
- `--headless` - Run without GUI
- `--no-sandbox` - Required in some environments
- `--disable-dev-shm-usage` - Prevents memory issues
- `--window-size=1920,1080` - Ensures responsive layout
- Custom user agent - Mimics real browser

### Wait Strategy
Layered waiting ensures complete page load:
1. WebDriverWait for table element (20s max)
2. Additional 3s sleep for JavaScript execution
3. Scroll + 2s sleep for lazy loading
