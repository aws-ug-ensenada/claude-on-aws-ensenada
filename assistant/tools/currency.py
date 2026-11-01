"""Currency conversion from Frankfurter (European Central Bank rates, free, no API key)."""

import json
import urllib.parse
import urllib.request

from strands import tool


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert money between currencies using today's reference rate.

    Args:
        amount: How much money to convert.
        from_currency: ISO code to convert from, e.g. "USD".
        to_currency: ISO code to convert to, e.g. "MXN".
    """
    params = urllib.parse.urlencode({"amount": amount, "from": from_currency.upper(), "to": to_currency.upper()})
    with urllib.request.urlopen(f"https://api.frankfurter.dev/v1/latest?{params}", timeout=10) as resp:
        data = json.load(resp)
    # Frankfurter's "rates" already holds the converted total; name it so the model doesn't mistake it for a rate.
    to, total = next(iter(data["rates"].items()))
    return {"amount": amount, "from": data["base"], "to": to, "converted_amount": total,
            "rate": round(total / amount, 4), "rate_date": data["date"]}


TOOLS = [convert_currency]
