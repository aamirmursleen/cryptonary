import requests
import csv
import time
from bs4 import BeautifulSoup # For parsing HTML

# --- Configuration ---
SCRAPERAPI_KEY = "ff6afb85da6000279986afe44dd3e951" # Your ScraperAPI key
SCRAPERAPI_ENDPOINT = 'http://api.scraperapi.com'
OUTPUT_CSV_FILE = "scraped_seo_data_scraperapi.csv" # CSV will be updated/overwritten
REQUEST_DELAY = 1 # Delay between requests in seconds
REQUEST_TIMEOUT = 60 # Timeout for requests to ScraperAPI

# --- NEW Input Data (URLs from your latest table for cryptonary.com) ---
# Note: The header for Brazilian Portuguese is 'pt-BR' to match URL paths.
data_table = [
    ["Fiat Currency", "de", "fr", "es-ES", "it", "nl", "pl", "pt-BR", "ru", "th"],
    ["British Pound (GBP)", "https://cryptonary.com/de/currency-converter/btc/gbp/", "https://cryptonary.com/fr/currency-converter/btc/gbp/", "https://cryptonary.com/es-ES/currency-converter/btc/gbp/", "https://cryptonary.com/it/currency-converter/btc/gbp/", "https://cryptonary.com/nl/currency-converter/btc/gbp/", "https://cryptonary.com/pl/currency-converter/btc/gbp/", "https://cryptonary.com/pt-BR/currency-converter/btc/gbp/", "https://cryptonary.com/ru/currency-converter/btc/gbp/", "https://cryptonary.com/th/currency-converter/btc/gbp/"],
    ["Euro (EUR)", "https://cryptonary.com/de/currency-converter/btc/eur/", "https://cryptonary.com/fr/currency-converter/btc/eur/", "https://cryptonary.com/es-ES/currency-converter/btc/eur/", "https://cryptonary.com/it/currency-converter/btc/eur/", "https://cryptonary.com/nl/currency-converter/btc/eur/", "https://cryptonary.com/pl/currency-converter/btc/eur/", "https://cryptonary.com/pt-BR/currency-converter/btc/eur/", "https://cryptonary.com/ru/currency-converter/btc/eur/", "https://cryptonary.com/th/currency-converter/btc/eur/"],
    ["Japanese Yen (JPY)", "https://cryptonary.com/de/currency-converter/btc/jpy/", "https://cryptonary.com/fr/currency-converter/btc/jpy/", "https://cryptonary.com/es-ES/currency-converter/btc/jpy/", "https://cryptonary.com/it/currency-converter/btc/jpy/", "https://cryptonary.com/nl/currency-converter/btc/jpy/", "https://cryptonary.com/pl/currency-converter/btc/jpy/", "https://cryptonary.com/pt-BR/currency-converter/btc/jpy/", "https://cryptonary.com/ru/currency-converter/btc/jpy/", "https://cryptonary.com/th/currency-converter/btc/jpy/"],
    ["Swiss Franc (CHF)", "https://cryptonary.com/de/currency-converter/btc/chf/", "https://cryptonary.com/fr/currency-converter/btc/chf/", "https://cryptonary.com/es-ES/currency-converter/btc/chf/", "https://cryptonary.com/it/currency-converter/btc/chf/", "https://cryptonary.com/nl/currency-converter/btc/chf/", "https://cryptonary.com/pl/currency-converter/btc/chf/", "https://cryptonary.com/pt-BR/currency-converter/btc/chf/", "https://cryptonary.com/ru/currency-converter/btc/chf/", "https://cryptonary.com/th/currency-converter/btc/chf/"],
    ["Australian Dollar (AUD)", "https://cryptonary.com/de/currency-converter/btc/aud/", "https://cryptonary.com/fr/currency-converter/btc/aud/", "https://cryptonary.com/es-ES/currency-converter/btc/aud/", "https://cryptonary.com/it/currency-converter/btc/aud/", "https://cryptonary.com/nl/currency-converter/btc/aud/", "https://cryptonary.com/pl/currency-converter/btc/aud/", "https://cryptonary.com/pt-BR/currency-converter/btc/aud/", "https://cryptonary.com/ru/currency-converter/btc/aud/", "https://cryptonary.com/th/currency-converter/btc/aud/"],
    ["Canadian Dollar (CAD)", "https://cryptonary.com/de/currency-converter/btc/cad/", "https://cryptonary.com/fr/currency-converter/btc/cad/", "https://cryptonary.com/es-ES/currency-converter/btc/cad/", "https://cryptonary.com/it/currency-converter/btc/cad/", "https://cryptonary.com/nl/currency-converter/btc/cad/", "https://cryptonary.com/pl/currency-converter/btc/cad/", "https://cryptonary.com/pt-BR/currency-converter/btc/cad/", "https://cryptonary.com/ru/currency-converter/btc/cad/", "https://cryptonary.com/th/currency-converter/btc/cad/"],
    ["Indian Rupee (INR)", "https://cryptonary.com/de/currency-converter/btc/inr/", "https://cryptonary.com/fr/currency-converter/btc/inr/", "https://cryptonary.com/es-ES/currency-converter/btc/inr/", "https://cryptonary.com/it/currency-converter/btc/inr/", "https://cryptonary.com/nl/currency-converter/btc/inr/", "https://cryptonary.com/pl/currency-converter/btc/inr/", "https://cryptonary.com/pt-BR/currency-converter/btc/inr/", "https://cryptonary.com/ru/currency-converter/btc/inr/", "https://cryptonary.com/th/currency-converter/btc/inr/"],
    ["Chinese Yuan (CNY)", "https://cryptonary.com/de/currency-converter/btc/cny/", "https://cryptonary.com/fr/currency-converter/btc/cny/", "https://cryptonary.com/es-ES/currency-converter/btc/cny/", "https://cryptonary.com/it/currency-converter/btc/cny/", "https://cryptonary.com/nl/currency-converter/btc/cny/", "https://cryptonary.com/pl/currency-converter/btc/cny/", "https://cryptonary.com/pt-BR/currency-converter/btc/cny/", "https://cryptonary.com/ru/currency-converter/btc/cny/", "https://cryptonary.com/th/currency-converter/btc/cny/"],
    ["Pakistani Rupee (PKR)", "https://cryptonary.com/de/currency-converter/btc/pkr/", "https://cryptonary.com/fr/currency-converter/btc/pkr/", "https://cryptonary.com/es-ES/currency-converter/btc/pkr/", "https://cryptonary.com/it/currency-converter/btc/pkr/", "https://cryptonary.com/nl/currency-converter/btc/pkr/", "https://cryptonary.com/pl/currency-converter/btc/pkr/", "https://cryptonary.com/pt-BR/currency-converter/btc/pkr/", "https://cryptonary.com/ru/currency-converter/btc/pkr/", "https://cryptonary.com/th/currency-converter/btc/pkr/"],
    ["Singapore Dollar (SGD)", "https://cryptonary.com/de/currency-converter/btc/sgd/", "https://cryptonary.com/fr/currency-converter/btc/sgd/", "https://cryptonary.com/es-ES/currency-converter/btc/sgd/", "https://cryptonary.com/it/currency-converter/btc/sgd/", "https://cryptonary.com/nl/currency-converter/btc/sgd/", "https://cryptonary.com/pl/currency-converter/btc/sgd/", "https://cryptonary.com/pt-BR/currency-converter/btc/sgd/", "https://cryptonary.com/ru/currency-converter/btc/sgd/", "https://cryptonary.com/th/currency-converter/btc/sgd/"],
    ["South Korean Won (KRW)", "https://cryptonary.com/de/currency-converter/btc/krw/", "https://cryptonary.com/fr/currency-converter/btc/krw/", "https://cryptonary.com/es-ES/currency-converter/btc/krw/", "https://cryptonary.com/it/currency-converter/btc/krw/", "https://cryptonary.com/nl/currency-converter/btc/krw/", "https://cryptonary.com/pl/currency-converter/btc/krw/", "https://cryptonary.com/pt-BR/currency-converter/btc/krw/", "https://cryptonary.com/ru/currency-converter/btc/krw/", "https://cryptonary.com/th/currency-converter/btc/krw/"],
    ["Hong Kong Dollar (HKD)", "https://cryptonary.com/de/currency-converter/btc/hkd/", "https://cryptonary.com/fr/currency-converter/btc/hkd/", "https://cryptonary.com/es-ES/currency-converter/btc/hkd/", "https://cryptonary.com/it/currency-converter/btc/hkd/", "https://cryptonary.com/nl/currency-converter/btc/hkd/", "https://cryptonary.com/pl/currency-converter/btc/hkd/", "https://cryptonary.com/pt-BR/currency-converter/btc/hkd/", "https://cryptonary.com/ru/currency-converter/btc/hkd/", "https://cryptonary.com/th/currency-converter/btc/hkd/"],
    ["Brazilian Real (BRL)", "https://cryptonary.com/de/currency-converter/btc/brl/", "https://cryptonary.com/fr/currency-converter/btc/brl/", "https://cryptonary.com/es-ES/currency-converter/btc/brl/", "https://cryptonary.com/it/currency-converter/btc/brl/", "https://cryptonary.com/nl/currency-converter/btc/brl/", "https://cryptonary.com/pl/currency-converter/btc/brl/", "https://cryptonary.com/pt-BR/currency-converter/btc/brl/", "https://cryptonary.com/ru/currency-converter/btc/brl/", "https://cryptonary.com/th/currency-converter/btc/brl/"],
    ["Russian Ruble (RUB)", "https://cryptonary.com/de/currency-converter/btc/rub/", "https://cryptonary.com/fr/currency-converter/btc/rub/", "https://cryptonary.com/es-ES/currency-converter/btc/rub/", "https://cryptonary.com/it/currency-converter/btc/rub/", "https://cryptonary.com/nl/currency-converter/btc/rub/", "https://cryptonary.com/pl/currency-converter/btc/rub/", "https://cryptonary.com/pt-BR/currency-converter/btc/rub/", "https://cryptonary.com/ru/currency-converter/btc/rub/", "https://cryptonary.com/th/currency-converter/btc/rub/"],
    ["South African Rand (ZAR)", "https://cryptonary.com/de/currency-converter/btc/zar/", "https://cryptonary.com/fr/currency-converter/btc/zar/", "https://cryptonary.com/es-ES/currency-converter/btc/zar/", "https://cryptonary.com/it/currency-converter/btc/zar/", "https://cryptonary.com/nl/currency-converter/btc/zar/", "https://cryptonary.com/pl/currency-converter/btc/zar/", "https://cryptonary.com/pt-BR/currency-converter/btc/zar/", "https://cryptonary.com/ru/currency-converter/btc/zar/", "https://cryptonary.com/th/currency-converter/btc/zar/"],
    ["Turkish Lira (TRY)", "https://cryptonary.com/de/currency-converter/btc/try/", "https://cryptonary.com/fr/currency-converter/btc/try/", "https://cryptonary.com/es-ES/currency-converter/btc/try/", "https://cryptonary.com/it/currency-converter/btc/try/", "https://cryptonary.com/nl/currency-converter/btc/try/", "https://cryptonary.com/pl/currency-converter/btc/try/", "https://cryptonary.com/pt-BR/currency-converter/btc/try/", "https://cryptonary.com/ru/currency-converter/btc/try/", "https://cryptonary.com/th/currency-converter/btc/try/"],
    ["Mexican Peso (MXN)", "https://cryptonary.com/de/currency-converter/btc/mxn/", "https://cryptonary.com/fr/currency-converter/btc/mxn/", "https://cryptonary.com/es-ES/currency-converter/btc/mxn/", "https://cryptonary.com/it/currency-converter/btc/mxn/", "https://cryptonary.com/nl/currency-converter/btc/mxn/", "https://cryptonary.com/pl/currency-converter/btc/mxn/", "https://cryptonary.com/pt-BR/currency-converter/btc/mxn/", "https://cryptonary.com/ru/currency-converter/btc/mxn/", "https://cryptonary.com/th/currency-converter/btc/mxn/"],
    ["Indonesian Rupiah (IDR)", "https://cryptonary.com/de/currency-converter/btc/idr/", "https://cryptonary.com/fr/currency-converter/btc/idr/", "https://cryptonary.com/es-ES/currency-converter/btc/idr/", "https://cryptonary.com/it/currency-converter/btc/idr/", "https://cryptonary.com/nl/currency-converter/btc/idr/", "https://cryptonary.com/pl/currency-converter/btc/idr/", "https://cryptonary.com/pt-BR/currency-converter/btc/idr/", "https://cryptonary.com/ru/currency-converter/btc/idr/", "https://cryptonary.com/th/currency-converter/btc/idr/"],
    ["Malaysian Ringgit (MYR)", "https://cryptonary.com/de/currency-converter/btc/myr/", "https://cryptonary.com/fr/currency-converter/btc/myr/", "https://cryptonary.com/es-ES/currency-converter/btc/myr/", "https://cryptonary.com/it/currency-converter/btc/myr/", "https://cryptonary.com/nl/currency-converter/btc/myr/", "https://cryptonary.com/pl/currency-converter/btc/myr/", "https://cryptonary.com/pt-BR/currency-converter/btc/myr/", "https://cryptonary.com/ru/currency-converter/btc/myr/", "https://cryptonary.com/th/currency-converter/btc/myr/"],
]

def get_seo_data_with_scraperapi(target_url: str, api_key: str) -> tuple[str | None, str | None]:
    """
    Scrapes a URL using ScraperAPI to get its HTML content,
    then parses it with BeautifulSoup to extract title and meta description.
    """
    params = {'api_key': api_key, 'url': target_url}
    
    title_text = "N/A"
    meta_description_content = "N/A"

    try:
        print(f"Scraping with ScraperAPI: {target_url}")
        response = requests.get(SCRAPERAPI_ENDPOINT, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title_text = title_tag.string.strip()
        
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            meta_description_content = meta_tag.get('content').strip()
        else:
            og_meta_tag = soup.find('meta', property='og:description')
            if og_meta_tag and og_meta_tag.get('content'):
                meta_description_content = og_meta_tag.get('content').strip()
        
        return title_text, meta_description_content

    except requests.exceptions.RequestException as e:
        print(f"Error scraping {target_url} with ScraperAPI: {e}")
        return "Error: Request failed", "Error: Request failed"
    except Exception as e:
        print(f"An unexpected error occurred while processing {target_url} with ScraperAPI: {e}")
        return "Error: Unexpected", "Error: Unexpected"

def main():
    processed_data_table = []

    if data_table:
        processed_data_table.append(data_table[0])

    for row_index, current_data_row in enumerate(data_table[1:], start=1): 
        print(f"\nProcessing row {row_index}/{len(data_table)-1}: {current_data_row[0]}")
        processed_row = [current_data_row[0]]

        for url_index, url_from_cell in enumerate(current_data_row[1:], start=1): 
            if url_from_cell and url_from_cell.strip():
                full_url = url_from_cell.strip() # URLs are now full, just strip whitespace
                
                title, meta_description = get_seo_data_with_scraperapi(full_url, SCRAPERAPI_KEY)
                
                cell_content = f"{full_url}\nTitle: {title}\nMeta: {meta_description}"
                processed_row.append(cell_content)
                
                is_last_url_in_current_row = (url_index == (len(current_data_row) - 1))
                is_last_data_row = (row_index == (len(data_table) - 1))
                
                if not (is_last_data_row and is_last_url_in_current_row):
                     time.sleep(REQUEST_DELAY)
            else:
                processed_row.append("N/A") 
        
        processed_data_table.append(processed_row)

    try:
        with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(processed_data_table)
        print(f"\nSuccessfully wrote data to {OUTPUT_CSV_FILE}")
    except IOError as e:
        print(f"Error: Could not write to CSV file {OUTPUT_CSV_FILE}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"AN UNCAUGHT ERROR OCCURRED IN THE SCRIPT: {e}")
        import traceback
        traceback.print_exc()
