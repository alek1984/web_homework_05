import aiohttp
import asyncio
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict

# URL ПриватБанку для отримання курсу валют
API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

class CurrencyFetcher:
    """Клас для отримання курсу валют з API ПриватБанку"""
    
    def __init__(self, days: int, currencies: List[str]):
        self.days = min(days, 10)  # Обмеження до 10 днів
        self.currencies = currencies

    async def fetch_exchange_rate(self, session: aiohttp.ClientSession, date: str) -> Dict:
        """Отримує курс валют на конкретну дату"""
        url = f"{API_URL}{date}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.extract_rates(date, data)
                else:
                    print(f" Помилка отримання даних за {date}: {response.status}")
                    return {}
        except Exception as e:
            print(f" Помилка підключення до API: {e}")
            return {}

    def extract_rates(self, date: str, data: Dict) -> Dict:
        """Виділяє курси тільки для обраних валют"""
        rates = {currency: {} for currency in self.currencies}
        for rate in data.get("exchangeRate", []):
            currency = rate.get("currency")
            if currency in self.currencies:
                rates[currency] = {
                    "sale": rate.get("saleRate", "N/A"),
                    "purchase": rate.get("purchaseRate", "N/A")
                }
        return {date: rates}

    async def get_exchange_rates(self) -> List[Dict]:
        """Отримує курс валют за кілька днів"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.days):
                date = (datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y")
                tasks.append(self.fetch_exchange_rate(session, date))
            return await asyncio.gather(*tasks)

async def main():
    """Основна функція програми"""
    if len(sys.argv) < 2:
        print(" Вкажіть кількість днів. Наприклад: python main.py 3 USD EUR")
        return

    try:
        days = int(sys.argv[1])
        currencies = sys.argv[2:] if len(sys.argv) > 2 else ["USD", "EUR"]
        fetcher = CurrencyFetcher(days, currencies)
        rates = await fetcher.get_exchange_rates()
        print(json.dumps(rates, indent=2, ensure_ascii=False))
    except ValueError:
        print("Некоректний формат числа днів!")

if __name__ == "__main__":
    asyncio.run(main())
