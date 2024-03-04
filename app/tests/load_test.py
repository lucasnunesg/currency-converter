import asyncio
import random
import time

import aiohttp

list_of_currencies = ["EUR", "BTC", "USD", "BRL", "ETH"]


async def make_request(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main(num_requests: int = 1000, version: str = "v1"):
    urls = list_urls_constructor(num_requests)
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        tasks = [make_request(session, url) for url in urls for _ in range(num_requests // len(urls))]
        await asyncio.gather(*tasks)
        end_time = time.time()
        print(f"Version: {version}")
        print(f'Total time for {num_requests} requests: {end_time - start_time} seconds')


def get_random_currency():
    """Returns a random currency from base list (list_of_currencies)."""
    return random.choice(list_of_currencies)


def url_constructor(c1: str, c2: str, amount: float, version: str = "v1"):
    """Returns the built URL based on two currencies and an amount."""
    return f"http://0.0.0.0:8000/{version}/conversion?source_currency={c1}&target_currency={c2}&amount={amount}"


def list_urls_constructor(n: int, version: str = "v1") -> list:
    list_urls = []
    for i in range(n):
        c1 = get_random_currency()
        c2 = get_random_currency()
        amount = random.uniform(1, 1000)
        list_urls.append(url_constructor(c1, c2, amount, version))
    return list_urls


if __name__ == "__main__":
    asyncio.run(main(1000, "v1"))
    asyncio.run(main(1000, "v2"))
