"""Rank private companies based on available metrics.

This script loads ``companies.csv`` and calculates a composite score for
ranking. The score is a weighted combination of valuation, revenue, and
employee count. Metrics are standardized using z-scores so that a
company with an extreme value in one metric does not completely dominate
the ranking. The script prints the top 100 companies to ``stdout``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean, pstdev
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


def compute_stats(companies: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Return mean and standard deviation for each weighted metric."""
    stats: Dict[str, Dict[str, float]] = {}
    for field in WEIGHTS:
        values = [c.get(field, 0.0) for c in companies]
        stats[field] = {
            "mean": mean(values) if values else 0.0,
            "std": pstdev(values) if len(values) > 1 else 1.0,
        }
        if stats[field]["std"] == 0:
            stats[field]["std"] = 1.0
    return stats


def compute_score(company: Dict[str, float], stats: Dict[str, Dict[str, float]]) -> float:
    """Compute weighted score for a company using z-score normalization."""
    score = 0.0
    for field, weight in WEIGHTS.items():
        field_stats = stats.get(field, {"mean": 0.0, "std": 1.0})
        normalized = (company.get(field, 0.0) - field_stats["mean"]) / field_stats["std"]
        score += normalized * weight
    return score


def rank_companies(companies: List[Dict[str, float]]) -> (List[Dict[str, float]], Dict[str, Dict[str, float]]):
    """Return companies sorted by composite score descending and stats."""
    if not companies:
        return [], {field: {"mean": 0.0, "std": 1.0} for field in WEIGHTS}

    stats = compute_stats(companies)
    ranked = sorted(
        companies,
        key=lambda c: compute_score(c, stats),
        reverse=True,
    )
    return ranked, stats


if __name__ == "__main__":
    companies = load_companies()
    ranked, stats = rank_companies(companies)
    top_100 = ranked[:100]
    if not top_100:
        print("No company data available")
    for i, c in enumerate(top_100, start=1):
        score = compute_score(c, stats)
        print(f"{i}. {c['company']} - score: {score:.2f}")

