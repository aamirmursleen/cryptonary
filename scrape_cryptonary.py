import requests
import json
import csv
import time
import re
from openai import OpenAI
from bs4 import BeautifulSoup
import pandas as pd

class ComprehensiveCoinMarketCapTranslator:
    def __init__(self, openai_api_key, scraperapi_key):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.scraperapi_key = scraperapi_key
        self.scraperapi_base_url = "http://api.scraperapi.com"
        
        self.languages = {
            'en': {'name': 'English', 'url': 'https://coinmarketcap.com/currencies/bitcoin/'},
            'de': {'name': 'German', 'url': 'https://coinmarketcap.com/de/currencies/bitcoin/'},
            'fr': {'name': 'French', 'url': 'https://coinmarketcap.com/fr/currencies/bitcoin/'},
            'it': {'name': 'Italian', 'url': 'https://coinmarketcap.com/it/currencies/bitcoin/'},
            'nl': {'name': 'Dutch', 'url': 'https://coinmarketcap.com/nl/currencies/bitcoin/'},
            'pl': {'name': 'Polish', 'url': 'https://coinmarketcap.com/pl/currencies/bitcoin/'},
            'pt-br': {'name': 'Portuguese (Brazil)', 'url': 'https://coinmarketcap.com/pt-br/currencies/bitcoin/'},
            'ru': {'name': 'Russian', 'url': 'https://coinmarketcap.com/ru/currencies/bitcoin/'},
            'th': {'name': 'Thai', 'url': 'https://coinmarketcap.com/th/currencies/bitcoin/'},
            'zh': {'name': 'Chinese', 'url': 'https://coinmarketcap.com/zh/currencies/bitcoin/'}
        }
        
        # Your original JSON structure to translate
        self.base_json = {
            "title": "${coinName?.toUpperCase()} Price Today | Live ${ticker} Chart & Live Trends | Cryptonary",
            "description": "Track ${coinName} (${ticker}) live price, market cap, real-time charts, trading volume, and latest crypto news on Cryptonary.",
            "h1": "${coinName} Price (${ticker})",
            "search": {
                "placeholder": "Search Coin",
                "noResults": "No coins found"
            },
            "marketStats": {
                "price": "Price",
                "rank": "Rank",
                "coin": "Coin",
                "high": "High",
                "low": "Low",
                "change24h": "24h",
                "keyMetrics": "Key Metrics",
                "updated": "Updated",
                "marketCap": "Market Cap",
                "24hTradingVolume": "24h Trading Volume",
                "circulatingSupply": "Circulating Supply",
                "maxSupply": "Max Supply"
            },
            "tokenInfo": {
                "title": "Token Information",
                "priceToday": "The {tokenName} price today is ${price}, reflecting a",
                "change24h": "{change}% {direction} over the past 24 hours",
                "increase": "increase",
                "decrease": "decrease",
                "tradingVolume": "With a 24-hour trading volume of ${volume} and a market capitalization of ${marketCap}, {tokenName} maintains its position as the #{rank} ranked cryptocurrency by market cap. It currently dominates {dominance}% of the total crypto market.",
                "priceHistory": "{tokenName} reached an all-time high of ${ath} on {athDate}, and recorded its lowest price of ${atl} on {atlDate}. The asset has a circulating supply of {circulatingSupply} {symbol} out of a maximum supply of {maxSupply} {symbol}.",
                "marketSentiment": "Market sentiment remains optimistic, with the Fear & Greed Index showing a value of {value}, indicating a state of",
                "greed": "Greed",
                "fear": "Fear",
                "neutral": "Neutral"
            },
            "strengthWeakness": {
                "strengths": "Strengths",
                "weaknesses": "Weaknesses"
            },
            "aboutToken": {
                "title": "About"
            },
            "trendingCoins": {
                "title": "Trending Coins"
            },
            "exchangeRates": {
                "title": "Search Ticker Trends",
                "liveData": "Live Data"
            },
            "relatedConversions": {
                "title": "Live {USDT} Prices",
                "from": "From",
                "to": "To",
                "topConversions": "Top {USDT} Price Today Conversions",
                "priceOfUSDTInUSD": "PRICE OF {USDT} IN {USD}"
            },
            "cryptoPricesFAQ": {
                "heading": "Frequently Asked Questions",
                "questions": {
                    "currentPrice": "What is the current price of {{coinName}}?",
                    "priceChange24h": "How much has {{coinName}} changed in the last 24 hours?",
                    "ath": "When was {{coinName}} all-time high?",
                    "founder": "Who created {{coinName}}?",
                    "strengths": "What are the strengths of {{coinName}}?",
                    "liveTracking": "Can I track {{coinName}} live on Cryptonary?"
                },
                "answers": {
                    "currentPrice": "The current price of {{coinName}} is {{price}} USD.",
                    "priceChange24h": "{{coinName}} has changed by {{changePercentage}}% in the last 24 hours.",
                    "ath": "{{coinName}} reached its all-time high of {{athPrice}} USD on {{athDate}}.",
                    "founder": "{{founders}}",
                    "strengthsDefault": "{{coinName}} has notable features.",
                    "strengthsList": "{{coinName}}'s strengths include: {{strengths}}.",
                    "liveTracking": "Yes, you can track {{coinName}} live using Cryptonary's tools such as the crypto currency converter and live dashboard."
                }
            }
        }

    def extract_comprehensive_semantic_content(self, soup):
        """Extract ALL semantic HTML elements from the entire CoinMarketCap page"""
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

    def scrape_coinmarketcap_comprehensive(self, url, language_code):
        """Scrape CoinMarketCap page using ScraperAPI with comprehensive content extraction"""
        try:
            # ScraperAPI parameters
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false',  # Don't render JavaScript (faster)
            }
            
            print(f"🔍 Scraping {language_code}: {url}")
            response = requests.get(self.scraperapi_base_url, params=params, timeout=60)
            
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract ALL semantic content using comprehensive method
                content_parts = self.extract_comprehensive_semantic_content(soup)
                
                # Join all parts - NO WORD LIMIT, get everything
                full_content = '\n\n'.join(content_parts)
                
                # Clean up formatting only
                full_content = re.sub(r'\n{3,}', '\n\n', full_content)  # Max 2 consecutive newlines
                full_content = re.sub(r' +', ' ', full_content)  # Single spaces
                
                print(f"✅ Successfully scraped {language_code} - {len(full_content)} characters")
                return full_content.strip()
            else:
                print(f"❌ Error scraping {language_code}: Status code {response.status_code}")
                return f"Error: Status code {response.status_code}"
                
        except Exception as e:
            print(f"❌ Exception scraping {language_code}: {str(e)}")
            return f"Error: {str(e)}"

    def translate_with_comprehensive_context(self, target_language, language_code, comprehensive_content):
        """Use OpenAI GPT-4 with comprehensive CoinMarketCap content for accurate translation"""
        
        # Create rich context from comprehensive scraped data
        context_prompt = f"""
        COMPREHENSIVE COINMARKETCAP {target_language.upper()} CONTENT FOR CONTEXT:
        
        {comprehensive_content[:8000]}  # Limit to 8000 chars to avoid token limits
        
        TRANSLATION TASK:
        Use the above comprehensive CoinMarketCap content to understand how cryptocurrency terms, 
        phrases, and UI elements are translated in {target_language}. 
        
        Match CoinMarketCap's exact terminology and style for:
        - Price/market data terms
        - Trading/exchange terminology  
        - FAQ questions and answers
        - Navigation elements
        - Call-to-action phrases
        - Technical cryptocurrency terms
        """
        
        main_prompt = f"""
        You are a professional cryptocurrency translator with access to CoinMarketCap's {target_language} content.
        
        CRITICAL TRANSLATION RULES:
        1. NEVER change JSON keys - only translate the values
        2. PRESERVE all variables EXACTLY: ${{coinName}}, ${{ticker}}, {{tokenName}}, etc.
        3. Keep title structure: "${{coinName?.toUpperCase()}} [translated] | [translated] | Cryptonary"
        4. Use EXACT CoinMarketCap terminology from the context provided
        5. Match CoinMarketCap's professional crypto language style
        6. Maintain all punctuation, formatting, and structure
        7. For FAQ sections, use natural, professional financial language
        
        CONTEXT: {context_prompt}
        
        JSON TO TRANSLATE:
        {json.dumps(self.base_json, indent=2, ensure_ascii=False)}
        
        Return ONLY the translated JSON, no explanations.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are a professional cryptocurrency translator specializing in {target_language}. You have access to comprehensive CoinMarketCap content in {target_language} to ensure accurate, contextual translations. Return only valid JSON."},
                    {"role": "user", "content": main_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent translations
                max_tokens=4000
            )
            
            translated_content = response.choices[0].message.content.strip()
            
            # Clean up response to ensure it's valid JSON
            if translated_content.startswith('```json'):
                translated_content = translated_content.replace('```json', '').replace('```', '').strip()
            elif translated_content.startswith('```'):
                translated_content = translated_content.replace('```', '').strip()
            
            # Parse to validate JSON
            translated_json = json.loads(translated_content)
            print(f"✅ Successfully translated to {target_language} ({language_code})")
            return translated_json
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error for {target_language}: {str(e)}")
            print("Raw response:", translated_content[:500])
            return None
        except Exception as e:
            print(f"❌ Translation error for {target_language}: {str(e)}")
            return None

    def process_all_languages_comprehensive(self):
        """Main processing function with comprehensive scraping and translation"""
        results = {}
        scraped_comprehensive_data = {}
        
        print("🚀 STARTING COMPREHENSIVE COINMARKETCAP TRANSLATION PROCESS")
        print("=" * 70)
        
        # Step 1: Comprehensive scraping of all CoinMarketCap pages
        print("📥 STEP 1: COMPREHENSIVE SCRAPING OF ALL COINMARKETCAP PAGES")
        print("-" * 50)
        
        for lang_code, lang_info in self.languages.items():
            if lang_code == 'en':  # We'll handle English separately
                continue
                
            scraped_data = self.scrape_coinmarketcap_comprehensive(
                lang_info['url'], 
                lang_code
            )
            
            if scraped_data and not scraped_data.startswith('Error:'):
                scraped_comprehensive_data[lang_code] = scraped_data
                print(f"✅ {lang_info['name']}: {len(scraped_data)} characters extracted")
            else:
                print(f"❌ {lang_info['name']}: Failed to scrape")
                
            time.sleep(2)  # Be respectful to ScraperAPI
        
        # Step 2: Add English original
        results['en'] = self.base_json
        print(f"\n✅ Added English (original base)")
        
        # Step 3: Comprehensive translation using scraped context
        print(f"\n🔄 STEP 2: TRANSLATING WITH COMPREHENSIVE CONTEXT")
        print("-" * 50)
        
        for lang_code, lang_info in self.languages.items():
            if lang_code == 'en':  # Skip English
                continue
                
            if lang_code in scraped_comprehensive_data:
                print(f"🔄 Translating {lang_info['name']} using {len(scraped_comprehensive_data[lang_code])} chars of context...")
                
                translated = self.translate_with_comprehensive_context(
                    lang_info['name'], 
                    lang_code, 
                    scraped_comprehensive_data[lang_code]
                )
                
                if translated:
                    results[lang_code] = translated
                    print(f"✅ {lang_info['name']}: Translation completed")
                else:
                    print(f"❌ {lang_info['name']}: Translation failed")
            else:
                print(f"⚠️ {lang_info['name']}: No scraped data, skipping translation")
            
            time.sleep(1)  # Rate limiting for OpenAI
        
        return results, scraped_comprehensive_data

    def save_comprehensive_results(self, translations, scraped_data, base_filename='comprehensive_coinmarketcap_translations'):
        """Save comprehensive results to multiple formats"""
        
        print(f"\n💾 STEP 3: SAVING COMPREHENSIVE RESULTS")
        print("-" * 40)
        
        # 1. Save translations as CSV
        translations_csv = f"{base_filename}.csv"
        flattened_data = []
        
        for lang_code, translation in translations.items():
            def flatten_dict(d, parent_key='', sep='.'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            flattened = flatten_dict(translation)
            flattened['language_code'] = lang_code
            flattened['language_name'] = self.languages[lang_code]['name']
            flattened_data.append(flattened)
        
        df = pd.DataFrame(flattened_data)
        cols = ['language_code', 'language_name'] + [col for col in df.columns if col not in ['language_code', 'language_name']]
        df = df[cols]
        df.to_csv(translations_csv, index=False, encoding='utf-8')
        print(f"✅ Translations saved: {translations_csv}")
        
        # 2. Save scraped data as CSV for reference
        scraped_csv = f"{base_filename}_scraped_context.csv"
        scraped_list = []
        for lang_code, content in scraped_data.items():
            scraped_list.append({
                'language_code': lang_code,
                'language_name': self.languages[lang_code]['name'],
                'scraped_content': content,
                'content_length': len(content)
            })
        
        scraped_df = pd.DataFrame(scraped_list)
        scraped_df.to_csv(scraped_csv, index=False, encoding='utf-8')
        print(f"✅ Scraped context saved: {scraped_csv}")
        
        # 3. Save individual JSON files
        import os
        json_dir = 'translations_json'
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        
        for lang_code, translation in translations.items():
            json_file = f"{json_dir}/{lang_code}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({lang_code: translation}, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Individual JSON files saved in: {json_dir}/")
        
        return translations_csv, scraped_csv

def main():
    print("🎯 COMPREHENSIVE COINMARKETCAP TRANSLATION SYSTEM")
    print("=" * 60)
    
    # Configuration - REPLACE WITH YOUR ACTUAL KEYS
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
    SCRAPERAPI_KEY = "67de34f1cde7abf6f7975d4f7ff9d629"  # Your provided key
    
    if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        print("❌ Please set your OpenAI API key in the OPENAI_API_KEY variable")
        return
    
    # Initialize comprehensive translator
    translator = ComprehensiveCoinMarketCapTranslator(OPENAI_API_KEY, SCRAPERAPI_KEY)
    
    try:
        # Process all languages with comprehensive scraping and translation
        translations, scraped_data = translator.process_all_languages_comprehensive()
        
        if translations:
            print(f"\n🎉 COMPREHENSIVE PROCESSING COMPLETED!")
            print("=" * 50)
            print(f"📊 Languages processed: {len(translations)}")
            print(f"📊 Comprehensive scraping: {len(scraped_data)} pages")
            
            # Save comprehensive results
            trans_csv, scraped_csv = translator.save_comprehensive_results(translations, scraped_data)
            
            print(f"\n📋 FINAL DELIVERABLES:")
            print(f"✅ Translation CSV: {trans_csv}")
            print(f"✅ Scraped Context CSV: {scraped_csv}")
            print(f"✅ Individual JSON files: translations_json/ directory")
            
            # Display sample translations
            print(f"\n🔍 SAMPLE TRANSLATIONS:")
            for lang_code in ['de', 'fr', 'es'][:2]:  # Show first 2 available
                if lang_code in translations:
                    print(f"\n{translator.languages[lang_code]['name']} ({lang_code}):")
                    print(f"  Title: {translations[lang_code].get('title', 'N/A')[:80]}...")
                    print(f"  H1: {translations[lang_code].get('h1', 'N/A')}")
        else:
            print("❌ No translations were generated - check your API keys and network connection")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
