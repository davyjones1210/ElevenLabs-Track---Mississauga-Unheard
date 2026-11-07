import os
import hashlib
import statistics
from collections import defaultdict
from pathlib import Path

from .data import DATASET_DIRS, load_speech_rows, read_csv, write_csv
from .metrics import character_error_rate, word_error_rate


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
                with audio_path.open("rb") as audio_file:
                    response = client.speech_to_text.convert(
                        file=audio_file,
                        model_id="scribe_v2",
                    )
                transcript = response.text.strip()
                existing[(dataset, row["file"])] = {
                    "dataset": dataset,
                    "language": language,
                    "file": row["file"],
                    "reference": row["reference"],
                    "transcript": transcript,
                    "wer": f"{word_error_rate(row['reference'], transcript):.6f}",
                    "cer": f"{character_error_rate(row['reference'], transcript):.6f}",
                    "reference_label": row["label"],
                }
                write_csv(output_path, list(existing.values()))
    results = sorted(existing.values(), key=lambda row: (row["dataset"], row["language"], row["file"]))
    write_csv(output_path, results)
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
            }
            for (dataset, language), rows in sorted(grouped.items())
        ],
    )
    return results
