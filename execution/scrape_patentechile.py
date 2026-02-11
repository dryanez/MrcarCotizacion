#!/usr/bin/env python3
"""
Scraper for patentechile.com using Selenium (handles JavaScript)
Retrieves Chilean vehicle information by license plate for FREE.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
from typing import Dict

def get_car_info_by_plate(plate: str, headless: bool = True) -> Dict[str, any]:
    """
    Scrape patentechile.com to get car information by license plate.
    
    Args:
        plate: Chilean license plate (e.g., "LXBW68")
        headless: Run browser in headless mode (default True)
    
    Returns:
        Dictionary with car information
    """
    
    plate = plate.upper().strip()
    
    result = {
        "success": False,
        "plate": plate,
        "make": None,
        "model": None,
        "year": None,
        "owner_name": None,
        "owner_rut": None,
        "error": None
    }
    
    driver = None
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')  # Use new headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Let Selenium Manager handle driver download automatically
        print(f"🌐 Opening browser...")
        from selenium.webdriver.chrome.service import Service
        service = Service()  # Selenium Manager will auto-download matching driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        # Navigate to the website
        print(f"📍 Navigating to patentechile.com...")
        driver.get("https://www.patentechile.com/")
        
        # Wait for page to load
        time.sleep(2)
        
        # Find the search input
        print(f"🔍 Searching for plate: {plate}...")
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "inputTerm"))
            )
        except TimeoutException:
            result["error"] = "Could not find search input field"
            return result
        
        # Enter the plate number
        search_input.clear()
        search_input.send_keys(plate)
        time.sleep(1)
        
        # Click the search button using JavaScript to bypass ads
        try:
            search_btn = driver.find_element(By.ID, "searchBtn")
            # Scroll to button first
            driver.execute_script("arguments[0].scrollIntoView(true);", search_btn)
            time.sleep(1)
            # Click using JavaScript to bypass any overlays
            driver.execute_script("arguments[0].click();", search_btn)
            print("✓ Search button clicked")
        except NoSuchElementException:
            result["error"] = "Could not find search button"
            return result
        
        # Wait for results page to load
        print("⏳ Waiting for results...")
        time.sleep(5)  # Give time for JavaScript to load results
        
        # Try to detect if we're on a results page
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Save screenshot for debugging
        driver.save_screenshot('.tmp/selenium_screenshot.png')
        print("📸 Screenshot saved to .tmp/selenium_screenshot.png")
        
        # Get page source
        page_source = driver.page_source
        
        # Save HTML for debugging
        with open('.tmp/selenium_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("💾 HTML saved to .tmp/selenium_page.html")
        
        # Parse with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find the results table
        results_table = soup.find('table', {'id': 'tbl-results'})
        
        if results_table:
            # Extract data from table rows
            rows = results_table.find_all('tr')
            
            # Flag to know when we're in the vehicle info section
            in_vehicle_section = False
            
            for row in rows:
                cells = row.find_all('td')
                
                # Check if this is a section header
                if len(cells) == 1 and cells[0].get('colspan') == '2':
                    header_text = cells[0].get_text().strip().lower()
                    in_vehicle_section = 'vehicular' in header_text
                    continue
                
                if len(cells) == 2:
                    # Get the label (first cell) and value (second cell)
                    label = cells[0].get_text().strip().replace('\xa0', '').lower()
                    value = cells[1].get_text().strip()
                    
                    if 'marca' in label:
                        result["make"] = value
                    elif 'modelo' in label:
                        result["model"] = value
                    elif 'año' in label and in_vehicle_section:
                        # Only extract year from vehicle section, not payment section
                        # Extract just the year number (e.g. "2006" from "2006" or "2025 (PAGO TOTAL)")
                        import re
                        year_match = re.search(r'\b(19|20)\d{2}\b', value)
                        if year_match:
                            result["year"] = year_match.group(0)
                    elif 'nombre' in label:
                        result["owner_name"] = value
                    elif 'rut' in label:
                        result["owner_rut"] = value
            
            # Check if we got data
            if result["make"] or result["model"] or result["year"]:
                result["success"] = True
                print(f"✅ Successfully retrieved data for {plate}")
            else:
                result["error"] = "No vehicle data found in table. Check .tmp/selenium_page.html"
                print(f"❌ No data extracted for {plate}")
        else:
            result["error"] = "Results table not found. Check .tmp/selenium_page.html"
            print(f"❌ Table not found for {plate}")
        
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        print(f"❌ Error: {e}")
        
    finally:
        if driver:
            driver.quit()
    
    return result


def main():
    """Test the scraper"""
    import sys
    
    if len(sys.argv) > 1:
        plate = sys.argv[1]
    else:
        plate = "LXBW68"  # Default test plate
    
    print(f"\n{'='*60}")
    print(f"🚗 Searching for plate: {plate}")
    print(f"{'='*60}\n")
    
    info = get_car_info_by_plate(plate, headless=True)  # Set to False to see browser
    
    print(f"\n{'='*60}")
    print("📊 RESULTS:")
    print(f"{'='*60}")
    print(f"✓ Success:    {info['success']}")
    print(f"📋 Plate:      {info['plate']}")
    print(f"🏢 Make:       {info['make']}")
    print(f"🚙 Model:      {info['model']}")
    print(f"📅 Year:       {info['year']}")
    print(f"👤 Owner:      {info['owner_name']}")
    print(f"🆔 RUT:        {info['owner_rut']}")
    
    if info.get('error'):
        print(f"\n❌ Error: {info['error']}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
