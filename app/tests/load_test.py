import httpx
import random
import time

list_of_currencies = ["EUR", "BTC", "USD", "BRL", "ETH"]


def get_random_currency():
    return random.choice(list_of_currencies)


def url_constructor(c1: str, c2: str, amount: float):
    return f"http://0.0.0.0:8000/v1/conversion?source_currency={c1}&target_currency={c2}&amount={amount}"


def requests_test(request_number: int):
    with httpx.Client() as client:
        n = 0
        start_time = time.time()
        while n <= request_number:
            c1 = get_random_currency()
            c2 = get_random_currency()
            amount = random.uniform(1, 1000)

            req = client.get(url_constructor(c1, c2, amount))
            if req.status_code != 200:
                print(req.status_code)
            n += 1
        end_time = time.time()
        elapsed_time = end_time - start_time
        client.close()
        print(f"Elapsed time: {elapsed_time:.2f}s")


if __name__ == "__main__":
    requests_test(1000)
