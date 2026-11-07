# Mississauga Unheard — project workflow

This project analyzes the supplied Mississauga census, speech, and 311 data, and includes an optional ElevenLabs prototype for multilingual callback audio.

## Install

From the project directory, in PowerShell:

```powershell
python -m pip install -e ".[elevenlabs]"
```

The ElevenLabs key is kept in the local, gitignored `.env` file. Do not copy it into source files, command output, or reports. The SDK loads it through `python-dotenv`.

## Run the analysis

Offline analysis does not call ElevenLabs:

```powershell
python -m mississauga_unheard analyze --workspace . --output-dir outputs
python -m mississauga_unheard index --workspace . --output-dir outputs
```

Or run the workflow in one command:

```powershell
python -m mississauga_unheard run --workspace . --output-dir outputs
```

This creates census coverage and geography summaries, Toronto 311 service-type summaries, Mississauga 311 annual call totals, held-out text-intent baselines, confusion counts, and the geography-level `unheard_index.csv`.

The index is a prioritization proxy rather than a resident-level probability. It reports the population coverage and evidence sources alongside each score. Intent evaluation uses text transcripts and labeled scenarios; it does not claim to evaluate a deployed 311 agent.

## Challenge report

### 1. Understood? Speech-to-text by language and accent

The workflow is set up to score FLEURS home-language speech and Speech Accent Archive English-accent speech with WER and CER against the provided references. The accent archive speakers read the same paragraph, so results can be compared across first-language groups. FLEURS has small, gender-imbalanced speaker samples (Arabic, Punjabi, and Urdu clips are female; Portuguese, Tagalog, and Vietnamese clips are male), so a measured difference cannot automatically be attributed to language rather than speaker or dialect.

**Current finding status: pending.** No Scribe benchmark is in `outputs/asr_benchmark.csv` yet, so this project does not currently have measured STT error rates, a ranking of the least-understood groups, or evidence explaining which errors are most common. Run the optional benchmark before making those claims. Inspect transcripts and sample counts alongside WER/CER; treat small groups as exploratory, not representative.

### 2. Routed? Spoken request intent and 311 context

The current evaluation is a **text-only intent baseline**: a character n-gram classifier receives the supplied reference/transcription, not audio, and predicts MInDS-14 intents or Speech-MASSIVE scenarios using a held-out split. Current accuracies in `outputs/intent_evaluation.csv` are:

| Dataset | Language | Held-out accuracy | Important interpretation |
|---|---|---:|---|
| MInDS-14 | English | 90.6% | Banking-call intents; not city 311 |
| MInDS-14 | Mandarin Chinese | 98.1% | Text transcript input |
| MInDS-14 | Polish | 94.3% | Text transcript input |
| MInDS-14 | Portuguese | 94.3% | Text transcript input |
| MInDS-14 | Spanish | 98.1% | Text transcript input |
| Speech-MASSIVE | Arabic | 55.2% | Predicts one of the dataset's scenarios |
| Speech-MASSIVE | Polish | 58.6% | Predicts one of the dataset's scenarios |
| Speech-MASSIVE | Portuguese | 58.6% | Predicts one of the dataset's scenarios |
| Speech-MASSIVE | Spanish | 58.6% | Predicts one of the dataset's scenarios |
| Speech-MASSIVE | Vietnamese | 62.1% | Predicts one of the dataset's scenarios |

These are not acoustic recognition or production voice-pipeline scores, and the MInDS-14 banking requests differ from municipal requests. `outputs/intent_confusions.csv` records the true-to-predicted label pairs to inspect what goes wrong. Toronto's 2025 request-type counts in `outputs/toronto_311_request_types.csv` provide service-demand context; the current most frequent listed categories include damaged residential bin lids (24,448 requests), property standards violations (17,079), and dead-wildlife pickup (15,513). Toronto is only a proxy for request mix, not Mississauga demand.

### 3. Who's unheard, and where?

`outputs/unheard_index.csv` ranks 50 wards and neighbourhoods, includes scored-language population coverage, and reports official-language knowledge separately. **The current index uses only the available text-intent error rates**: the Scribe/FLEURS benchmark has not yet been run. Consequently, its present coverage is limited to Arabic, Mandarin Chinese, Polish, Portuguese, Spanish, and Vietnamese, and its score should be read as a text-baseline prioritization proxy, not a resident-level likelihood of being misunderstood. For example, Ward 10 has 8,165 speakers in those scored language groups, 11.059% benchmark-population coverage, and an index of 29.145; the scores do not represent all Ward 10 language communities.

The current formula does not weight recent immigration or call urgency. The number who know neither official language is displayed separately, not added to home-language counts, because these populations overlap. Add the Scribe results and validate an explicit weighting scheme before presenting a final risk ranking or an affected-population estimate.

### Close the loop with ElevenLabs

The callback prototype has generated [outputs/311_callback.mp3](outputs/311_callback.mp3) using voice ID `hpp4J3VqNfWAUOO0d1Us`. This demonstrates generating callback audio from provided text; it is not itself a multilingual agent, translation, or evidence that the callback improves comprehension or routing. Pair it with reviewed human translations, measured benchmark results, and usability testing before claiming impact.

## Optional speech-to-text benchmark

Scribe calls use ElevenLabs credits. Start with a small, explicit sample:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs `
  --datasets fleurs --per-group 1 --languages Urdu,Arabic
python -m mississauga_unheard index --workspace . --output-dir outputs
```

`--per-group` limits newly submitted clips by dataset and language. Transcripts and WER/CER results are stored in `outputs/asr_benchmark.csv`; group means go to `outputs/asr_summary.csv`. Processed clips are skipped on subsequent runs.

## Generate callback audio

Pass reviewed, human-translated callback wording and a real voice ID from your ElevenLabs account's Voices page:

```powershell
python -m mississauga_unheard prototype --workspace . `
  --voice-id hpp4J3VqNfWAUOO0d1Us `
  --text "Your reviewed callback message in the target language." `
  --output outputs/311_callback.mp3
```

The voice ID shown above was successfully tested with this account. Other IDs must be available to the account/API key; a `voice_not_found` error means the ID is unavailable. This command calls ElevenLabs text-to-speech and may use credits. The generated [callback sample](outputs/311_callback.mp3) is 33,897 bytes. It demonstrates multilingual audio delivery; it does not itself translate text or validate the service message. Have a fluent speaker review translations and pronunciations before presenting the message as city guidance.

## Verification completed

- Unit and mocked integration suite: **8 tests passed** using `python -m unittest discover -s tests -v`.
- Offline analysis and index ran successfully against the included data; the index contains 50 ward/neighbourhood rows.
- The ElevenLabs onboarding test request returned HTTP 200 and generated [outputs/elevenlabs_test.mp3](outputs/elevenlabs_test.mp3) (29,300 bytes; ID3 MP3 header verified). The SDK/key setup check passed. The MP3 is the CLI's approved test sample; it does not substitute for a Scribe benchmark run.

## Data cautions

- Ward 10 must use the corrected derived census data.
- Toronto 311 request categories are context, not Mississauga request-level data.
- The request datasets cover only some languages; unavailable language/service combinations are left unscored.
- Speech Accent Archive and Speech-MASSIVE have non-commercial and ShareAlike licensing conditions. See [LICENSES.md](LICENSES.md) before publishing.
- The supplied [README.md](README.md) is preserved unchanged; this file documents the Python workflow separately.
