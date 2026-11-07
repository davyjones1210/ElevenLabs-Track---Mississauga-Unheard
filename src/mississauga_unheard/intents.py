from collections import Counter
from pathlib import Path

from .data import DATASET_DIRS, load_crosswalk, read_csv, write_csv


def _sklearn():
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
    except ImportError as exc:
        raise RuntimeError(
            "Intent evaluation requires scikit-learn. Install the project with "
            "`python -m pip install -e .`."
        ) from exc
    return TfidfVectorizer, LogisticRegression, train_test_split, make_pipeline


def _training_groups(data_root: Path) -> dict[str, list[dict[str, str]]]:
    locale_to_language, _ = load_crosswalk(data_root)
    groups: dict[str, list[dict[str, str]]] = {"minds14": [], "massive": []}
    for dataset in groups:
        folder = data_root / DATASET_DIRS[dataset]
        rows = read_csv(folder / "metadata.csv")
        for row in rows:
            if dataset == "minds14":
                language = locale_to_language.get(row["locale"].casefold(), row["language"])
                text, label = row["transcription"], row["intent"]
            else:
                language = row["language"]
                text, label = row["utterance"], row["scenario"]
            if text.strip() and label.strip():
                groups[dataset].append(
                    {"language": language, "text": text, "label": label, "file": row["file"]}
                )
    return groups


def evaluate_intents(data_root: Path, output_dir: Path) -> list[dict[str, str]]:
    TfidfVectorizer, LogisticRegression, train_test_split, make_pipeline = _sklearn()
    groups = _training_groups(data_root)
    evaluations: list[dict[str, str]] = []
    confusions: list[dict[str, str]] = []
    for dataset, rows in groups.items():
        languages = sorted({row["language"] for row in rows})
        for language in languages:
            subset = [row for row in rows if row["language"] == language]
            texts = [row["text"] for row in subset]
            labels = [row["label"] for row in subset]
            counts = Counter(labels)
            if len(counts) < 2 or min(counts.values()) < 2:
                evaluations.append(
                    {
                        "dataset": dataset,
                        "language": language,
                        "label_type": "intent" if dataset == "minds14" else "scenario",
                        "samples": str(len(subset)),
                        "correct": "",
                        "accuracy": "",
                        "status": "skipped: at least two examples per label are required",
                    }
                )
                continue

            indices = list(range(len(texts)))
            train_indices, test_indices = train_test_split(
                indices, test_size=0.25, random_state=42, stratify=labels
            )
            model = make_pipeline(
                TfidfVectorizer(
                    analyzer="char",
                    ngram_range=(2, 5),
                    min_df=1,
                    max_features=100_000,
                    sublinear_tf=True,
                ),
                LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
            )
            model.fit([texts[i] for i in train_indices], [labels[i] for i in train_indices])
            predictions = model.predict([texts[i] for i in test_indices])
            correct = sum(predicted == labels[i] for i, predicted in zip(test_indices, predictions))
            evaluations.append(
                {
                    "dataset": dataset,
                    "language": language,
                    "label_type": "intent" if dataset == "minds14" else "scenario",
                    "samples": str(len(test_indices)),
                    "correct": str(correct),
                    "accuracy": f"{correct / len(test_indices):.6f}",
                    "status": "ok",
                }
            )
            for i, predicted in zip(test_indices, predictions):
                confusions.append(
                    {
                        "dataset": dataset,
                        "language": language,
                        "true_label": labels[i],
                        "predicted_label": predicted,
                    }
                )

    write_csv(output_dir / "intent_evaluation.csv", evaluations)
    if confusions:
        confusion_counts = Counter(
            (
                row["dataset"],
                row["language"],
                row["true_label"],
                row["predicted_label"],
            )
            for row in confusions
        )
        write_csv(
            output_dir / "intent_confusions.csv",
            [
                {
                    "dataset": dataset,
                    "language": language,
                    "true_label": true_label,
                    "predicted_label": predicted_label,
                    "count": count,
                }
                for (dataset, language, true_label, predicted_label), count
                in sorted(confusion_counts.items())
            ],
        )
    return evaluations


def evaluate_audio_intents(
    data_root: Path, output_dir: Path
) -> list[dict[str, str]]:
    asr_path = output_dir / "asr_benchmark.csv"
    if not asr_path.is_file():
        return []

    TfidfVectorizer, LogisticRegression, _, make_pipeline = _sklearn()
    training = _training_groups(data_root)
    test_rows = [
        row
        for row in read_csv(asr_path)
        if row.get("dataset") in {"minds14", "massive"} and row.get("transcript", "").strip()
    ]
    by_group: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in test_rows:
        by_group.setdefault((row["dataset"], row["language"]), []).append(row)

    predictions: list[dict[str, str]] = []
    evaluation: list[dict[str, str]] = []
    for (dataset, language), samples in sorted(by_group.items()):
        train_rows = [
            row
            for row in training[dataset]
            if row["language"].casefold() == language.casefold()
            and row["file"] not in {sample["file"] for sample in samples}
        ]
        if not train_rows or len({row["label"] for row in train_rows}) < 2:
            evaluation.append(
                {
                    "dataset": dataset,
                    "language": language,
                    "label_type": "intent" if dataset == "minds14" else "scenario",
                    "samples": str(len(samples)),
                    "correct": "",
                    "accuracy": "",
                    "status": "skipped: insufficient labeled training examples",
                }
            )
            continue

        model = make_pipeline(
            TfidfVectorizer(
                analyzer="char",
                ngram_range=(2, 5),
                min_df=1,
                max_features=100_000,
                sublinear_tf=True,
            ),
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        )
        model.fit(
            [row["text"] for row in train_rows],
            [row["label"] for row in train_rows],
        )
        texts = [row["transcript"] for row in samples]
        predicted_labels = model.predict(texts)
        correct = 0
        for sample, prediction in zip(samples, predicted_labels):
            is_correct = prediction == sample["reference_label"]
            correct += is_correct
            predictions.append(
                {
                    "dataset": dataset,
                    "language": language,
                    "file": sample["file"],
                    "true_label": sample["reference_label"],
                    "predicted_label": prediction,
                    "correct": str(is_correct).lower(),
                    "asr_transcript": sample["transcript"],
                    "reference_transcript": sample["reference"],
                }
            )
        evaluation.append(
            {
                "dataset": dataset,
                "language": language,
                "label_type": "intent" if dataset == "minds14" else "scenario",
                "samples": str(len(samples)),
                "correct": str(correct),
                "accuracy": f"{correct / len(samples):.6f}",
                "status": "audio transcript; exploratory sample",
            }
        )

    write_csv(output_dir / "audio_intent_evaluation.csv", evaluation)
    write_csv(output_dir / "audio_intent_predictions.csv", predictions)
    confusion_counts = Counter(
        (
            row["dataset"],
            row["language"],
            row["true_label"],
            row["predicted_label"],
        )
        for row in predictions
    )
    write_csv(
        output_dir / "audio_intent_confusions.csv",
        [
            {
                "dataset": dataset,
                "language": language,
                "true_label": true_label,
                "predicted_label": predicted_label,
                "count": count,
            }
            for (dataset, language, true_label, predicted_label), count
            in sorted(confusion_counts.items())
        ],
    )
    return evaluation
