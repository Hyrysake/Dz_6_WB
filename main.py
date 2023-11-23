import aiohttp
import asyncio
from datetime import datetime, timedelta
import argparse


class ExchangeRateFetcher:
    def __init__(self):
        self.base_url = "https://api.privatbank.ua/p24api/exchange_rates"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def fetch_exchange_rate(self, date):
        url = f"{self.base_url}?json&date={date}"
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['exchangeRate']
            else:
                raise Exception(f"Failed to fetch data for date {date}, status code: {response.status}")

    async def fetch_exchange_rates(self, num_days):
        current_date = datetime.now()
        exchange_rates = []

        for _ in range(num_days):
            formatted_date = current_date.strftime("%d.%m.%Y")
            data = await self.fetch_exchange_rate(formatted_date)

            # Extracting relevant data from the API response
            rates = {
                'EUR': {
                    'sale': None,
                    'purchase': None
                },
                'USD': {
                    'sale': None,
                    'purchase': None
                }
            }

            # Find the relevant exchange rates for EUR and USD
            for entry in data:
                if entry['currency'] == 'EUR':
                    rates['EUR']['sale'] = entry['saleRateNB']
                    rates['EUR']['purchase'] = entry['purchaseRateNB']
                elif entry['currency'] == 'USD':
                    rates['USD']['sale'] = entry['saleRateNB']
                    rates['USD']['purchase'] = entry['purchaseRateNB']

            exchange_rates.append({formatted_date: rates})
            current_date -= timedelta(days=1)

        return exchange_rates


async def main():
    parser = argparse.ArgumentParser(description='Fetch exchange rates for the last N days.')
    parser.add_argument('num_days', type=int, help='Number of days to fetch exchange rates for')
    args = parser.parse_args()

    async with ExchangeRateFetcher() as exchange_rate_fetcher:
        exchange_rates = await exchange_rate_fetcher.fetch_exchange_rates(args.num_days)

    print(exchange_rates)


if __name__ == "__main__":
    asyncio.run(main())
