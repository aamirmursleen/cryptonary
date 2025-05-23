import requests
import csv
from bs4 import BeautifulSoup
import time
import re

class ScraperAPIScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.scraperapi.com"
        
    def extract_semantic_content(self, soup):
        """Extract all semantic HTML elements from the entire page"""
        content_parts = []
        
        # 1. Title tag
        title = soup.find('title')
        if title:
            content_parts.append(f"TITLE: {title.get_text().strip()}")
        
        # 2. Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content_parts.append(f"META DESCRIPTION: {meta_desc.get('content').strip()}")
        
        # Remove only scripts, styles, and ads - keep everything else
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        
        # 3. All heading tags (H1-H6) - extract all of them
        for i in range(1, 7):
            heading_tags = soup.find_all(f'h{i}')
            if heading_tags:
                heading_content = []
                for heading in heading_tags:
                    heading_text = heading.get_text().strip()
                    if heading_text and len(heading_text) > 1:
                        heading_content.append(heading_text)
                if heading_content:
                    content_parts.append(f"H{i}: {' | '.join(heading_content)}")
        
        # 4. All paragraph content
        paragraphs = soup.find_all('p')
        if paragraphs:
            paragraph_content = []
            for p in paragraphs:
                p_text = p.get_text().strip()
                if p_text and len(p_text) > 5:  # Include even short meaningful paragraphs
                    paragraph_content.append(p_text)
            
            if paragraph_content:
                content_parts.append(f"PARAGRAPHS: {' '.join(paragraph_content)}")
        
        # 5. FAQ sections specifically
        faq_selectors = [
            'div[class*="faq"]', 'section[class*="faq"]', 'div[id*="faq"]',
            'div[class*="FAQ"]', 'section[class*="FAQ"]', 'div[id*="FAQ"]',
            'div[class*="question"]', 'div[class*="accordion"]'
        ]
        
        faq_content = []
        for selector in faq_selectors:
            faq_elements = soup.select(selector)
            for faq in faq_elements:
                faq_text = faq.get_text().strip()
                if faq_text and len(faq_text) > 10:
                    faq_content.append(faq_text)
        
        if faq_content:
            content_parts.append(f"FAQ SECTIONS: {' '.join(faq_content)}")
        
        # 6. Lists (ul, ol) - often contain important information
        lists = soup.find_all(['ul', 'ol'])
        if lists:
            list_content = []
            for lst in lists:
                list_text = lst.get_text().strip()
                if list_text and len(list_text) > 10:
                    list_content.append(list_text)
            
            if list_content:
                content_parts.append(f"LISTS: {' '.join(list_content)}")
        
        # 7. Table content
        tables = soup.find_all('table')
        if tables:
            table_content = []
            for table in tables:
                table_text = table.get_text().strip()
                if table_text and len(table_text) > 10:
                    table_content.append(table_text)
            
            if table_content:
                content_parts.append(f"TABLES: {' '.join(table_content)}")
        
        # 8. All remaining content from divs, sections, articles, spans
        other_elements = soup.find_all(['div', 'span', 'section', 'article', 'aside', 'main'])
        additional_content = []
        processed_text = set()  # Avoid duplicates
        
        for element in other_elements:
            # Skip if it's already processed as part of other sections
            if element.find_parent(['table', 'ul', 'ol']) or any(faq_sel in str(element.get('class', [])) + str(element.get('id', '')) for faq_sel in ['faq', 'FAQ', 'question', 'accordion']):
                continue
                
            text = element.get_text().strip()
            if text and len(text) > 15 and text not in processed_text:
                # Only get direct text, not nested
                direct_text = ''.join(element.find_all(string=True, recursive=False)).strip()
                if direct_text and len(direct_text) > 15:
                    additional_content.append(direct_text)
                    processed_text.add(direct_text)
        
        if additional_content:
            content_parts.append(f"ADDITIONAL CONTENT: {' '.join(additional_content)}")
        
        return content_parts
    
    def scrape_url(self, url):
        """Scrape a single URL using ScraperAPI and return complete semantic content"""
        try:
            # ScraperAPI parameters
            params = {
                'api_key': self.api_key,
                'url': url,
                'render': 'false',  # Don't render JavaScript (faster)
            }
            
            print(f"Scraping: {url}")
            response = requests.get(self.base_url, params=params, timeout=60)
            
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract all semantic content
                content_parts = self.extract_semantic_content(soup)
                
                # Join all parts - NO WORD LIMIT, get everything
                full_content = '\n\n'.join(content_parts)
                
                # Clean up formatting only
                full_content = re.sub(r'\n{3,}', '\n\n', full_content)  # Max 2 consecutive newlines
                full_content = re.sub(r' +', ' ', full_content)  # Single spaces
                
                return full_content.strip()
            else:
                print(f"Error scraping {url}: Status code {response.status_code}")
                return f"Error: Status code {response.status_code}"
                
        except Exception as e:
            print(f"Exception scraping {url}: {str(e)}")
            return f"Error: {str(e)}"
    
    def scrape_paired_urls_to_csv(self, url_pairs, output_file):
        """Scrape paired URLs and save to CSV with both domains in same row"""
        results = []
        
        for i, (language, coinmarketcap_url, cryptonary_url) in enumerate(url_pairs, 1):
            print(f"Processing {i}/{len(url_pairs)} - Language: {language}")
            
            # Scrape CoinMarketCap URL
            coinmarketcap_content = self.scrape_url(coinmarketcap_url)
            time.sleep(1)  # Rate limiting
            
            # Scrape Cryptonary URL
            cryptonary_content = self.scrape_url(cryptonary_url)
            time.sleep(1)  # Rate limiting
            
            results.append({
                'language': language,
                'coinmarketcap_url': coinmarketcap_url,
                'coinmarketcap_content': coinmarketcap_content,
                'cryptonary_url': cryptonary_url,
                'cryptonary_content': cryptonary_content
            })
        
        # Save to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['language', 'coinmarketcap_url', 'coinmarketcap_content', 'cryptonary_url', 'cryptonary_content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"Results saved to {output_file}")

def main():
    # Replace with your ScraperAPI key
    API_KEY = "67de34f1cde7abf6f7975d4f7ff9d629"
    
    # Paired URLs by language
    url_pairs = [
        ("English", 
         "https://coinmarketcap.com/currencies/bitcoin/", 
         "https://cryptonary.com/currency-converter/btc/usd/"),
        
        ("German", 
         "https://coinmarketcap.com/de/currencies/bitcoin/", 
         "https://cryptonary.com/de/currency-converter/btc/usd/"),
        
        ("French", 
         "https://coinmarketcap.com/fr/currencies/bitcoin/", 
         "https://cryptonary.com/fr/currency-converter/btc/usd/"),
        
        ("Italian", 
         "https://coinmarketcap.com/it/currencies/bitcoin/", 
         "https://cryptonary.com/it/currency-converter/btc/usd/"),
        
        ("Dutch", 
         "https://coinmarketcap.com/nl/currencies/bitcoin/", 
         "https://cryptonary.com/nl/currency-converter/btc/usd/"),
        
        ("Polish", 
         "https://coinmarketcap.com/pl/currencies/bitcoin/", 
         "https://cryptonary.com/pl/currency-converter/btc/usd/"),
        
        ("Portuguese-Brazil", 
         "https://coinmarketcap.com/pt-br/currencies/bitcoin/", 
         "https://cryptonary.com/pt-BR/currency-converter/btc/usd/"),
        
        ("Russian", 
         "https://coinmarketcap.com/ru/currencies/bitcoin/", 
         "https://cryptonary.com/ru/currency-converter/btc/usd/"),
        
        ("Thai", 
         "https://coinmarketcap.com/th/currencies/bitcoin/", 
         "https://cryptonary.com/th/currency-converter/btc/usd/"),
        
        ("Chinese", 
         "https://coinmarketcap.com/zh/currencies/bitcoin/", 
         "https://cryptonary.com/zh-CN/currency-converter/btc/usd/")
    ]
    
    # Initialize scraper
    scraper = ScraperAPIScraper(API_KEY)
    
    # Scrape paired URLs and save to CSV
    output_file = "bitcoin_complete_content_comparison.csv"
    scraper.scrape_paired_urls_to_csv(url_pairs, output_file)
    
    print("Scraping completed!")

if __name__ == "__main__":
    main()