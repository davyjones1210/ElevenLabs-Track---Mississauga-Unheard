import csv
from collections import Counter, defaultdict
from pathlib import Path

from .data import read_csv, write_csv
from .intents import evaluate_audio_intents, evaluate_intents


def _as_int(value: str) -> int | None:
    value = value.strip().replace(",", "")
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def summarize_census(data_root: Path, output_dir: Path) -> None:
    derived = data_root / "01_people_census" / "derived"
    coverage = read_csv(derived / "language_coverage.csv")
    write_csv(output_dir / "language_coverage.csv", coverage)
    geo_rows = read_csv(derived / "geo_language_long.csv")

    geography: dict[tuple[str, str], dict] = {}
    for row in geo_rows:
        key = (row["geo_level"], row["geo"])
        entry = geography.setdefault(
            key,
            {
                "geo_level": row["geo_level"],
                "geo": row["geo"],
                "population_language_base": row["population_language_base"],
                "knows_neither_english_nor_french": row[
                    "knows_neither_english_nor_french"
                ],
                "pct_knows_neither_english_nor_french": row[
                    "pct_knows_neither_english_nor_french"
                ],
                "recent_immigrants_2016_2021": row["recent_immigrants_2016_2021"],
                "top14_nonofficial_home_language_speakers": 0,
            },
        )
        entry["top14_nonofficial_home_language_speakers"] += _as_int(
            row["home_speakers"]
        ) or 0
    write_csv(
        output_dir / "population_by_geography.csv",
        sorted(geography.values(), key=lambda row: (row["geo_level"], row["geo"])),
    )


def summarize_toronto_311(data_root: Path, output_dir: Path) -> None:
    source = data_root / "05_city_311_requests" / "toronto_311_requests_2025.csv"
    type_counts: Counter[tuple[str, str, str]] = Counter()
    ward_counts: Counter[tuple[str, str]] = Counter()
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            request_type = row.get("service_request_type", "").strip()
            division = row.get("division", "").strip()
            ward = row.get("ward", "").strip()
            if request_type:
                type_counts[(division, request_type, ward)] += 1
                ward_counts[(ward, division)] += 1
    types_by_division: Counter[tuple[str, str]] = Counter()
    for (division, request_type, _), count in type_counts.items():
        types_by_division[(division, request_type)] += count
    write_csv(
        output_dir / "toronto_311_request_types.csv",
        [
            {"division": division, "service_request_type": request_type, "requests_2025": count}
            for (division, request_type), count in types_by_division.most_common()
        ],
    )
    write_csv(
        output_dir / "toronto_311_ward_divisions.csv",
        [
            {"ward": ward, "division": division, "requests_2025": count}
            for (ward, division), count in sorted(ward_counts.items())
        ],
    )


def summarize_mississauga_311(data_root: Path, output_dir: Path) -> None:
    source_dir = data_root / "05_city_311_requests"
    yearly: list[dict[str, str]] = []
    for year in (2017, 2018):
        source = source_dir / f"Mississauga_311_Call_Data_{year}.csv"
        totals = defaultdict(int)
        valid_days = 0
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                normalized = {key.strip().casefold(): value for key, value in row.items() if key}
                offered = _as_int(normalized.get("calls_offered", ""))
                answered = _as_int(normalized.get("calls_answered", ""))
                abandoned = _as_int(
                    normalized.get("calls_abandoned_under_svl", "")
                    or normalized.get("calls abandoned under svl", "")
                )
                if offered is None or answered is None:
                    continue
                valid_days += 1
                totals["calls_offered"] += offered
                totals["calls_answered"] += answered
                totals["calls_abandoned_under_svl"] += abandoned or 0
        yearly.append(
            {
                "year": str(year),
                "valid_business_days": str(valid_days),
                "calls_offered": str(totals["calls_offered"]),
                "calls_answered": str(totals["calls_answered"]),
                "calls_abandoned_under_svl": str(totals["calls_abandoned_under_svl"]),
                "answer_rate": (
                    f"{totals['calls_answered'] / totals['calls_offered']:.6f}"
                    if totals["calls_offered"]
                    else ""
                ),
            }
        )
    write_csv(output_dir / "mississauga_311_yearly_calls.csv", yearly)


def run_analysis(data_root: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summarize_census(data_root, output_dir)
    summarize_toronto_311(data_root, output_dir)
    summarize_mississauga_311(data_root, output_dir)
    evaluate_intents(data_root, output_dir)
    if (output_dir / "asr_benchmark.csv").is_file():
        evaluate_audio_intents(data_root, output_dir)
