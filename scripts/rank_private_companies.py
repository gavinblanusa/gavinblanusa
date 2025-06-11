"""Rank private companies based on available metrics.

This script loads ``companies.csv`` and calculates a composite score for
ranking. The score is a weighted combination of valuation, revenue, and
employee count. It outputs the top 100 companies to ``stdout``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COMPANY_CSV = DATA_DIR / "companies.csv"

WEIGHTS = {
    "valuation_usd_millions": 0.6,
    "revenue_usd_millions": 0.3,
    "employees": 0.1,
}


def load_companies() -> List[Dict[str, float]]:
    """Load company data from the CSV file."""
    companies = []
    with COMPANY_CSV.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            companies.append({
                "company": row["company"],
                "valuation_usd_millions": float(row.get("valuation_usd_millions", 0) or 0),
                "employees": float(row.get("employees", 0) or 0),
                "revenue_usd_millions": float(row.get("revenue_usd_millions", 0) or 0),
            })
    return companies


def compute_score(company: Dict[str, float]) -> float:
    """Compute weighted score for a company."""
    score = 0.0
    for field, weight in WEIGHTS.items():
        score += company.get(field, 0) * weight
    return score


def rank_companies(companies: List[Dict[str, float]]) -> List[Dict[str, float]]:
    """Return companies sorted by composite score descending."""
    return sorted(companies, key=compute_score, reverse=True)


if __name__ == "__main__":
    companies = load_companies()
    ranked = rank_companies(companies)[:100]
    for i, c in enumerate(ranked, start=1):
        score = compute_score(c)
        print(f"{i}. {c['company']} - score: {score:.2f}")

