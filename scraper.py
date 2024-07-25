import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Product:
    product_title: str
    product_price: float
    path_to_image: str

class Scraper:
    def __init__(self, base_url: str, max_pages: Optional[int] = None, proxy: Optional[str] = None):
        self.base_url = base_url
        self.max_pages = max_pages
        self.proxy = proxy

    async def scrape(self) -> List[Product]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://dentalstall.com/shop/',
        }
        print(f"Starting scrape of {self.base_url}")
        async with aiohttp.ClientSession() as session:
            products = []
            page = 1
            while True:
                if page == 1:
                    url = self.base_url
                else:
                    url = f"{self.base_url}page/{page}/"

                if self.max_pages and page > self.max_pages:
                    print(f"Reached max pages: {self.max_pages}")
                    break

                print(f"Scraping page: {url}")
                try:
                    async with session.get(url, proxy=self.proxy, headers=headers) as response:
                        print(f"Response status code: {response.status}")
                        if response.status == 200:
                            content = await response.text()
                            print("Page content fetched successfully")
                            soup = BeautifulSoup(content, 'html.parser')
                            product_elements = soup.find_all('li', class_='product')
                            print(f"Found {len(product_elements)} products on page {page}")
                            if not product_elements and page != 1:
                                print("No more products found. Ending scrape.")
                                break
                            for element in product_elements:
                                title_element = element.find('h2', class_='woo-loop-product__title')
                                price_element = element.find('ins')
                                image_element = element.find('img', class_='attachment-woocommerce_thumbnail')

                                if title_element and price_element and image_element:
                                    title = title_element.text.strip()
                                    price = float(price_element.text.strip().replace('₹', '').replace(',', ''))
                                    image = image_element.get('data-lazy-src') or image_element.get('src')
                                    products.append(Product(title, price, image))
                                    print(f"Scraped product - Title: {title}, Price: {price}, Image: {image}")
                            page += 1
                        else:
                            print(f"Failed to fetch page {page}. Status code: {response.status}")
                            if page == 1:
                                break
                            else:
                                await asyncio.sleep(5)  # Simple retry mechanism
                except Exception as e:
                    print(f"Error scraping page {page}: {str(e)}")
                    await asyncio.sleep(5)  # Simple retry mechanism
        print(f"Scraping completed. Total products scraped: {len(products)}")
        return products
