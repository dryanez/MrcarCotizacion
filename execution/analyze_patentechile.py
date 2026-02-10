#!/usr/bin/env python3
"""
Analyze patentechile.com structure to understand how the search works
"""

import requests
from bs4 import BeautifulSoup

def analyze_site():
    url = "https://www.patentechile.com/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    print("=" * 80)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Save full HTML for inspection
    with open('.tmp/patentechile_homepage.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("Saved HTML to .tmp/patentechile_homepage.html")
    print("=" * 80)
    
    # Look for all forms
    forms = soup.find_all('form')
    print(f"\nFound {len(forms)} form(s):")
    for i, form in enumerate(forms, 1):
        print(f"\nForm {i}:")
        print(f"  Action: {form.get('action')}")
        print(f"  Method: {form.get('method')}")
        print(f"  ID: {form.get('id')}")
        print(f"  Class: {form.get('class')}")
        
        inputs = form.find_all('input')
        print(f"  Inputs ({len(inputs)}):")
        for inp in inputs:
            print(f"    - name='{inp.get('name')}' id='{inp.get('id')}' type='{inp.get('type')}'")
    
    # Look for search-related elements
    print("\n" + "=" * 80)
    print("Search elements:")
    
    search_input = soup.find('input', {'type': 'search'}) or \
                   soup.find('input', {'id': re.compile(r'search|patente|input', re.I)}) or \
                   soup.find('input', {'name': re.compile(r'search|patente|input', re.I)})
    
    if search_input:
        print(f"Search input found: {search_input}")
    
    # Look for buttons
    buttons = soup.find_all('button')
    print(f"\nFound {len(buttons)} button(s):")
    for btn in buttons:
        print(f"  - {btn.get_text()[:50]} (id='{btn.get('id')}', class='{btn.get('class')}')")
    
    # Look for JavaScript that might handle the search
    scripts = soup.find_all('script')
    print(f"\nFound {len(scripts)} script tags")
    
    for script in scripts:
        src = script.get('src', '')
        if 'search' in src.lower() or 'patente' in src.lower():
            print(f"  Relevant script: {src}")

if __name__ == "__main__":
    import re
    analyze_site()
