"""Script for collecting data about private companies.

This script is a starting point for fetching valuations and other
information on private companies. Data sources often have restrictions,
so check the terms of service of any API or website you use.
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import Iterable, Dict

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COMPANY_CSV = DATA_DIR / "companies.csv"

API_URL = "https://api.example.com/company"  # Placeholder API


def fetch_company_data(company: str) -> Dict[str, str]:
    """Fetch data about a company from a placeholder API.

    Parameters
    ----------
    company : str
        Name of the company to fetch data for.

    Returns
    -------
    Dict[str, str]
        JSON response from the API converted to a dictionary.
    """
    response = requests.get(API_URL, params={"q": company})
    response.raise_for_status()
    return response.json()


def update_company_csv(rows: Iterable[Dict[str, str]]) -> None:
    """Append rows to the company CSV file."""
    header = ["company", "valuation_usd_millions", "employees", "revenue_usd_millions"]
    COMPANY_CSV.parent.mkdir(exist_ok=True)
    exists = COMPANY_CSV.exists()
    with COMPANY_CSV.open("a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def main(companies: Iterable[str]) -> None:
    collected = []
    for company in companies:
        data = fetch_company_data(company)
        collected.append({
            "company": company,
            "valuation_usd_millions": data.get("valuation"),
            "employees": data.get("employees"),
            "revenue_usd_millions": data.get("revenue"),
        })

    update_company_csv(collected)


if __name__ == "__main__":
    # Example usage: adjust the list to suit your needs.
    companies = ["Stripe", "SpaceX", "Klarna"]
    main(companies)
