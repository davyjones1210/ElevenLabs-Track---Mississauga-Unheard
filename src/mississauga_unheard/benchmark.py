import os
import hashlib
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from .data import DATASET_DIRS, load_speech_rows, read_csv, write_csv
from .metrics import character_error_rate, word_error_rate


def _result_row(dataset: str, language: str, row: dict, response) -> dict[str, str]:
    transcript = response.text.strip()
    return {
        "dataset": dataset,
        "language": language,
        "file": row["file"],
        "fleurs_id": row.get("fleurs_id", ""),
        "reference_label": row["label"],
        "reference": row["reference"],
        "transcript": transcript,
        "wer": f"{word_error_rate(row['reference'], transcript):.6f}",
        "cer": f"{character_error_rate(row['reference'], transcript):.6f}",
        "detected_language": str(getattr(response, "language_code", "") or ""),
        "language_probability": str(
            getattr(response, "language_probability", "") or ""
        ),
        "speaker_gender": row.get("gender") or row.get("speaker_sex") or "",
        "speaker_age": row.get("age") or row.get("speaker_age") or "",
        "native_language": row.get("native_language")
        or row.get("speaker_first_language")
        or "",
        "birth_country": row.get("birth_country")
        or row.get("speaker_country_of_birth")
        or "",
        "variety_note": row.get("variety_note", ""),
    }


def _transcribe(client, audio_path: Path):
    from elevenlabs.core.api_error import ApiError

    try:
        with audio_path.open("rb") as audio_file:
            return client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v2",
            )
    except ApiError as exc:
        raise RuntimeError(
            f"ElevenLabs Scribe request failed (HTTP {exc.status_code}): {exc.body}"
        ) from exc


def _write_asr_summary(output_dir: Path, results: list[dict[str, str]]) -> None:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in results:
        grouped[(row["dataset"], row["language"])].append(row)
    write_csv(
        output_dir / "asr_summary.csv",
        [
            {
                "dataset": dataset,
                "language": language,
                "samples": str(len(rows)),
                "mean_wer": f"{statistics.mean(float(row['wer']) for row in rows):.6f}",
                "mean_cer": f"{statistics.mean(float(row['cer']) for row in rows):.6f}",
                "gender_counts": ";".join(
                    f"{gender}:{count}"
                    for gender, count in sorted(
                        Counter(row.get("speaker_gender", "") or "unknown" for row in rows).items()
                    )
                ),
                "detected_languages": ";".join(
                    sorted(
                        {
                            row["detected_language"]
                            for row in rows
                            if row.get("detected_language")
                        }
                    )
                ),
                "variety_notes": ";".join(
                    sorted({row["variety_note"] for row in rows if row.get("variety_note")})
                ),
            }
            for (dataset, language), rows in sorted(grouped.items())
        ],
    )


def _load_api_key(workspace: Path) -> str:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError(
            "The ElevenLabs optional dependencies are not installed. Run "
            "`python -m pip install -e \".[elevenlabs]\"`."
        ) from exc

    load_dotenv(workspace / ".env")
    value = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if value:
        return value
    raise RuntimeError(
        "ELEVENLABS_API_KEY was not found. Run the ElevenLabs onboarding flow or set it "
        "in the environment; the key is never written to benchmark outputs."
    )


def _client(workspace: Path):
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError as exc:
        raise RuntimeError(
            "The ElevenLabs Python SDK is not installed. Run "
            "`python -m pip install -e \".[elevenlabs]\"`."
        ) from exc
    return ElevenLabs(api_key=_load_api_key(workspace))


def run_benchmark(
    data_root: Path,
    output_dir: Path,
    workspace: Path,
    datasets: list[str],
    per_group: int,
    languages: set[str] | None = None,
) -> list[dict[str, str]]:
    if per_group < 1:
        raise ValueError("--per-group must be at least 1.")
    client = _client(workspace)
    output_path = output_dir / "asr_benchmark.csv"
    existing: dict[tuple[str, str], dict[str, str]] = {}
    if output_path.exists():
        existing = {
            (row["dataset"], row["file"]): row for row in read_csv(output_path)
        }

    for dataset in datasets:
        if dataset not in DATASET_DIRS:
            raise ValueError(f"Unknown dataset {dataset!r}.")
        folder = data_root / DATASET_DIRS[dataset]
        by_language: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in load_speech_rows(data_root, dataset):
            language = row["group_language"]
            if languages and language.casefold() not in languages:
                continue
            if (dataset, row["file"]) not in existing:
                by_language[language].append(row)

        for language, rows in sorted(by_language.items()):
            sample = sorted(
                rows,
                key=lambda row: hashlib.sha256(
                    f"{dataset}:{language}:{row['file']}:42".encode("utf-8")
                ).digest(),
            )[:per_group]
            for row in sample:
                audio_path = (folder / row["file"]).resolve()
                if not audio_path.is_relative_to(folder.resolve()):
                    raise ValueError(f"Audio path escapes dataset directory: {row['file']}")
                if not audio_path.is_file():
                    raise FileNotFoundError(audio_path)
                response = _transcribe(client, audio_path)
                existing[(dataset, row["file"])] = _result_row(
                    dataset, language, row, response
                )
                write_csv(output_path, list(existing.values()))
    results = sorted(existing.values(), key=lambda row: (row["dataset"], row["language"], row["file"]))
    write_csv(output_path, results)
    _write_asr_summary(output_dir, results)
    return results


def run_paired_fleurs_benchmark(
    data_root: Path,
    output_dir: Path,
    workspace: Path,
    fleurs_id: str = "1589",
) -> list[dict[str, str]]:
    client = _client(workspace)
    dataset = "fleurs"
    folder = data_root / DATASET_DIRS[dataset]
    paired_rows = [
        row
        for row in load_speech_rows(data_root, dataset)
        if row.get("fleurs_id") == fleurs_id
    ]
    languages = {row["group_language"] for row in paired_rows}
    expected_languages = {
        row["group_language"] for row in load_speech_rows(data_root, dataset)
    }
    if not paired_rows or languages != expected_languages:
        raise ValueError(
            f"FLEURS sentence {fleurs_id!r} is not available in every language group."
        )

    cache_path = output_dir / "asr_benchmark.csv"
    cache = {
        (row["dataset"], row["file"]): row
        for row in read_csv(cache_path)
    } if cache_path.exists() else {}
    paired: list[dict[str, str]] = []
    for row in sorted(paired_rows, key=lambda item: item["group_language"]):
        key = (dataset, row["file"])
        if key in cache:
            result = dict(cache[key])
            result["fleurs_id"] = fleurs_id
        else:
            audio_path = (folder / row["file"]).resolve()
            if not audio_path.is_relative_to(folder.resolve()):
                raise ValueError(f"Audio path escapes dataset directory: {row['file']}")
            if not audio_path.is_file():
                raise FileNotFoundError(audio_path)
            response = _transcribe(client, audio_path)
            result = _result_row(dataset, row["group_language"], row, response)
            cache[key] = result
            write_csv(cache_path, list(cache.values()))
        paired.append(result)

    paired.sort(key=lambda item: item["language"])
    write_csv(output_dir / "paired_fleurs_benchmark.csv", paired)
    grouped = defaultdict(list)
    for row in paired:
        grouped[row["language"]].append(row)
    write_csv(
        output_dir / "paired_fleurs_summary.csv",
        [
            {
                "fleurs_id": fleurs_id,
                "language": language,
                "samples": str(len(rows)),
                "wer": f"{statistics.mean(float(row['wer']) for row in rows):.6f}",
                "cer": f"{statistics.mean(float(row['cer']) for row in rows):.6f}",
                "gender": rows[0].get("speaker_gender", ""),
                "variety_note": rows[0].get("variety_note", ""),
                "detected_language": rows[0].get("detected_language", ""),
            }
            for language, rows in sorted(grouped.items())
        ],
    )
    _write_asr_summary(output_dir, sorted(cache.values(), key=lambda item: (item["dataset"], item["language"], item["file"])))
    return paired
