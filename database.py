import json
from abc import ABC, abstractmethod
from typing import List
from scraper import Product

class DatabaseInterface(ABC):
    @abstractmethod
    def save_products(self, products: List[Product]):
        pass

    @abstractmethod
    def load_products(self) -> List[Product]:
        pass

class JSONDatabase(DatabaseInterface):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_products(self, products: List[Product]):
        with open(self.file_path, 'w') as f:
            json.dump([product.__dict__ for product in products], f)

    def load_products(self) -> List[Product]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return [Product(**item) for item in data]
        except FileNotFoundError:
            return []
