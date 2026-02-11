#!/usr/bin/env python3
"""
Scraper for patentechile.com using undetected-chromedriver to bypass Cloudflare.
Retrieves Chilean vehicle information by license plate.
"""

import time
import sys
import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import re

def get_car_info_by_plate(plate):
    """
    Scrape patentechile.com to get car information by license plate.
    Uses undetected-chromedriver to bypass Cloudflare Turnstile.
    """
    plate = plate.upper().strip()
    
    result = {
        "success": False,
        "plate": plate,
        "make": None,
        "model": None,
        "year": None,
        "owner": None,
        "rut": None,
        "error": None
    }
    
    driver = None
    try:
        # Configure undetected-chromedriver
        options = uc.ChromeOptions()
        # Headless mode allows Cloudflare to detect us more easily.
        # We try to mitigate this with arguments and persistent profile.
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument(f'--user-data-dir={os.getcwd()}/.tmp/chrome_profile_patente') # Disabled to save space
        
        # Consistent User Agent
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        # Initialize driver
        print(f"🌐 Opening browser (stealth mode)...", file=sys.stderr)
        driver = uc.Chrome(options=options, version_main=144) # Explicitly set version to match installed Chrome
        
        # Navigate to site
        url = "https://patentechile.com/"
        print(f"📍 Navigating to {url}...", file=sys.stderr)
        driver.get(url)
        
        # Wait specifically for Cloudflare to clear
        # We wait for the input element to appear
        print(f"🔍 Waiting for search input...", file=sys.stderr)
        try:
            # Check if we are stuck on Cloudflare
            try:
                iframe = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[starts-with(@src, 'https://challenges.cloudflare.com/')]"))
                )
                if iframe:
                    print("⚠️ Cloudflare challenge detected. Attempting to solve...", file=sys.stderr)
                    driver.switch_to.frame(iframe)
                    try:
                        checkbox = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
                        )
                        checkbox.click()
                        print("✅ Clicked Cloudflare checkbox", file=sys.stderr)
                    except:
                        pass # Might not be a checkbox, just a wait
                    driver.switch_to.default_content()
                    time.sleep(5)
            except:
                pass # No iframe found, proceed

            # Try to click "Patente" tab if it exists (sometimes it defaults to RUT or other)
            try:
                patente_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Patente')] | //a[contains(text(), 'Patente')]")
                patente_tab.click()
                time.sleep(1)
            except:
                pass

            search_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "inputTerm"))
            )
        except TimeoutException:
            # Capture debug info if we timeout (likely stuck at challenge)
            driver.save_screenshot('.tmp/selenium_timeout.png')
            with open('.tmp/selenium_timeout.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            result["error"] = "Timeout waiting for search input (Cloudflare check?)"
            return result

        # Perform search
        print(f"⌨️ Entering plate: {plate}...", file=sys.stderr)
        search_input.clear()
        search_input.send_keys(plate)
        time.sleep(0.5)
        
        # Click search button
        try:
            search_btn = driver.find_element(By.ID, "searchBtn")
            driver.execute_script("arguments[0].click();", search_btn)
        except NoSuchElementException:
            result["error"] = "Search button not found"
            return result
            
        # Wait for results
        print("⏳ Waiting for results...", file=sys.stderr)
        time.sleep(3) # Give time for JS to load
        
        # Parse results
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results_table = soup.find('table', {'id': 'tbl-results'})
        
        if not results_table:
            # Check for "Not Found" message
            if "No se encontraron registros" in driver.page_source:
                result["error"] = "Patente no encontrada"
                return result
            
            # Save debug if table missing but no error msg
            driver.save_screenshot('.tmp/selenium_no_table.png')
            result["error"] = "Results table not found"
            return result
            
        # Extract data
        rows = results_table.find_all('tr')
        in_vehicle_section = False
        
        for row in rows:
            cells = row.find_all('td')
            
            # Check section headers
            if len(cells) == 1 and cells[0].get('colspan') == '2':
                header = cells[0].get_text().strip().lower()
                if 'vehicular' in header:
                    in_vehicle_section = True
                else:
                    in_vehicle_section = False
                continue
            
            # Check data rows
            if len(cells) == 2:
                label = cells[0].get_text().strip().lower()
                value = cells[1].get_text().strip()
                
                if 'marca' in label:
                    result["make"] = value
                elif 'modelo' in label:
                    result["model"] = value
                elif 'año' in label and in_vehicle_section:
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', value)
                    if year_match:
                        result["year"] = year_match.group(0)
                        
                # Owner info (if needed)
                elif 'nombre' in label:
                    result["owner"] = value
                elif 'rut' in label:
                    result["rut"] = value

        if result["make"] or result["model"]:
            result["success"] = True
            print(f"✅ Data found: {result['make']} {result['model']} {result['year']}", file=sys.stderr)
        else:
            result["error"] = "Data extracted but empty fields"

    except Exception as e:
        result["error"] = f"Scraper error: {str(e)}"
        print(f"❌ Exception: {e}", file=sys.stderr)
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
                
    return result

if __name__ == "__main__":
    test_plate = sys.argv[1] if len(sys.argv) > 1 else "LXBW68"
    print(json.dumps(get_car_info_by_plate(test_plate), indent=2, ensure_ascii=False))
