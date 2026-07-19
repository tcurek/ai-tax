"""Currency conversion tools for AI Tax agents.

Rates are yearly average exchange rates expressed as foreign currency units per
1 US dollar. For example, Canada 2024 = 1.370 means 1 USD = 1.370 CAD.
"""

from __future__ import annotations

from langchain_core.tools import tool

EXCHANGE_RATES: dict[str, dict[str, object]] = {
    "afghanistan": {"country": "Afghanistan", "currency": "Afghani", "rates": {2025: 69.637, 2024: 70.649, 2023: 82.635, 2022: 90.084, 2021: 83.484}},
    "algeria": {"country": "Algeria", "currency": "Dinar", "rates": {2025: 131.627, 2024: 134.124, 2023: 135.933, 2022: 142.123, 2021: 135.011}},
    "argentina": {"country": "Argentina", "currency": "Peso", "rates": {2025: 1243.369, 2024: 915.161, 2023: 296.154, 2022: 130.792, 2021: 95.098}},
    "australia": {"country": "Australia", "currency": "Dollar", "rates": {2025: 1.551, 2024: 1.516, 2023: 1.506, 2022: 1.442, 2021: 1.332}},
    "bahrain": {"country": "Bahrain", "currency": "Dinar", "rates": {2025: 0.377, 2024: 0.377, 2023: 0.377, 2022: 0.377, 2021: 0.377}},
    "brazil": {"country": "Brazil", "currency": "Real", "rates": {2025: 5.593, 2024: 5.392, 2023: 4.994, 2022: 5.165, 2021: 5.395}},
    "canada": {"country": "Canada", "currency": "Dollar", "rates": {2025: 1.398, 2024: 1.370, 2023: 1.350, 2022: 1.301, 2021: 1.254}},
    "cayman islands": {"country": "Cayman Islands", "currency": "Dollar", "rates": {2025: 0.821, 2024: 0.833, 2023: 0.833, 2022: 0.833, 2021: 0.833}},
    "china": {"country": "China", "currency": "Yuan", "rates": {2025: 7.129, 2024: 7.189, 2023: 7.075, 2022: 6.730, 2021: 6.452}},
    "denmark": {"country": "Denmark", "currency": "Krone", "rates": {2025: 6.617, 2024: 6.896, 2023: 6.890, 2022: 7.077, 2021: 6.290}},
    "egypt": {"country": "Egypt", "currency": "Pound", "rates": {2025: 49.233, 2024: 45.345, 2023: 30.651, 2022: 19.208, 2021: 15.697}},
    "euro zone": {"country": "Euro Zone", "currency": "Euro", "rates": {2025: 0.886, 2024: 0.924, 2023: 0.924, 2022: 0.951, 2021: 0.846}},
    "hong kong": {"country": "Hong Kong", "currency": "Dollar", "rates": {2025: 7.796, 2024: 7.803, 2023: 7.829, 2022: 7.831, 2021: 7.773}},
    "hungary": {"country": "Hungary", "currency": "Forint", "rates": {2025: 352.869, 2024: 365.603, 2023: 353.020, 2022: 372.775, 2021: 303.292}},
    "iceland": {"country": "Iceland", "currency": "Krona", "rates": {2025: 128.262, 2024: 137.958, 2023: 137.857, 2022: 135.296, 2021: 126.986}},
    "india": {"country": "India", "currency": "Rupee", "rates": {2025: 87.133, 2024: 83.677, 2023: 82.572, 2022: 78.598, 2021: 73.936}},
    "iraq": {"country": "Iraq", "currency": "Dinar", "rates": {2025: 1309.753, 2024: 1309.744, 2023: 1376.529, 2022: 1459.51, 2021: 1460.133}},
    "israel": {"country": "Israel", "currency": "New Shekel", "rates": {2025: 3.451, 2024: 3.701, 2023: 3.687, 2022: 3.361, 2021: 3.232}},
    "japan": {"country": "Japan", "currency": "Yen", "rates": {2025: 149.632, 2024: 151.353, 2023: 140.511, 2022: 131.454, 2021: 109.817}},
    "lebanon": {"country": "Lebanon", "currency": "Pound", "rates": {2025: 89568.540, 2024: 78958.611, 2023: 13730.988, 2022: 1515.669, 2021: 1519.228}},
    "mexico": {"country": "Mexico", "currency": "Peso", "rates": {2025: 19.212, 2024: 18.330, 2023: 17.733, 2022: 20.110, 2021: 20.284}},
    "morocco": {"country": "Morocco", "currency": "Dirham", "rates": {2025: 9.344, 2024: 9.937, 2023: 10.134, 2022: 10.275, 2021: 8.995}},
    "new zealand": {"country": "New Zealand", "currency": "Dollar", "rates": {2025: 1.719, 2024: 1.654, 2023: 1.630, 2022: 1.578, 2021: 1.415}},
    "norway": {"country": "Norway", "currency": "Kroner", "rates": {2025: 10.392, 2024: 10.756, 2023: 10.564, 2022: 9.619, 2021: 8.598}},
    "qatar": {"country": "Qatar", "currency": "Rial", "rates": {2025: 3.643, 2024: 3.643, 2023: 3.643, 2022: 3.644, 2021: 3.644}},
    "russia": {"country": "Russia", "currency": "Ruble", "rates": {2025: 83.755, 2024: 92.837, 2023: 85.509, 2022: 69.896, 2021: 73.686}},
    "saudi arabia": {"country": "Saudi Arabia", "currency": "Riyal", "rates": {2025: 3.751, 2024: 3.752, 2023: 3.752, 2022: 3.755, 2021: 3.751}},
    "singapore": {"country": "Singapore", "currency": "Dollar", "rates": {2025: 1.307, 2024: 1.336, 2023: 1.343, 2022: 1.379, 2021: 1.344}},
    "south africa": {"country": "South Africa", "currency": "Rand", "rates": {2025: 17.884, 2024: 18.326, 2023: 18.457, 2022: 16.377, 2021: 14.789}},
    "south korean": {"country": "South Korean", "currency": "Won", "rates": {2025: 1421.779, 2024: 1364.153, 2023: 1306.686, 2022: 1291.729, 2021: 1144.883}},
    "sweden": {"country": "Sweden", "currency": "Krona", "rates": {2025: 9.813, 2024: 10.577, 2023: 10.613, 2022: 10.122, 2021: 8.584}},
    "switzerland": {"country": "Switzerland", "currency": "Franc", "rates": {2025: 0.831, 2024: 0.881, 2023: 0.899, 2022: 0.955, 2021: 0.914}},
    "taiwan": {"country": "Taiwan", "currency": "Dollar", "rates": {2025: 31.167, 2024: 32.117, 2023: 31.160, 2022: 29.813, 2021: 27.932}},
    "thailand": {"country": "Thailand", "currency": "Baht", "rates": {2025: 32.870, 2024: 35.267, 2023: 34.802, 2022: 35.044, 2021: 31.997}},
    "tunisia": {"country": "Tunisia", "currency": "Dinar", "rates": {2025: 2.996, 2024: 3.111, 2023: 3.103, 2022: 3.082, 2021: 2.778}},
    "turkey": {"country": "Turkey", "currency": "New Lira", "rates": {2025: 39.546, 2024: 32.867, 2023: 23.824, 2022: 16.572, 2021: 8.904}},
    "united arab emirates": {"country": "United Arab Emirates", "currency": "Dirham", "rates": {2025: 3.673, 2024: 3.673, 2023: 3.673, 2022: 3.673, 2021: 3.673}},
    "united kingdom": {"country": "United Kingdom", "currency": "Pound", "rates": {2025: 0.759, 2024: 0.783, 2023: 0.804, 2022: 0.811, 2021: 0.727}},
    "venezuela": {"country": "Venezuela", "currency": "Bolivar (Fuerte)", "rates": {2025: 13057596875331350.0, 2024: 3833558362078.0, 2023: 2863377461538.5, 2022: 666470505836.6, 2021: 232298866894.8}},
}


def _normalize_country(country: str) -> str:
    return " ".join(country.casefold().strip().split())


@tool
def list_supported_currencies() -> list[dict[str, str]]:
    """List countries/currencies supported by the static exchange-rate table."""
    return [
        {"country": str(data["country"]), "currency": str(data["currency"])}
        for data in EXCHANGE_RATES.values()
    ]


@tool
def convert_currency_to_usd(
    amount: float,
    country: str,
    year: int,
) -> dict[str, float | int | str]:
    """Convert a foreign currency amount to USD using yearly average exchange rates.

    Args:
        amount: Foreign currency amount to convert to USD.
        country: Country/region name from the supported currency table.
        year: Exchange-rate year. Supported years: 2021 through 2025.
    """
    country_key = _normalize_country(country)
    exchange_data = EXCHANGE_RATES.get(country_key)
    if exchange_data is None:
        supported = ", ".join(str(data["country"]) for data in EXCHANGE_RATES.values())
        raise ValueError(f"Unsupported country: {country}. Supported countries: {supported}")

    rates = exchange_data["rates"]
    if not isinstance(rates, dict) or year not in rates:
        raise ValueError(f"Unsupported year: {year}. Supported years: 2021, 2022, 2023, 2024, 2025")

    rate = float(rates[year])
    usd_amount = amount / rate

    return {
        "foreign_amount": amount,
        "usd_amount": usd_amount,
        "country": str(exchange_data["country"]),
        "currency": str(exchange_data["currency"]),
        "rate": rate,
        "year": year,
    }


CURRENCY_TOOLS = [list_supported_currencies, convert_currency_to_usd]
