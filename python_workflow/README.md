# Mississauga Unheard Python workflow

This package turns the challenge into repeatable, staged commands. It keeps reference-text intent classification separate from speech-to-text performance, uses the corrected Ward 10 census file through the supplied derived data, and does not infer a benchmark score for languages with no matching audio evidence.

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

Then benchmark a deliberately small sample using ElevenLabs Scribe v2:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs `
  --datasets fleurs,accent --per-group 1 --languages Urdu,Arabic
```

Each selected clip is a separate API request and may incur credits. `--per-group` limits new clips per dataset and language; completed clips are retained in `outputs/asr_benchmark.csv` and skipped on reruns. Group summaries are written to `outputs/asr_summary.csv`. Remove or move that output only if you intentionally want to retranscribe those clips.

The benchmark defaults to auto language detection; it does not pass a language hint that could make the comparison less neutral. FLEURS references are the supplied normalized text; the accent archive uses its shared elicitation paragraph. WER and CER are normalized consistently and reported together. These measurements are small-sample diagnostics, not proof of citywide accuracy.

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

`outputs/unheard_index.csv` has one row per ward and neighbourhood. Its `unheard_index` is an equally weighted mean of the available clipped FLEURS WER and held-out text-intent error rates, weighted across the area's measured home-language speaker counts. `benchmark_coverage_pct` is the share of the area's language-base population covered by those measured home-language groups. `knows_neither_english_nor_french` is shown separately because the census categories overlap with home-language populations and should not be added as independent people.

This is a prioritization proxy, not a probability that a particular resident will be misunderstood. The accent archive is reported for English-accent analysis, but is not mapped directly onto a home-language group. Request intent results use text utterances (not predictions from a production 311 agent), and MInDS-14 is banking speech while Speech-MASSIVE is voice-assistant speech. The absent request languages remain unscored rather than imputed.

Toronto request categories are context only, not Mississauga service-request counts. The Mississauga 2017-2018 call summary uses offered/answered call totals, not language or request type. Check the dataset's `LICENSES.md` before publishing results; Speech Accent Archive and Speech-MASSIVE are non-commercial and ShareAlike.

## ElevenLabs callback prototype

Provide translated and reviewed text in the target language; this command synthesizes it but does not translate or make city-service claims:

```powershell
python -m mississauga_unheard prototype --workspace . `
  --voice-id YOUR_REAL_VOICE_ID `
  --text "Your translated callback message goes here." `
  --output outputs/311_callback.mp3
```

Replace `YOUR_REAL_VOICE_ID` with a voice ID from your ElevenLabs Voices page; the placeholder is not a valid voice ID. A `voice_not_found` response means the ID is invalid or unavailable to the account/API key. The generated MP3 is a demonstration of a callback in the caller's language, not a deployed agent or a validated translation. Use a voice permitted for this purpose and review the message with a fluent speaker before presenting it as service guidance.
