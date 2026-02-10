# How to Set Up ChromeDriver for Selenium

## Quick Install (Mac)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ChromeDriver
brew install chromedriver

# Allow ChromeDriver to run (bypass Mac security)
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

## Alternative: Manual Download

1. Check your Chrome version: Chrome menu → About Google Chrome
2. Download matching ChromeDriver from: https://googlechromelabs.github.io/chrome-for-testing/
3. Extract and move to /usr/local/bin/chromedriver
4. Run: `chmod +x /usr/local/bin/chromedriver`
5. Run: `xattr -d com.apple.quarantine /usr/local/bin/chromedriver`

## Test Installation

```bash
chromedriver --version
```

You should see: `ChromeDriver 1XX.X.XXXX.XX`

## Usage

Once installed, run the scraper:

```bash
python3 execution/scrape_patentechile.py LXBW68
```
