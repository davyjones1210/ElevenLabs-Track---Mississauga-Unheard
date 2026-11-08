from collections import defaultdict
from pathlib import Path

from .data import read_csv, write_csv


def build_unheard_index(data_root: Path, output_dir: Path) -> list[dict[str, str]]:
    asr_path = output_dir / "asr_benchmark.csv"
    intent_path = output_dir / "intent_evaluation.csv"
    paired_fleurs_path = output_dir / "paired_fleurs_summary.csv"
    asr_by_language: dict[str, list[float]] = defaultdict(list)
    asr_sample_counts: dict[str, int] = defaultdict(int)
    if asr_path.exists():
        for row in read_csv(asr_path):
            if row.get("dataset") != "fleurs":
                continue
            try:
                language = row["language"].casefold()
                asr_by_language[language].append(float(row["cer"]))
                asr_sample_counts[language] += 1
            except (ValueError, KeyError):
                continue
    elif paired_fleurs_path.exists():
        for row in read_csv(paired_fleurs_path):
            try:
                language = row["language"].casefold()
                asr_by_language[language].append(float(row["cer"]))
                asr_sample_counts[language] += int(row["samples"])
            except (ValueError, KeyError):
                continue

    audio_intent_path = output_dir / "audio_intent_evaluation.csv"
    audio_intent_rows = (
        read_csv(audio_intent_path) if audio_intent_path.exists() else []
    )
    has_audio_intent_results = any(
        row.get("status", "").startswith("audio transcript")
        for row in audio_intent_rows
    )
    intent_totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    intent_source: dict[str, str] = {}
    if has_audio_intent_results:
        source_path = audio_intent_path
        intent_rows = audio_intent_rows
    else:
        source_path = intent_path
        intent_rows = read_csv(intent_path) if intent_path.exists() else []
    if intent_rows:
        for row in intent_rows:
            valid_status = (
                row.get("status", "").startswith("audio transcript")
                if source_path == audio_intent_path
                else row.get("status") == "ok"
            )
            if not valid_status:
                continue
            try:
                samples = int(row["samples"])
                correct = int(row["correct"])
            except (ValueError, KeyError):
                continue
            values = intent_totals[row["language"].casefold()]
            values[0] += samples
            values[1] += samples - correct
            intent_source[row["language"].casefold()] = (
                "audio_intent_error"
                if source_path == audio_intent_path
                else "text_intent_error"
            )

    language_risks: dict[str, tuple[float, str]] = {}
    language_sample_counts: dict[str, int] = {}
    for language in set(asr_by_language) | set(intent_totals):
        scores: list[tuple[float, str]] = []
        language_sample_counts[language] = asr_sample_counts.get(language, 0)
        if language in asr_by_language:
            mean_cer = sum(asr_by_language[language]) / len(asr_by_language[language])
            scores.append((min(max(mean_cer, 0.0), 1.0), "FLEURS_CER"))
        if language in intent_totals and intent_totals[language][0]:
            samples, errors = intent_totals[language]
            scores.append((errors / samples, intent_source[language]))
            language_sample_counts[language] += samples
        if scores:
            language_risks[language] = (
                sum(score for score, _ in scores) / len(scores),
                "+".join(name for _, name in scores),
            )

    geo_rows = read_csv(
        data_root / "01_people_census" / "derived" / "geo_language_long.csv"
    )
    totals: dict[tuple[str, str], dict] = {}
    for row in geo_rows:
        key = (row["geo_level"], row["geo"])
        result = totals.setdefault(
            key,
            {
                "geo_level": row["geo_level"],
                "geo": row["geo"],
                "population_language_base": int(float(row["population_language_base"])),
                "knows_neither_english_nor_french": int(
                    float(row["knows_neither_english_nor_french"])
                ),
                "pct_knows_neither_english_nor_french": row[
                    "pct_knows_neither_english_nor_french"
                ],
                "scored_home_speakers": 0,
                "weighted_error_count": 0.0,
                "benchmark_clip_count": 0,
                "scored_languages": set(),
                "risk_sources": set(),
            },
        )
        language = row["language"].casefold()
        if language not in language_risks:
            continue
        speakers = int(float(row["home_speakers"]))
        risk, source = language_risks[language]
        result["scored_home_speakers"] += speakers
        result["weighted_error_count"] += speakers * risk
        result["benchmark_clip_count"] += language_sample_counts[language]
        result["scored_languages"].add(row["language"])
        result["risk_sources"].add(source)

    output: list[dict[str, str]] = []
    for result in totals.values():
        scored = result["scored_home_speakers"]
        population = result["population_language_base"]
        output.append(
            {
                "geo_level": result["geo_level"],
                "geo": result["geo"],
                "population_language_base": str(population),
                "knows_neither_english_nor_french": str(
                    result["knows_neither_english_nor_french"]
                ),
                "pct_knows_neither_english_nor_french": result[
                    "pct_knows_neither_english_nor_french"
                ],
                "scored_home_speakers": str(scored),
                "benchmark_clip_count": str(result["benchmark_clip_count"]),
                "benchmark_coverage_pct": f"{100 * scored / population:.3f}" if population else "",
                "unheard_index": f"{100 * result['weighted_error_count'] / scored:.3f}"
                if scored
                else "",
                "weighted_error_count_proxy": f"{result['weighted_error_count']:.1f}"
                if scored
                else "",
                "scored_languages": ";".join(sorted(result["scored_languages"])),
                "risk_sources": ";".join(sorted(result["risk_sources"])),
                "status": "scored" if scored else "no matched benchmark evidence",
            }
        )
    output.sort(
        key=lambda row: (
            row["status"] != "scored",
            -float(row["unheard_index"] or 0),
            -float(row["benchmark_coverage_pct"] or 0),
        )
    )
    write_csv(output_dir / "unheard_index.csv", output)
    return output
