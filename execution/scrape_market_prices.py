#!/usr/bin/env python3
"""
Market Price Scraper for Chilean Vehicle Marketplaces
Primary: autofact.cl (most reliable Chilean vehicle valuation)
Fallback: MercadoLibre Chile
"""

import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup


def normalize_model_for_url(model):
    """Normalize model name for autofact.cl URL format"""
    # Remove version/trim info, keep main model name
    # e.g., "AVEO II LS 1.4" -> "aveo"
    # e.g., "CX-5" -> "cx_5"
    # e.g., "MIDI TRUCK CARGO BOX 1.3" -> "midi_truck"
    
    model_clean = model.lower().strip()
    
    # Remove engine size patterns like "1.4", "2.0", "1.3"
    model_clean = re.sub(r'\s+\d+\.\d+$', '', model_clean)
    model_clean = re.sub(r'\s+\d+\.\d+\s', ' ', model_clean)
    
    # Remove common trim levels
    for trim in ['ls', 'lt', 'ltz', 'se', 'ex', 'dx', 'gl', 'gls', 'ii', 'iii', 'iv',
                 'cargo', 'box', 'base', 'full', 'limited', 'sport', 'premium']:
        model_clean = re.sub(rf'\b{trim}\b', '', model_clean)
    
    model_clean = model_clean.strip()
    
    # Take first 1-2 words as the core model name
    words = model_clean.split()
    if len(words) > 2:
        model_clean = ' '.join(words[:2])
    
    # Replace spaces and hyphens with underscores for URL
    model_clean = model_clean.replace('-', '_').replace(' ', '_')
    
    # Remove double underscores
    model_clean = re.sub(r'_+', '_', model_clean).strip('_')
    
    return model_clean


def search_market_price(make, model, year, max_results=10):
    """
    Search for vehicle market price, primarily using autofact.cl
    
    Args:
        make: Vehicle make/brand (e.g., "MAZDA")
        model: Vehicle model (e.g., "CX-5")
        year: Vehicle year (e.g., "2018")
        max_results: Maximum number of results to retrieve
    
    Returns:
        dict with pricing data
    """
    result = {
        "success": False,
        "make": make,
        "model": model,
        "year": year,
        "listings": [],
        "average_price": None,
        "min_price": None,
        "max_price": None,
        "source": None,
        "error": None
    }
    
    driver = None
    
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Searching market prices for: {make} {model} {year}")
        print(f"{'='*60}\n")
        
        # Setup Chrome options - HEADLESS (no popup window)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        print("🌐 Starting headless browser...")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        # ===== STRATEGY 1: Autofact.cl (Primary) =====
        make_lower = make.lower().strip()
        model_url = normalize_model_for_url(model)
        
        autofact_url = f"https://www.autofact.cl/valor-comercial-autos/{make_lower}/{model_url}/{year}"
        print(f"\n📍 Strategy 1: Autofact.cl")
        print(f"   URL: {autofact_url}")
        
        try:
            driver.get(autofact_url)
            time.sleep(4)
            
            page_source = driver.page_source
            
            # Save for debugging
            with open('.tmp/autofact_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            driver.save_screenshot('.tmp/autofact_screenshot.png')
            
            soup = BeautifulSoup(page_source, 'html.parser')
            page_text = soup.get_text()
            
            # Look for prices in autofact format: "$XX.XXX.XXX"
            # Autofact shows "Precio promedio" / "Precio más bajo" / "Precio más alto"
            prices_found = []
            
            # Pattern: Chilean peso format $X.XXX.XXX or $XX.XXX.XXX
            price_matches = re.findall(r'\$\s*([\d]{1,3}(?:\.[\d]{3})+)', page_text)
            
            for match in price_matches:
                price_str = match.replace('.', '')
                try:
                    price = int(price_str)
                    # Valid car price range: $1.5M to $100M CLP
                    if 1500000 <= price <= 100000000:
                        prices_found.append(price)
                        print(f"   ✓ Found price: ${price:,}")
                except ValueError:
                    continue
            
            # Remove duplicates
            prices_found = list(set(prices_found))
            
            if prices_found:
                result["success"] = True
                result["source"] = "autofact.cl"
                result["average_price"] = int(sum(prices_found) / len(prices_found))
                result["min_price"] = min(prices_found)
                result["max_price"] = max(prices_found)
                result["num_listings"] = len(prices_found)
                print(f"\n   ✅ Autofact prices found!")
                print(f"   💰 Average: ${result['average_price']:,}")
                print(f"   📉 Range: ${result['min_price']:,} - ${result['max_price']:,}")
                return result
            else:
                print(f"   ⚠️ No prices found on autofact.cl")
                
        except Exception as e:
            print(f"   ❌ Autofact error: {str(e)}")
        
        # ===== STRATEGY 2: Try autofact with simplified model name =====
        # Try just the first word of the model
        model_simple = model.split()[0].lower().replace('-', '_')
        if model_simple != model_url:
            autofact_url2 = f"https://www.autofact.cl/valor-comercial-autos/{make_lower}/{model_simple}/{year}"
            print(f"\n📍 Strategy 2: Autofact (simplified model)")
            print(f"   URL: {autofact_url2}")
            
            try:
                driver.get(autofact_url2)
                time.sleep(4)
                
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                page_text = soup.get_text()
                
                prices_found = []
                price_matches = re.findall(r'\$\s*([\d]{1,3}(?:\.[\d]{3})+)', page_text)
                
                for match in price_matches:
                    price_str = match.replace('.', '')
                    try:
                        price = int(price_str)
                        if 1500000 <= price <= 100000000:
                            prices_found.append(price)
                            print(f"   ✓ Found price: ${price:,}")
                    except ValueError:
                        continue
                
                prices_found = list(set(prices_found))
                
                if prices_found:
                    result["success"] = True
                    result["source"] = "autofact.cl"
                    result["average_price"] = int(sum(prices_found) / len(prices_found))
                    result["min_price"] = min(prices_found)
                    result["max_price"] = max(prices_found)
                    result["num_listings"] = len(prices_found)
                    print(f"\n   ✅ Autofact prices found (simplified)!")
                    print(f"   💰 Average: ${result['average_price']:,}")
                    return result
                    
            except Exception as e:
                print(f"   ❌ Autofact simplified error: {str(e)}")
        
        # ===== STRATEGY 3: MercadoLibre with year filtering =====
        search_query = f"{make} {model} {year}".strip()
        ml_url = f"https://vehiculos.mercadolibre.cl/{make_lower}-{model_url}-{year}_NoIndex_True"
        print(f"\n📍 Strategy 3: MercadoLibre")
        print(f"   URL: {ml_url}")
        
        try:
            driver.get(ml_url)
            time.sleep(5)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Save for debugging
            with open('.tmp/market_search.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            driver.save_screenshot('.tmp/market_search.png')
            
            # Calculate year tolerance
            try:
                target_year = int(year)
                min_year = target_year - 2
                max_year = target_year + 2
            except:
                min_year, max_year = 1990, 2030
            
            prices = []
            
            # Find listings with year+price
            listings = soup.find_all(['article', 'div', 'li'],
                class_=lambda x: x and any(k in str(x).lower() for k in ['card', 'listing', 'item']))
            
            for listing in listings:
                text = listing.get_text()
                year_match = re.search(r'\b(19|20)\d{2}\b', text)
                listing_year = int(year_match.group(0)) if year_match else None
                
                if listing_year and min_year <= listing_year <= max_year:
                    price_match = re.search(r'\$\s*[\d.,]+', text)
                    if price_match:
                        price_clean = ''.join(filter(str.isdigit, price_match.group(0)))
                        if len(price_clean) >= 7:
                            try:
                                price = int(price_clean)
                                if 1500000 <= price <= 100000000:
                                    prices.append(price)
                                    print(f"   ✓ ML: {listing_year} - ${price:,}")
                            except ValueError:
                                continue
            
            prices = list(set(prices))
            
            if prices:
                result["success"] = True
                result["source"] = "mercadolibre.cl"
                result["average_price"] = int(sum(prices) / len(prices))
                result["min_price"] = min(prices)
                result["max_price"] = max(prices)
                result["num_listings"] = len(prices)
                print(f"\n   ✅ MercadoLibre prices found!")
                print(f"   💰 Average: ${result['average_price']:,}")
                return result
                
        except Exception as e:
            print(f"   ❌ MercadoLibre error: {str(e)}")
        
        # ===== STRATEGY 4: ChileAutos =====
        chileautos_url = f"https://www.chileautos.cl/vehiculos/autos-veh%C3%ADculo/{make_lower}/{model_simple}/{year}-ano/"
        print(f"\n📍 Strategy 4: ChileAutos")
        print(f"   URL: {chileautos_url}")
        
        try:
            driver.get(chileautos_url)
            time.sleep(5)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            page_text = soup.get_text()
            
            prices_found = []
            price_matches = re.findall(r'\$\s*([\d]{1,3}(?:\.[\d]{3})+)', page_text)
            
            for match in price_matches:
                price_str = match.replace('.', '')
                try:
                    price = int(price_str)
                    if 1500000 <= price <= 100000000:
                        prices_found.append(price)
                        print(f"   ✓ Found: ${price:,}")
                except ValueError:
                    continue
            
            prices_found = list(set(prices_found))
            
            if prices_found:
                result["success"] = True
                result["source"] = "chileautos.cl"
                result["average_price"] = int(sum(prices_found) / len(prices_found))
                result["min_price"] = min(prices_found)
                result["max_price"] = max(prices_found)
                result["num_listings"] = len(prices_found)
                print(f"\n   ✅ ChileAutos prices found!")
                print(f"   💰 Average: ${result['average_price']:,}")
                return result
                
        except Exception as e:
            print(f"   ❌ ChileAutos error: {str(e)}")
        
        # No source worked
        if not result["success"]:
            result["error"] = "No prices found from any source"
            print("\n❌ All sources failed to return prices")
        
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
    
    return result


def main():
    """Command line interface"""
    if len(sys.argv) < 4:
        print("Usage: python scrape_market_prices.py <MAKE> <MODEL> <YEAR>")
        print("Example: python scrape_market_prices.py MAZDA CX-5 2018")
        sys.exit(1)
    
    make = sys.argv[1]
    model = sys.argv[2]
    year = sys.argv[3]
    
    result = search_market_price(make, model, year)
    
    print(f"\n{'='*60}")
    print("📈 MARKET VALUATION RESULT")
    print(f"{'='*60}")
    
    if result["success"]:
        print(f"✓ Success:        {result['success']}")
        print(f"🚗 Vehicle:        {result['make']} {result['model']} {result['year']}")
        print(f"📊 Source:         {result['source']}")
        print(f"💰 Average Price:  ${result['average_price']:,}")
        print(f"📉 Min Price:      ${result['min_price']:,}")
        print(f"📈 Max Price:      ${result['max_price']:,}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print(f"{'='*60}\n")
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
