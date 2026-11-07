# Mississauga Unheard Python workflow

This package turns the challenge into repeatable, staged commands. It separates reference-text baselines from measured speech-to-text and audio-intent results, uses the corrected Ward 10 census data through the supplied derived table, and does not infer a benchmark score for languages with no matching audio evidence.

## Setup

From the project root:

```powershell
python -m pip install -e ".[elevenlabs]"
```

The ElevenLabs coding-agent onboarding command from the official quickstart is:

```powershell
npx -y @elevenlabs/cli@latest onboard init
```

It requires Node.js and may open a browser for sign-in/authorization. The key should remain in the local `.env` file and is ignored by `.gitignore`. If you already have a key, set it for the current PowerShell session instead:

```powershell
$env:ELEVENLABS_API_KEY = "your-key"
```

No key is required for offline analysis. Never add a real key to source control or include it in analysis outputs.

## Run the workflow

Run all offline summaries and the intent baseline first:

```powershell
python -m mississauga_unheard analyze --workspace . --output-dir outputs
```

This reads the demographic and 311 tables, computes an intent-routing text baseline on held-out utterances, and writes:

- `outputs/language_coverage.csv`
- `outputs/population_by_geography.csv`
- `outputs/toronto_311_request_types.csv`
- `outputs/toronto_311_ward_divisions.csv`
- `outputs/mississauga_311_yearly_calls.csv`
- `outputs/intent_evaluation.csv`
- `outputs/intent_confusions.csv`

Then benchmark a deliberately small sample using ElevenLabs Scribe v2. Each request is a paid clip; `--per-group 1` makes one deterministic selection for each dataset/language group:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs `
  --datasets fleurs,accent,minds14,massive --per-group 1
```

For a controlled FLEURS comparison, transcribe the same prompt in every language. This matched sentence ID is cached separately and reuses matching clips already benchmarked:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs --paired-fleurs
```

Completed clips are retained in `outputs/asr_benchmark.csv` and skipped on reruns. Group summaries are written to `outputs/asr_summary.csv`; matched results are in `outputs/paired_fleurs_summary.csv` and `outputs/paired_fleurs_benchmark.csv`. Remove or move those outputs only if you intentionally want to retranscribe the clips.

The benchmark defaults to auto language detection; it does not pass a language hint that could make the comparison less neutral. FLEURS references are the supplied normalized text; the accent archive uses its shared elicitation paragraph. WER and CER are normalized consistently and reported together; use CER when word boundaries differ, especially for Chinese and Indic scripts. The matched prompt controls content but not speaker identity or dialect, and FLEURS has no speaker IDs. These measurements are small-sample diagnostics, not proof of citywide accuracy.

When Scribe results for MInDS-14 or Speech-MASSIVE are available, analysis automatically uses each ASR transcript to predict its labeled intent/scenario, training on the other reference transcripts for that dataset/language. Results and specific confusions are written to `outputs/audio_intent_evaluation.csv`, `outputs/audio_intent_predictions.csv`, and `outputs/audio_intent_confusions.csv`. The text-only baseline remains separate.

After both offline analysis and any desired ASR run, generate the geographic index:

```powershell
python -m mississauga_unheard index --workspace . --output-dir outputs
```

Or run them together. By default this does not call ElevenLabs:

```powershell
python -m mississauga_unheard run --workspace . --output-dir outputs
```

To explicitly opt in to sample API usage:

```powershell
python -m mississauga_unheard run --workspace . --output-dir outputs `
  --with-elevenlabs --datasets fleurs --per-group 1 --languages Urdu,Arabic
```

## Index interpretation

`outputs/unheard_index.csv` has one row per ward and neighbourhood. Its `unheard_index` is an equally weighted mean of available FLEURS CER and audio-intent error rates, weighted across the area's measured home-language speaker counts. If no audio-intent evaluation exists, it uses the held-out text-intent baseline instead. `benchmark_coverage_pct` is the share of the area's language-base population covered by those measured home-language groups. The weighted-error count is a pilot proxy, not a count of known misunderstood residents. `knows_neither_english_nor_french` is shown separately because the census categories overlap with home-language populations and should not be added as independent people.

This is a prioritization proxy, not a probability that a particular resident will be misunderstood. The accent archive is reported for English-accent analysis, but is not mapped directly onto a home-language group. Audio-intent results are predictions from a simple benchmark classifier, not a production 311 agent; MInDS-14 is banking speech while Speech-MASSIVE is voice-assistant speech. The absent request languages remain unscored rather than imputed.

Toronto request categories are context only, not Mississauga service-request counts. The Mississauga 2017-2018 call summary uses offered/answered call totals, not language or request type. Check the dataset's `LICENSES.md` before publishing results; Speech Accent Archive and Speech-MASSIVE are non-commercial and ShareAlike.

## ElevenLabs callback prototype

Provide translated and reviewed text in the target language; this command synthesizes it but does not translate or make city-service claims:

```powershell
python -m mississauga_unheard prototype --workspace . `
  --voice-id hpp4J3VqNfWAUOO0d1Us `
  --text "Your translated callback message goes here." `
  --output outputs/311_callback.mp3
```

This voice ID was used for the English and Spanish demonstration clips. The Spanish audio is `outputs/311_callback_es.mp3`; its sample translation needs fluent-speaker review. This generated audio demonstrates a callback, not a deployed agent or validated city-service translation.
