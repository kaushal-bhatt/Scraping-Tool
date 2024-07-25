from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import APIKeyHeader
from typing import Optional
import asyncio
from scraper import Scraper, Product
from database import JSONDatabase
from notifier import ConsoleNotifier
from cache import Cache
from config import API_KEY, REDIS_HOST, REDIS_PORT, REDIS_DB, DATABASE_FILE

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key")

database = JSONDatabase(DATABASE_FILE)
notifier = ConsoleNotifier()
cache = Cache(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def get_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    print(f"Received API key: {x_api_key}")  # Debug print
    print(f"Expected API key: {API_KEY}")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@app.post("/scrape")
async def scrape_products(max_pages: Optional[int] = None, proxy: Optional[str] = None, api_key: str = Depends(get_api_key)):
    try:
        scraper = Scraper("https://dentalstall.com/shop/", max_pages, proxy)
        products = await scraper.scrape()
        print(f"Products scraped: {products}")

        updated_count = 0
        for product in products:
            cached_price = cache.get(product.product_title)
            if cached_price is None or float(cached_price) != product.product_price:
                cache.set(product.product_title, str(product.product_price))
                updated_count += 1

        database.save_products(products)
        message = f"Scraping completed. {len(products)} products scraped, {updated_count} updated in the database."
        notifier.notify(message)

        return {"message": message, "products": [p.__dict__ for p in products]}
    except Exception as e:
        error_message = f"Error during scraping: {str(e)}"
        print(error_message)
        return {"error": error_message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)