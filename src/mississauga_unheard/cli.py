import argparse
import sys
from pathlib import Path

from .analysis import run_analysis
from .benchmark import run_benchmark, run_paired_fleurs_benchmark
from .data import DATASET_DIRS, resolve_data_root
from .index import build_unheard_index
from .intents import evaluate_audio_intents
from .prototype import synthesize_callback


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace containing the supplied data folder (default: current directory).",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))


def _benchmark(parser: argparse.ArgumentParser) -> None:
    _common(parser)
    parser.add_argument(
        "--paired-fleurs",
        action="store_true",
        help="Evaluate one shared FLEURS sentence ID across every language, reusing cached clips.",
    )
    parser.add_argument(
        "--datasets",
        default="fleurs,accent",
        help="Comma-separated datasets: fleurs, accent, minds14, massive.",
    )
    parser.add_argument(
        "--per-group",
        type=int,
        default=1,
        help="Maximum new clips per dataset/language; each clip makes a paid API request.",
    )
    parser.add_argument(
        "--languages",
        default="",
        help="Optional comma-separated canonical language names, e.g. Urdu,Arabic.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mississauga-unheard",
        description="Reproducible census, speech, routing, and 311 analysis workflow.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Run offline census, 311, and intent baselines.")
    _common(analyze)

    benchmark = subparsers.add_parser("benchmark", help="Transcribe a small audio sample with Scribe.")
    _benchmark(benchmark)

    index = subparsers.add_parser("index", help="Build geography risk scores from available evidence.")
    _common(index)

    prototype = subparsers.add_parser(
        "prototype", help="Generate a multilingual 311 callback prompt with ElevenLabs TTS."
    )
    prototype.add_argument("--workspace", type=Path, default=Path.cwd())
    prototype.add_argument("--text", required=True, help="Callback text already translated by a person.")
    prototype.add_argument("--voice-id", required=True, help="Voice ID from your ElevenLabs voice library.")
    prototype.add_argument("--output", type=Path, default=Path("outputs/311_callback.mp3"))
    prototype.add_argument("--model-id", default="eleven_multilingual_v2")

    run = subparsers.add_parser("run", help="Run offline analysis, optional sample ASR, then the index.")
    _common(run)
    run.add_argument(
        "--with-elevenlabs",
        action="store_true",
        help="Transcribe sample audio (paid API usage; one new clip per language/dataset).",
    )
    run.add_argument("--datasets", default="fleurs,accent")
    run.add_argument("--per-group", type=int, default=1)
    run.add_argument("--languages", default="")
    return parser


def _paths(workspace: Path, output_dir: Path) -> tuple[Path, Path]:
    data_root = resolve_data_root(workspace)
    resolved_output = output_dir if output_dir.is_absolute() else workspace / output_dir
    resolved_output.mkdir(parents=True, exist_ok=True)
    return data_root, resolved_output


def _parse_datasets(value: str) -> list[str]:
    datasets = [item.strip().casefold() for item in value.split(",") if item.strip()]
    invalid = sorted(set(datasets) - set(DATASET_DIRS))
    if invalid:
        raise ValueError(f"Unknown dataset(s): {', '.join(invalid)}.")
    if not datasets:
        raise ValueError("Select at least one dataset.")
    return datasets


def _parse_languages(value: str) -> set[str] | None:
    languages = {item.strip().casefold() for item in value.split(",") if item.strip()}
    return languages or None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "prototype":
            output = args.output if args.output.is_absolute() else args.workspace / args.output
            result = synthesize_callback(
                args.workspace.resolve(), args.text, args.voice_id, output, args.model_id
            )
            print(f"Generated callback audio: {result}")
            return 0

        data_root, output_dir = _paths(args.workspace.resolve(), args.output_dir)
        if args.command == "analyze":
            run_analysis(data_root, output_dir)
            print(f"Offline analysis written to {output_dir}")
        elif args.command == "benchmark":
            if args.paired_fleurs:
                results = run_paired_fleurs_benchmark(
                    data_root,
                    output_dir,
                    args.workspace.resolve(),
                )
                print(
                    f"Matched FLEURS results ({len(results)} languages) written to "
                    f"{output_dir / 'paired_fleurs_summary.csv'}"
                )
                return 0
            results = run_benchmark(
                data_root,
                output_dir,
                args.workspace.resolve(),
                _parse_datasets(args.datasets),
                args.per_group,
                _parse_languages(args.languages),
            )
            evaluate_audio_intents(data_root, output_dir)
            print(f"ASR results ({len(results)} clips) written to {output_dir / 'asr_benchmark.csv'}")
        elif args.command == "index":
            evaluate_audio_intents(data_root, output_dir)
            rows = build_unheard_index(data_root, output_dir)
            print(f"Geography index ({len(rows)} areas) written to {output_dir / 'unheard_index.csv'}")
        elif args.command == "run":
            run_analysis(data_root, output_dir)
            if args.with_elevenlabs:
                run_benchmark(
                    data_root,
                    output_dir,
                    args.workspace.resolve(),
                    _parse_datasets(args.datasets),
                    args.per_group,
                    _parse_languages(args.languages),
                )
            evaluate_audio_intents(data_root, output_dir)
            rows = build_unheard_index(data_root, output_dir)
            print(f"Workflow complete: {output_dir} ({len(rows)} geography rows)")
        return 0
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
