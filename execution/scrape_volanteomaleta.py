#!/usr/bin/env python3
"""
Scraper for volanteomaleta.cl using undetected-chromedriver.
Alternative source for vehicle data.
"""

import time
import sys
import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

def get_car_info_by_plate(plate):
    """
    Scrape volanteomaleta.cl to get car information by license plate.
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
        options = uc.ChromeOptions()
        # Headless mode allows Cloudflare to detect us more easily.
        # We try to mitigate this with arguments.
        options.add_argument('--headless=new') 
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument(f'--user-data-dir={os.getcwd()}/.tmp/chrome_profile_volante') # Disabled to save space
        
        # Randomize user agent slightly or use a standard one
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        print(f"🌐 Opening browser (stealth mode) for Volante o Maleta...", file=sys.stderr)
        driver = uc.Chrome(options=options, version_main=144) # Let it auto-detect logic
        
        url = "https://volanteomaleta.com/"
        print(f"📍 Navigating to {url}...", file=sys.stderr)
        driver.get(url)
        
        # Wait specifically for Cloudflare to clear
        print(f"🔍 Checking for Cloudflare...", file=sys.stderr)
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
                    pass
                driver.switch_to.default_content()
                time.sleep(5)
        except:
            pass

        # Wait for input
        print(f"🔍 Waiting for search input...", file=sys.stderr)
        try:
            # Based on common structures, or we can look for *any* input type text if ID unknown
            # But let's try to find the form
            search_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "patente"))
            )
        except:
             # Fallback if name is different
             search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")

        search_input.clear()
        search_input.send_keys(plate)
        time.sleep(0.5)
        
        # Click search
        try:
            search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            search_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
            
        driver.execute_script("arguments[0].click();", search_btn)
        
        print("⏳ Waiting for results...", file=sys.stderr)
        time.sleep(5)
        
        # Parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Look for table or specific divs
        # Volanteomaleta.com usually has a table
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    label = cols[0].get_text().strip().lower()
                    val = cols[1].get_text().strip()
                    if "marca" in label: result["make"] = val
                    if "modelo" in label: result["model"] = val
                    if "año" in label: result["year"] = val
                    if "nombre" in label: result["owner"] = val
                    if "rut" in label: result["rut"] = val
        else:
             # saving debug if no table found
             driver.save_screenshot('.tmp/volante_no_table.png')

        if result["make"]:
            result["success"] = True
            print(f"✅ Data found: {result['make']} {result['model']}", file=sys.stderr)
        else:
            result["error"] = "Could not extract data (Table not found or empty)"

    except Exception as e:
        result["error"] = f"Scraper error: {str(e)}"
        print(f"❌ Exception: {e}", file=sys.stderr)
        if driver:
            driver.save_screenshot('.tmp/volante_error.png')
            
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
