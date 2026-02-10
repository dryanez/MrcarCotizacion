#!/usr/bin/env python3
"""
Market Price Scraper for Chilean Vehicle Marketplaces
Searches for similar vehicles on chileautos.cl to estimate market value
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


def search_market_price(make, model, year, max_results=10):
    """
    Search for similar vehicles on Chilean marketplaces
    
    Args:
        make: Vehicle make/brand (e.g., "FOTON")
        model: Vehicle model (e.g., "MIDI TRUCK")
        year: Vehicle year (e.g., "2020")
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
        "error": None
    }
    
    driver = None
    
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Searching market prices for: {make} {model} {year}")
        print(f"{'='*60}\n")
        
        # Setup Chrome options - HEADLESS (no popup window)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')  # NEW headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize driver (let Selenium Manager handle driver)
        print("🌐 Starting browser...")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        # Prepare search query with year for better results
        search_query = f"{make} {model} {year}".strip()
        
        # Try multiple Chilean marketplaces
        marketplaces = [
            {
                "name": "MercadoLibre",
                "base_url": "https://vehiculos.mercadolibre.cl",
                "search_url": f"https://vehiculos.mercadolibre.cl/{make.lower()}-{model.lower().replace(' ', '-')}-{year}_NoIndex_True"
            },
            {
                "name": "Yapo.cl",
                "base_url": "https://www.yapo.cl",
                "search_url": f"https://www.yapo.cl/region_metropolitana/vehiculos?q={search_query.replace(' ', '+')}"
            }
        ]
        
        success = False
        for marketplace in marketplaces:
            try:
                print(f"\n📍 Trying {marketplace['name']}...")
                driver.get(marketplace['search_url'])
                time.sleep(5)
                
                page_source = driver.page_source
                
                # Check if we hit a CAPTCHA
                if 'captcha' in page_source.lower() or 'datadome' in page_source.lower():
                    print(f"  ⚠️  CAPTCHA detected on {marketplace['name']}, skipping...")
                    continue
                
                # Check if we got results
                if len(page_source) > 5000:  # Reasonable page size
                    print(f"  ✓ Successfully loaded {marketplace['name']}")
                    success = True
                    break
            except Exception as e:
                print(f"  ❌ Error loading {marketplace['name']}: {str(e)}")
                continue
        
        if not success:
            result["error"] = "All marketplaces blocked or failed"
            print("❌ All marketplaces failed")
            return result
        
        # Parse prices from HTML with year filtering
        print("🔍 Extracting prices from search results (with year filtering)...")
        soup = BeautifulSoup(page_source, 'html.parser')
        prices = []
        
        # Calculate year tolerance (±2 years)
        try:
            target_year = int(year)
            min_year = target_year - 2
            max_year = target_year + 2
            print(f"   Year filter: {min_year}-{max_year}")
        except:
            target_year = None
            min_year = 1990
            max_year = 2030
        
        # Look for vehicle cards/listings
        # Pattern 1: Try to find structured listings with both price and year
        listings = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['card', 'listing', 'item', 'vehicle']))
        
        print(f"   Found {len(listings)} potential listings")
        
        for listing in listings:
            listing_text = listing.get_text()
            
            # Look for year in the listing
            year_match = re.search(r'\b(19|20)\d{2}\b', listing_text)
            listing_year = int(year_match.group(0)) if year_match else None
            
            # Only process if year matches (±2 years tolerance)
            if listing_year and min_year <= listing_year <= max_year:
                # Look for price in this listing
                price_match = re.search(r'\$\s*[\d.,]+', listing_text)
                if price_match:
                    price_clean = ''.join(filter(str.isdigit, price_match.group(0)))
                    if len(price_clean) >= 7:  # At least 1 million
                        try:
                            price = float(price_clean)
                            if 1000000 <= price <= 100000000:  # Reasonable car price
                                prices.append(price)
                                print(f"     ✓ Found: {listing_year} - ${price:,.0f}")
                        except ValueError:
                            continue
        
        # If no structured listings, try fallback (less reliable)
        if not prices:
            print("   No listings with year+price found, trying fallback...")
            # Pattern 2: Price in meta tags (usually accurate)
            price_metas = soup.find_all('meta', {'itemprop': 'price'})
            for meta in price_metas:
                price_content = meta.get('content', '')
                if price_content:
                    try:
                        price = float(price_content.replace(',', '').replace('.', ''))
                        if 1000000 <= price <= 100000000:
                            prices.append(price)
                    except ValueError:
                        continue
        
        # Remove duplicates and calculate statistics
        prices = list(set(prices))
        
        print(f"✓ Found {len(prices)} valid prices matching year range")
        
        if prices:
            result["success"] = True
            result["average_price"] = int(sum(prices) / len(prices))
            result["min_price"] = int(min(prices))
            result["max_price"] = int(max(prices))
            result["num_listings"] = len(prices)
            print(f"💰 Average: ${result['average_price']:,}")
            print(f"   Range: ${result['min_price']:,} - ${result['max_price']:,}")
        else:
            result["success"] = False
            result["error"] = "No prices found matching the year range"
            print("⚠️  No valid prices extracted for target year")
        
        # Save screenshot for debugging
        driver.save_screenshot('.tmp/market_search.png')
        print("📸 Screenshot saved to .tmp/market_search.png")
        
        # Get page source and parse
        page_source = driver.page_source
        
        # Save HTML for debugging
        with open('.tmp/market_search.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("💾 HTML saved to .tmp/market_search.html")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for vehicle listings
        # ChileAutos uses various structures, try multiple selectors
        listing_selectors = [
            'article',
            'div[class*="listing"]',
            'div[class*="vehicle"]',
            'div[class*="card"]',
            'li[class*="item"]'
        ]
        
        listings_found = []
        for selector in listing_selectors:
            listings_found = soup.select(selector)
            if len(listings_found) > 5:  # Found reasonable number of listings
                print(f"✓ Found {len(listings_found)} listings using selector: {selector}")
                break
        
        if not listings_found:
            print("⚠️  No listings found with standard selectors")
            # Try to find price elements directly
            price_elements = soup.find_all(text=re.compile(r'\$[\d\.,]+'))
            if price_elements:
                result["error"] = f"Found prices but couldn't match to vehicles. Check .tmp/market_search.html"
                print(f"⚠️  Found {len(price_elements)} price elements")
            else:
                result["error"] = "No listings or prices found"
            return result
        
        # Extract data from listings
        for idx, listing in enumerate(listings_found[:max_results]):
            listing_data = {
                "title": None,
                "price": None,
                "year": None,
                "url": None
            }
            
            # Get title/description
            title_elem = listing.find(['h2', 'h3', 'h4', 'h5', 'a'], class_=re.compile(r'title|name|heading', re.I))
            if title_elem:
                listing_data["title"] = title_elem.get_text().strip()
            
            # Get price
            price_elem = listing.find(text=re.compile(r'\$[\d\.,]+'))
            if price_elem:
                # Extract numeric price
                price_text = price_elem.strip()
                price_match = re.search(r'\$([\d\.,]+)', price_text)
                if price_match:
                    price_str = price_match.group(1).replace('.', '').replace(',', '')
                    try:
                        listing_data["price"] = int(price_str)
                    except ValueError:
                        pass
            
            # Get year
            year_match = re.search(r'\b(19|20)\d{2}\b', listing.get_text())
            if year_match:
                listing_data["year"] = year_match.group(0)
            
            # Get URL
            link_elem = listing.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    href = base_url + href
                listing_data["url"] = href
            
            # Only add if we got at least a price
            if listing_data["price"]:
                result["listings"].append(listing_data)
                print(f"  {idx+1}. {listing_data['title'][:50] if listing_data['title'] else 'N/A'} - ${listing_data['price']:,}")
        
        # Calculate statistics
        if result["listings"]:
            prices = [l["price"] for l in result["listings"]]
            result["average_price"] = int(sum(prices) / len(prices))
            result["min_price"] = min(prices)
            result["max_price"] = max(prices)
            result["success"] = True
            
            print(f"\n📊 PRICE STATISTICS:")
            print(f"  Found {len(result['listings'])} comparable listings")
            print(f"  Average: ${result['average_price']:,}")
            print(f"  Range: ${result['min_price']:,} - ${result['max_price']:,}")
        else:
            result["error"] = "No valid listings with prices found"
            print("❌ No valid listings found")
        
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
        print("Example: python scrape_market_prices.py FOTON 'MIDI TRUCK' 2020")
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
        print(f"📊 Listings Found: {len(result['listings'])}")
        print(f"💰 Average Price:  ${result['average_price']:,}")
        print(f"📉 Min Price:      ${result['min_price']:,}")
        print(f"📈 Max Price:      ${result['max_price']:,}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print(f"{'='*60}\n")
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
