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

## Optional speech-to-text benchmark

Scribe calls use ElevenLabs credits. Start with a small, explicit sample:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs `
  --datasets fleurs --per-group 1 --languages Urdu,Arabic
python -m mississauga_unheard index --workspace . --output-dir outputs
```

`--per-group` limits newly submitted clips by dataset and language. Transcripts and WER/CER results are stored in `outputs/asr_benchmark.csv`; group means go to `outputs/asr_summary.csv`. Processed clips are skipped on subsequent runs.

## Generate callback audio

Pass reviewed, human-translated callback wording and a voice ID from your ElevenLabs voice library:

```powershell
python -m mississauga_unheard prototype --workspace . `
  --voice-id YOUR_VOICE_ID `
  --text "Your reviewed callback message in the target language." `
  --output outputs/311_callback.mp3
```

This command calls ElevenLabs text-to-speech and may use credits. The generated clip demonstrates multilingual audio delivery; it does not itself translate text or validate the service message. Have a fluent speaker review translations and pronunciations before presenting the message as city guidance.

## Verification completed

- Unit and mocked integration suite: **6 tests passed** using `python -m unittest discover -s tests -v`.
- Offline analysis and index ran successfully against the included data; the index contains 50 ward/neighbourhood rows.
- The ElevenLabs onboarding test request returned HTTP 200 and generated [outputs/elevenlabs_test.mp3](outputs/elevenlabs_test.mp3) (29,300 bytes; ID3 MP3 header verified). The SDK/key setup check passed. The MP3 is the CLI's approved test sample; it does not substitute for a Scribe benchmark run.

## Data cautions

- Ward 10 must use the corrected derived census data.
- Toronto 311 request categories are context, not Mississauga request-level data.
- The request datasets cover only some languages; unavailable language/service combinations are left unscored.
- Speech Accent Archive and Speech-MASSIVE have non-commercial and ShareAlike licensing conditions. See [LICENSES.md](LICENSES.md) before publishing.
- The supplied [README.md](README.md) is preserved unchanged; this file documents the Python workflow separately.
