from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import APIKeyHeader
from typing import Optional
import asyncio
from scraper import Scraper, Product
from database import JSONDatabase
from notifier import ConsoleNotifier
from cache import Cache

app = FastAPI()

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

database = JSONDatabase("products.json")
notifier = ConsoleNotifier()
cache = Cache()

def get_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/scrape")
async def scrape_products(max_pages: Optional[int] = None, proxy: Optional[str] = None, api_key: str = Depends(get_api_key)):
    scraper = Scraper("https://dentalstall.com/shop/", max_pages, proxy)
    products = await scraper.scrape()
    
    updated_count = 0
    for product in products:
        cached_price = cache.get(product.product_title)
        if cached_price is None or float(cached_price) != product.product_price:
            cache.set(product.product_title, str(product.product_price))
            updated_count += 1

    database.save_products(products)
    notifier.notify(f"Scraping completed. {len(products)} products scraped, {updated_count} updated in the database.")
    
    return {"message": f"Scraping completed. {len(products)} products scraped, {updated_count} updated in the database."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)