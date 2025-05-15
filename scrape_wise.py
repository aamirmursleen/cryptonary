#working great

import requests
import csv
import time
from bs4 import BeautifulSoup # For parsing HTML

# --- Configuration ---
SCRAPERAPI_KEY = "ff6afb85da6000279986afe44dd3e951" # Your NEW ScraperAPI key
SCRAPERAPI_ENDPOINT = 'http://api.scraperapi.com'
OUTPUT_CSV_FILE = "scraped_seo_data_scraperapi.csv" # CSV will be updated/overwritten
REQUEST_DELAY = 1 # Delay between requests in seconds
REQUEST_TIMEOUT = 60 # Timeout for requests to ScraperAPI

# --- NEW Input Data (URLs from your table) ---
data_table = [
    ["Fiat Currency", "de", "fr", "es", "it", "nl", "pl", "br", "ru", "th"],
    ["British Pound", "wise.com/de/currency-converter/usd-to-gbp-rate", "wise.com/fr/currency-converter/usd-to-gbp-rate", "wise.com/es/currency-converter/usd-to-gbp-rate", "wise.com/it/currency-converter/usd-to-gbp-rate", "wise.com/nl/currency-converter/usd-to-gbp-rate", "wise.com/pl/currency-converter/usd-to-gbp-rate", "wise.com/br/currency-converter/usd-to-gbp-rate", "wise.com/ru/currency-converter/usd-to-gbp-rate", "wise.com/th/currency-converter/usd-to-gbp-rate"],
    ["Euro", "wise.com/de/currency-converter/usd-to-eur-rate", "wise.com/fr/currency-converter/usd-to-eur-rate", "wise.com/es/currency-converter/usd-to-eur-rate", "wise.com/it/currency-converter/usd-to-eur-rate", "wise.com/nl/currency-converter/usd-to-eur-rate", "wise.com/pl/currency-converter/usd-to-eur-rate", "wise.com/br/currency-converter/usd-to-eur-rate", "wise.com/ru/currency-converter/usd-to-eur-rate", "wise.com/th/currency-converter/usd-to-eur-rate"],
    ["Japanese Yen", "wise.com/de/currency-converter/usd-to-jpy-rate", "wise.com/fr/currency-converter/usd-to-jpy-rate", "wise.com/es/currency-converter/usd-to-jpy-rate", "wise.com/it/currency-converter/usd-to-jpy-rate", "wise.com/nl/currency-converter/usd-to-jpy-rate", "wise.com/pl/currency-converter/usd-to-jpy-rate", "wise.com/br/currency-converter/usd-to-jpy-rate", "wise.com/ru/currency-converter/usd-to-jpy-rate", "wise.com/th/currency-converter/usd-to-jpy-rate"],
    ["Swiss Franc", "wise.com/de/currency-converter/usd-to-chf-rate", "wise.com/fr/currency-converter/usd-to-chf-rate", "wise.com/es/currency-converter/usd-to-chf-rate", "wise.com/it/currency-converter/usd-to-chf-rate", "wise.com/nl/currency-converter/usd-to-chf-rate", "wise.com/pl/currency-converter/usd-to-chf-rate", "wise.com/br/currency-converter/usd-to-chf-rate", "wise.com/ru/currency-converter/usd-to-chf-rate", "wise.com/th/currency-converter/usd-to-chf-rate"],
    ["Australian Dollar", "wise.com/de/currency-converter/usd-to-aud-rate", "wise.com/fr/currency-converter/usd-to-aud-rate", "wise.com/es/currency-converter/usd-to-aud-rate", "wise.com/it/currency-converter/usd-to-aud-rate", "wise.com/nl/currency-converter/usd-to-aud-rate", "wise.com/pl/currency-converter/usd-to-aud-rate", "wise.com/br/currency-converter/usd-to-aud-rate", "wise.com/ru/currency-converter/usd-to-aud-rate", "wise.com/th/currency-converter/usd-to-aud-rate"],
    ["Canadian Dollar", "wise.com/de/currency-converter/usd-to-cad-rate", "wise.com/fr/currency-converter/usd-to-cad-rate", "wise.com/es/currency-converter/usd-to-cad-rate", "wise.com/it/currency-converter/usd-to-cad-rate", "wise.com/nl/currency-converter/usd-to-cad-rate", "wise.com/pl/currency-converter/usd-to-cad-rate", "wise.com/br/currency-converter/usd-to-cad-rate", "wise.com/ru/currency-converter/usd-to-cad-rate", "wise.com/th/currency-converter/usd-to-cad-rate"],
    ["Indian Rupee", "wise.com/de/currency-converter/usd-to-inr-rate", "wise.com/fr/currency-converter/usd-to-inr-rate", "wise.com/es/currency-converter/usd-to-inr-rate", "wise.com/it/currency-converter/usd-to-inr-rate", "wise.com/nl/currency-converter/usd-to-inr-rate", "wise.com/pl/currency-converter/usd-to-inr-rate", "wise.com/br/currency-converter/usd-to-inr-rate", "wise.com/ru/currency-converter/usd-to-inr-rate", "wise.com/th/currency-converter/usd-to-inr-rate"],
    ["Chinese Yuan", "wise.com/de/currency-converter/usd-to-cny-rate", "wise.com/fr/currency-converter/usd-to-cny-rate", "wise.com/es/currency-converter/usd-to-cny-rate", "wise.com/it/currency-converter/usd-to-cny-rate", "wise.com/nl/currency-converter/usd-to-cny-rate", "wise.com/pl/currency-converter/usd-to-cny-rate", "wise.com/br/currency-converter/usd-to-cny-rate", "wise.com/ru/currency-converter/usd-to-cny-rate", "wise.com/th/currency-converter/usd-to-cny-rate"],
    ["Pakistani Rupee", "wise.com/de/currency-converter/usd-to-pkr-rate", "wise.com/fr/currency-converter/usd-to-pkr-rate", "wise.com/es/currency-converter/usd-to-pkr-rate", "wise.com/it/currency-converter/usd-to-pkr-rate", "wise.com/nl/currency-converter/usd-to-pkr-rate", "wise.com/pl/currency-converter/usd-to-pkr-rate", "wise.com/br/currency-converter/usd-to-pkr-rate", "wise.com/ru/currency-converter/usd-to-pkr-rate", "wise.com/th/currency-converter/usd-to-pkr-rate"],
    ["Singapore Dollar", "wise.com/de/currency-converter/usd-to-sgd-rate", "wise.com/fr/currency-converter/usd-to-sgd-rate", "wise.com/es/currency-converter/usd-to-sgd-rate", "wise.com/it/currency-converter/usd-to-sgd-rate", "wise.com/nl/currency-converter/usd-to-sgd-rate", "wise.com/pl/currency-converter/usd-to-sgd-rate", "wise.com/br/currency-converter/usd-to-sgd-rate", "wise.com/ru/currency-converter/usd-to-sgd-rate", "wise.com/th/currency-converter/usd-to-sgd-rate"],
    ["South Korean Won", "wise.com/de/currency-converter/usd-to-krw-rate", "wise.com/fr/currency-converter/usd-to-krw-rate", "wise.com/es/currency-converter/usd-to-krw-rate", "wise.com/it/currency-converter/usd-to-krw-rate", "wise.com/nl/currency-converter/usd-to-krw-rate", "wise.com/pl/currency-converter/usd-to-krw-rate", "wise.com/br/currency-converter/usd-to-krw-rate", "wise.com/ru/currency-converter/usd-to-krw-rate", "wise.com/th/currency-converter/usd-to-krw-rate"],
    ["Hong Kong Dollar", "wise.com/de/currency-converter/usd-to-hkd-rate", "wise.com/fr/currency-converter/usd-to-hkd-rate", "wise.com/es/currency-converter/usd-to-hkd-rate", "wise.com/it/currency-converter/usd-to-hkd-rate", "wise.com/nl/currency-converter/usd-to-hkd-rate", "wise.com/pl/currency-converter/usd-to-hkd-rate", "wise.com/br/currency-converter/usd-to-hkd-rate", "wise.com/ru/currency-converter/usd-to-hkd-rate", "wise.com/th/currency-converter/usd-to-hkd-rate"],
    ["Brazilian Real", "wise.com/de/currency-converter/usd-to-brl-rate", "wise.com/fr/currency-converter/usd-to-brl-rate", "wise.com/es/currency-converter/usd-to-brl-rate", "wise.com/it/currency-converter/usd-to-brl-rate", "wise.com/nl/currency-converter/usd-to-brl-rate", "wise.com/pl/currency-converter/usd-to-brl-rate", "wise.com/br/currency-converter/usd-to-brl-rate", "wise.com/ru/currency-converter/usd-to-brl-rate", "wise.com/th/currency-converter/usd-to-brl-rate"],
    ["Russian Ruble", "wise.com/de/currency-converter/usd-to-rub-rate", "wise.com/fr/currency-converter/usd-to-rub-rate", "wise.com/es/currency-converter/usd-to-rub-rate", "wise.com/it/currency-converter/usd-to-rub-rate", "wise.com/nl/currency-converter/usd-to-rub-rate", "wise.com/pl/currency-converter/usd-to-rub-rate", "wise.com/br/currency-converter/usd-to-rub-rate", "wise.com/ru/currency-converter/usd-to-rub-rate", "wise.com/th/currency-converter/usd-to-rub-rate"],
    ["South African Rand", "wise.com/de/currency-converter/usd-to-zar-rate", "wise.com/fr/currency-converter/usd-to-zar-rate", "wise.com/es/currency-converter/usd-to-zar-rate", "wise.com/it/currency-converter/usd-to-zar-rate", "wise.com/nl/currency-converter/usd-to-zar-rate", "wise.com/pl/currency-converter/usd-to-zar-rate", "wise.com/br/currency-converter/usd-to-zar-rate", "wise.com/ru/currency-converter/usd-to-zar-rate", "wise.com/th/currency-converter/usd-to-zar-rate"],
    ["Turkish Lira", "wise.com/de/currency-converter/usd-to-try-rate", "wise.com/fr/currency-converter/usd-to-try-rate", "wise.com/es/currency-converter/usd-to-try-rate", "wise.com/it/currency-converter/usd-to-try-rate", "wise.com/nl/currency-converter/usd-to-try-rate", "wise.com/pl/currency-converter/usd-to-try-rate", "wise.com/br/currency-converter/usd-to-try-rate", "wise.com/ru/currency-converter/usd-to-try-rate", "wise.com/th/currency-converter/usd-to-try-rate"],
    ["Mexican Peso", "wise.com/de/currency-converter/usd-to-mxn-rate", "wise.com/fr/currency-converter/usd-to-mxn-rate", "wise.com/es/currency-converter/usd-to-mxn-rate", "wise.com/it/currency-converter/usd-to-mxn-rate", "wise.com/nl/currency-converter/usd-to-mxn-rate", "wise.com/pl/currency-converter/usd-to-mxn-rate", "wise.com/br/currency-converter/usd-to-mxn-rate", "wise.com/ru/currency-converter/usd-to-mxn-rate", "wise.com/th/currency-converter/usd-to-mxn-rate"],
    ["Indonesian Rupiah", "wise.com/de/currency-converter/usd-to-idr-rate", "wise.com/fr/currency-converter/usd-to-idr-rate", "wise.com/es/currency-converter/usd-to-idr-rate", "wise.com/it/currency-converter/usd-to-idr-rate", "wise.com/nl/currency-converter/usd-to-idr-rate", "wise.com/pl/currency-converter/usd-to-idr-rate", "wise.com/br/currency-converter/usd-to-idr-rate", "wise.com/ru/currency-converter/usd-to-idr-rate", "wise.com/th/currency-converter/usd-to-idr-rate"],
    ["Malaysian Ringgit", "wise.com/de/currency-converter/usd-to-myr-rate", "wise.com/fr/currency-converter/usd-to-myr-rate", "wise.com/es/currency-converter/usd-to-myr-rate", "wise.com/it/currency-converter/usd-to-myr-rate", "wise.com/nl/currency-converter/usd-to-myr-rate", "wise.com/pl/currency-converter/usd-to-myr-rate", "wise.com/br/currency-converter/usd-to-myr-rate", "wise.com/ru/currency-converter/usd-to-myr-rate", "wise.com/th/currency-converter/usd-to-myr-rate"],
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
        processed_data_table.append(data_table[0]) # Add header row

    for row_index, current_data_row in enumerate(data_table[1:], start=1): 
        print(f"\nProcessing row {row_index}/{len(data_table)-1}: {current_data_row[0]}")
        processed_row = [current_data_row[0]]

        for url_index, partial_url in enumerate(current_data_row[1:], start=1): 
            if partial_url and partial_url.strip():
                full_url = f"https://{partial_url}" # Script prepends https://
                title, meta_description = get_seo_data_with_scraperapi(full_url, SCRAPERAPI_KEY)
                
                cell_content = f"{full_url}\nTitle: {title}\nMeta: {meta_description}"
                processed_row.append(cell_content)
                
                # Determine if it's the very last URL to avoid sleeping after it
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
