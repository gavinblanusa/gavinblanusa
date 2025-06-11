"""Rank private companies based on available metrics.

This script loads ``companies.csv`` and calculates a composite score for
ranking. The score is a weighted combination of valuation, revenue, and
employee count. Metrics are normalized so that a company with a large
valuation does not overwhelm other factors. The script prints the top 100
companies to ``stdout``.
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


def compute_score(company: Dict[str, float], max_values: Dict[str, float]) -> float:
    """Compute weighted score for a company using normalized metrics."""
    score = 0.0
    for field, weight in WEIGHTS.items():
        max_v = max_values.get(field) or 1
        score += (company.get(field, 0) / max_v) * weight
    return score


def rank_companies(companies: List[Dict[str, float]]) -> (List[Dict[str, float]], Dict[str, float]):
    """Return companies sorted by composite score descending and max values."""
    if not companies:
        return [], {field: 1 for field in WEIGHTS}

    max_values = {
        field: max((c.get(field, 0) for c in companies), default=0) or 1
        for field in WEIGHTS
    }
    ranked = sorted(
        companies,
        key=lambda c: compute_score(c, max_values),
        reverse=True,
    )
    return ranked, max_values


if __name__ == "__main__":
    companies = load_companies()
    ranked, max_vals = rank_companies(companies)
    top_100 = ranked[:100]
    if not top_100:
        print("No company data available")
    for i, c in enumerate(top_100, start=1):
        score = compute_score(c, max_vals)
        print(f"{i}. {c['company']} - score: {score:.2f}")

