import asyncio
from scraper import Scraper

async def main():
    # Initialize the scraper with the base URL and optional parameters
    scraper = Scraper("https://dentalstall.com/shop/", max_pages=5)

    # Run the scraper
    products = await scraper.scrape()

    # Print the scraped products
    for product in products:
        print(f"Title: {product.product_title}, Price: {product.product_price}, Image: {product.path_to_image}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
