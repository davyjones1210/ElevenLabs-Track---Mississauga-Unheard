import csv
from pathlib import Path


DATASET_DIRS = {
    "fleurs": "02_speech_home_languages_FLEURS",
    "accent": "03_accented_english_SpeechAccentArchive",
    "minds14": "04_spoken_requests/minds14",
    "massive": "04_spoken_requests/speech_massive",
}


def resolve_data_root(path: Path) -> Path:
    path = path.resolve()
    candidates = [path]
    if path.is_dir():
        candidates.extend(child for child in path.iterdir() if child.is_dir())
    for candidate in candidates:
        if (candidate / "01_people_census" / "derived" / "language_coverage.csv").is_file():
            return candidate
    raise FileNotFoundError(
        f"Could not find the supplied dataset under {path}; expected "
        "01_people_census/derived/language_coverage.csv."
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_crosswalk(data_root: Path) -> tuple[dict[str, str], dict[str, str]]:
    rows = read_csv(data_root / "language_crosswalk.csv")
    locale_to_language: dict[str, str] = {}
    code_to_language: dict[str, str] = {}
    for row in rows:
        language = row["language"]
        for key in ("minds14_locale", "speech_massive_locale"):
            locale = row.get(key, "").strip()
            if locale:
                locale_to_language[locale.casefold()] = language
        code = row.get("iso639_1", "").strip()
        if code:
            code_to_language[code.casefold()] = language
    return locale_to_language, code_to_language


def load_speech_rows(data_root: Path, dataset: str) -> list[dict[str, str]]:
    if dataset not in DATASET_DIRS:
        raise ValueError(f"Unknown dataset {dataset!r}; choose from {', '.join(DATASET_DIRS)}.")

    folder = data_root / DATASET_DIRS[dataset]
    metadata = read_csv(folder / "metadata.csv")
    if dataset == "accent":
        reference = (folder / "elicitation_paragraph.txt").read_text(encoding="utf-8").strip()
        for row in metadata:
            row["reference"] = reference
            row["group_language"] = row["language"]
            row["label"] = ""
    elif dataset == "fleurs":
        for row in metadata:
            row["reference"] = row["transcription"]
            row["group_language"] = row["language"]
            row["label"] = ""
    elif dataset == "minds14":
        locale_to_language, _ = load_crosswalk(data_root)
        for row in metadata:
            row["reference"] = row["transcription"]
            row["group_language"] = locale_to_language.get(
                row["locale"].casefold(), row["language"]
            )
            row["label"] = row["intent"]
    else:
        for row in metadata:
            row["reference"] = row["utterance"]
            row["group_language"] = row["language"]
            row["label"] = row["scenario"]
    return metadata
