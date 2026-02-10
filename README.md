# Mr. Car - Chilean Vehicle Valuation App

Complete vehicle quotation system for Chile with automatic license plate lookup and pricing engine.

## Features

- ✅ Multi-step wizard form (personal info + vehicle patent)
- ✅ Automatic vehicle info extraction from Chilean registries
- ✅ Manufacturing year detection (not payment year)
- ✅ Complete pricing engine:
  - Market valuation (with depreciation model for old cars)
  - Immediate purchase offer (52% of market price)
  - Consignment liquidation (tiered: 5.355% for >$8M, fixed $428,400 for ≤$8M)
- ✅ WhatsApp integration (+56968517995)
- ✅ localStorage for form data persistence

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Scraping**: Selenium + BeautifulSoup
- **Deployment**: Vercel

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python3 app.py

# Access at http://localhost:8080
```

## Deployment

Deploy to Vercel:

```bash
# Connect to GitHub repository
git remote add origin https://github.com/dryanez/MrcarCotizacion.git

# Push to GitHub
git push -u origin main

# Deploy on Vercel (connect the GitHub repo)
```

## Project Structure

```
Mrcar/
├── app.py                      # Flask backend API
├── index.html                  # Multi-step wizard frontend
├── mrcarlogo.png              # Mr. Car logo
├── execution/
│   ├── scrape_patentechile.py # Vehicle info scraper
│   ├── scrape_market_prices.py # Market pricing scraper
│   └── pricing_engine.py      # Pricing calculation logic
├── vercel.json                 # Vercel deployment config
└── requirements.txt            # Python dependencies
```

## API Endpoints

- `GET /` - Main application
- `GET /api/vehicle/<plate>` - Get vehicle info by plate
- `GET /api/market-price?make=X&model=Y&year=Z&mileage=M` - Get complete pricing

## Pricing Logic

```json
{
  "market_price": "From market data or depreciation model",
  "immediate_offer": "market_price * 0.52 (rounded to 100k)",
  "consignment_liquidation": "market_price > 8M ? (market_price * 0.94645) : (market_price - 428400)"
}
```

## License

Proprietary - Mr. Car 2026
