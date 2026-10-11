import requests
from decimal import Decimal

FRANKFURTER_API = "https://api.frankfurter.dev/v2"


def get_converted_currency(
    amount: float | Decimal,
    from_currency: str,
    to_currency: str,
) -> dict:
    """
    Convert an amount from one currency to another using Frankfurter.
    Example: get_converted_currency(100, "USD", "INR")
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    response = requests.get(
        f"{FRANKFURTER_API}/rate/{from_currency}/{to_currency}",
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    rate = Decimal(str(data["rate"]))
    converted_amount = Decimal(str(amount)) * rate

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount,
        "exchange_rate": rate,
        "converted_amount": converted_amount,
        "rate_date": data["date"],
    }


if __name__ == "__main__":
    result = get_converted_currency(100, "USD", "INR")

    print(f"100 {result['from_currency']} = "
          f"{result['converted_amount']:.2f} {result['to_currency']}")
    print(f"Exchange rate: 1 {result['from_currency']} = "
          f"{result['exchange_rate']} {result['to_currency']}")
    print(f"Rate date: {result['rate_date']}")