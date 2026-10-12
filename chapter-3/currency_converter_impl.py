import sys
import os

# Add root directory to sys.path so lib can be imported from any location
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from lib import get_converted_currency

if __name__ == "__main__":
    result = get_converted_currency(100, "USD", "INR")

    print(f"100 {result['from_currency']} = "
          f"{result['converted_amount']:.2f} {result['to_currency']}")
    print(f"Exchange rate: 1 {result['from_currency']} = "
          f"{result['exchange_rate']} {result['to_currency']}")
    print(f"Rate date: {result['rate_date']}")