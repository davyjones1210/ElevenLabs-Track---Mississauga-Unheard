# Mississauga Unheard — project workflow

This project analyzes the supplied Mississauga census, speech, and 311 data, and includes an optional ElevenLabs prototype for multilingual callback audio.

## Findings summary

The detailed, consolidated results are in [outputs/REPORT.md](outputs/REPORT.md).
In brief: the matched FLEURS pilot's highest CERs were Tamil (5.19%), Gujarati
(3.08%), Punjabi (2.82%), and Urdu (2.20%); Mandarin and Cantonese each had
100% WER but 0% CER due to Chinese character-spacing differences. In the
single-speaker Accent Archive sample, Mandarin Chinese first-language English
had the highest error (10.14% WER, 9.52% CER), with repeated/stuttered text
visible in the transcript. The same-text design does not isolate a language
effect because speaker IDs are unavailable and gender/dialect vary.

The held-out text baseline reached 90.6–98.1% on MInDS-14 and 55.2–62.1% on
Speech-MASSIVE. In the separate audio pipeline smoke test, 5/5 MInDS-14
requests and 1/5 Speech-MASSIVE requests were routed correctly; observed
Speech-MASSIVE confusions were Arabic `qa`→`play`, Polish
`recommendation`→`transport`, Portuguese `play`→`transport`, and Vietnamese
`calendar`→`recommendation`. The Polish and Vietnamese sampled transcripts
matched their references, showing that errors can also arise in routing after
transcription.

The request-audio ASR samples add an important qualification: Speech-MASSIVE
Arabic had 33.33% WER / 6.25% CER, Portuguese 15.38% / 1.79%; MInDS-14
Mandarin had 700.00% / 17.24% and Portuguese 13.33% / 9.39%. Each is one clip,
and the extreme Mandarin WER is tokenization-sensitive. In the combined
FLEURS ASR summary (initial plus matched samples), Gujarati had the highest
mean CER (3.76%), followed by Tamil (2.60%) and Urdu (2.20%); the matched-only
FLEURS values above are a separate comparison. See the detailed group tables
in [outputs/REPORT.md](outputs/REPORT.md).

Ward 7 had the highest ward index (17.573); Clarkson Village CN had the
highest populated-neighbourhood index (24.107). The index uses sparse
benchmark-derived evidence and its weighted-error values are projections, not
observed failed calls. Toronto's top listed 2025 request types were damaged
residential bin lids (24,448), property standards violations (17,079), and
dead-wildlife pickup (15,513); Toronto is only a demand proxy and contains no
language or urgency labels. Open service-request audio is missing for Urdu,
Punjabi, Tamil, Tagalog, Hindi, Gujarati, Bengali, and Cantonese. The
ElevenLabs English and Spanish callback clips demonstrate TTS generation only;
the Spanish wording needs fluent-speaker review and neither clip proves
improved service outcomes.

The SDK/key onboarding check passed, and the approved onboarding TTS request
returned HTTP 200 with a 29,300-byte MP3; this was a setup check, not an ASR
benchmark.

The supplied Mississauga annual 311 summary lists 250,476 calls offered and
233,547 answered in 2017 (93.2%); in 2018 it lists 253,674 offered and 232,348
answered (91.6%). The Unheard Index contains 11 wards and 39 neighbourhoods;
the highest ward index is Ward 7 (19,160 scored speakers, 24.003% coverage),
while Clarkson Village CN leads populated neighbourhoods with only 140 scored
speakers and 5.957% coverage. Residents who know neither official language
are shown separately, and recent immigration and urgency are not index weights.

## Install

From the project directory, in PowerShell:

```powershell
python -m pip install -e ".[elevenlabs]"
```

The ElevenLabs key is kept in the local, gitignored `.env` file. Do not copy it into source files, command output, or reports. The SDK loads it through `python-dotenv`.

## Data-first workflow

Start with `Mississauga_Unheard_ElevenLabs_Track/01_people_census/derived/language_coverage.csv` to see Mississauga home-language speaker counts and how many clips each corpus contains. Then use `Mississauga_Unheard_ElevenLabs_Track/01_people_census/derived/geo_language_long.csv` to connect ward/neighbourhood speakers to the crosswalked language names. The workflow consumes this derived geographic table, which uses the corrected Ward 10 home-language values; home language is not the same measure as mother tongue.

The supplied speech corpora total about 1.6 hours of FLEURS, 3.7 hours of accented English, 3.8 hours of MInDS-14, and 0.6 hours of Speech-MASSIVE. Scribe usage is per clip, so this project deliberately began with one clip per dataset/language group and a matched FLEURS prompt, rather than processing every recording. FLEURS Portuguese is Brazilian, Spanish is Latin American, and Arabic is Egyptian; MInDS-14 uses European Portuguese/Spanish. Speech-MASSIVE Portuguese speakers were born in Portugal, while about half of its `es-ES` speakers were born in Mexico. These are dialect/sample differences, not direct proxies for every Mississauga resident.

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

This creates census coverage and geography summaries, Toronto 311 service-type summaries, Mississauga 311 annual call totals, held-out text-intent baselines, confusion counts, and the geography-level `unheard_index.csv`. If an ASR benchmark exists, it also evaluates spoken-request audio transcripts against held-out intent labels before building the index.

The index is a prioritization proxy rather than a resident-level probability. It reports the population coverage and evidence sources alongside each score. Intent evaluation uses text transcripts and labeled scenarios; it does not claim to evaluate a deployed 311 agent.

## Challenge report

### 1. Understood? Speech-to-text by language and accent

The pilot used ElevenLabs Scribe v2 on one clip per dataset/language group and then an additional **matched FLEURS sentence** (`fleurs_id=1589`) for all 14 FLEURS languages. Metrics are WER/CER against the provided references. The matched sentence controls prompt content across languages; it does not control speaker identity, gender, or dialect. FLEURS metadata does not provide speaker IDs, and several language samples have the gender imbalance described in the challenge. The Speech Accent Archive uses the same English paragraph for its groups.

**Matched FLEURS pilot — one speaker/clip per language:**

| Language | WER | CER | Recorded gender | Scribe detected |
|---|---:|---:|---|---|
| Arabic | 0.00% | 0.00% | female | Arabic |
| Cantonese | 100.00% | 0.00% | female | Chinese (`zho`) |
| English | 0.00% | 0.00% | female | English |
| Gujarati | 4.08% | 3.08% | female | Gujarati |
| Hindi | 0.00% | 0.00% | female | Hindi |
| Mandarin Chinese | 100.00% | 0.00% | female | Chinese (`zho`) |
| Polish | 0.00% | 0.00% | female | Polish |
| Portuguese | 0.00% | 0.00% | male | Portuguese |
| Punjabi | 20.00% | 2.82% | female | Punjabi |
| Spanish | 0.00% | 0.00% | male | Spanish |
| Tagalog | 16.00% | 1.32% | male | Filipino |
| Tamil | 7.84% | 5.19% | male | Tamil |
| Urdu | 9.52% | 2.20% | female | Urdu (`urd`) |
| Vietnamese | 0.00% | 0.00% | male | Vietnamese |

The 100% WER for Cantonese and Mandarin is a tokenization artifact: references contain spaces between Chinese characters, while Scribe returns unspaced text. CER is 0% for these matched clips after punctuation/spacing normalization. The pilot detected Urdu as Urdu, not Hindi; the Cantonese clip was transcribed in the same character script as the reference at CER level. These are sample observations, not evidence that the model always identifies the language or preserves script.

**Speech Accent Archive English pilot — one speaker per first-language group:**

| First language | WER | CER | Gender |
|---|---:|---:|---|
| Arabic | 0.00% | 0.00% | female |
| Bengali | 0.00% | 0.00% | male |
| Cantonese | 4.35% | 2.93% | male |
| English (Canadian baseline) | 0.00% | 0.00% | female |
| Gujarati | 0.00% | 0.00% | female |
| Hindi | 0.00% | 0.00% | male |
| Mandarin Chinese | 10.14% | 9.52% | female |
| Polish | 1.45% | 1.10% | male |
| Portuguese | 0.00% | 0.00% | female |
| Punjabi | 1.45% | 0.73% | female |
| Spanish | 0.00% | 0.00% | male |
| Tagalog | 0.00% | 0.00% | female |
| Tamil | 0.00% | 0.00% | female |
| Urdu | 1.45% | 1.10% | male |
| Vietnamese | 2.90% | 1.47% | male |

Mandarin-accented English had the highest error in this one-clip accent sample. Its transcript repeats “We also need a small plastic” and stutters “sco-scoop,” which explains many of the observed insertions. Gujarati, Punjabi, and Urdu had the highest non-zero CER in the matched FLEURS sample (3.08%, 2.82%, and 2.20%). **Do not interpret these as reliable rankings or claim a language caused the errors:** each group has only one sampled speaker, FLEURS gender and dialect vary by language, and speaker IDs are unavailable for a speaker-controlled comparison. Error causes beyond visible tokenization/script effects need more clips and human transcript review.

Results and per-clip transcripts are in `outputs/paired_fleurs_summary.csv`, `outputs/paired_fleurs_benchmark.csv`, `outputs/asr_summary.csv`, and `outputs/asr_benchmark.csv`. CER is especially important for Urdu, Punjabi, Tamil, and Chinese; WER alone is misleading when word boundaries or tokenization differ.

The initial MInDS-14 and Speech-MASSIVE speech-to-text sample scores are also
reported in [outputs/REPORT.md](outputs/REPORT.md), separately from the text
intent scores below. These per-language ASR results each use a single spoken
request and are exploratory.

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

The existing held-out text baseline is not an audio score. The pilot also tested the actual sampled request audio through Scribe, then passed Scribe's transcript to a text intent/scenario classifier trained on the other reference transcripts in that dataset/language. It got **MInDS-14 right on 5/5 sampled clips** (one each: English, Mandarin Chinese, Polish, Portuguese, Spanish) and **Speech-MASSIVE right on 1/5** (Spanish; one each: Arabic, Polish, Portuguese, Spanish, Vietnamese). At one clip per language, these rates are smoke-test results, not estimates of real-world intent accuracy.

`outputs/audio_intent_predictions.csv` and `outputs/audio_intent_confusions.csv` show the misroutes: Arabic `qa` → `play`, Polish `recommendation` → `transport`, Portuguese `play` → `transport`, and Vietnamese `calendar` → `recommendation`. In a city deployment, these would route a caller to the wrong service flow; confirm the request and provide a human/alternate-language fallback rather than silently proceeding. The text-only comparison results remain in `outputs/intent_evaluation.csv` and `outputs/intent_confusions.csv`.

Toronto's 2025 request-type counts in `outputs/toronto_311_request_types.csv` provide service-demand context; the top listed categories include damaged residential bin lids (24,448 requests), property standards violations (17,079), and dead-wildlife pickup (15,513). Toronto is only a proxy for request mix, not Mississauga demand; neither dataset identifies language or an urgency label.

### 3. Who's unheard, and where?

`outputs/unheard_index.csv` ranks 11 wards and 39 neighbourhoods. It weights each area's speakers in benchmarked home languages by the mean available FLEURS CER and audio-intent error rate, then reports that weighted rate on a 0–100 scale. When a matched FLEURS sample exists, its CER is used. It also reports the number of scored language speakers, coverage of the language-base population, and count of benchmark clips contributing to the score.

In this pilot, Ward 7 ranks highest among wards (index 17.573; 19,160 home-language speakers in scored groups; 24.003% coverage; 22 benchmark clips; 3,367.0 weighted-error-count proxy). Clarkson Village CN ranks highest among populated neighbourhoods (index 24.107; 140 scored speakers; 5.957% coverage; 22 benchmark clips; 33.8 weighted-error-count proxy). Those proxy counts are arithmetic projections from tiny, non-representative samples—not counts of residents known to have been misunderstood. Use the coverage and clip-count fields to interpret them; do not present this ranking as a citywide finding.

The census's residents who know neither official language are shown separately because this group overlaps home-language speakers. Recent immigrants are included in census output but are not a weight in the current index. Toronto 311 data has no urgency label, so urgency is not modeled. Most importantly, the open request corpora have no service-request audio for Urdu, Punjabi, Tamil, Tagalog, Hindi, Gujarati, Bengali, or Cantonese. FLEURS/accent results do not replace missing real service-request examples for these communities; their request-routing risk remains unmeasured.

### Close the loop with ElevenLabs

The prototype has generated an English sample at [outputs/311_callback.mp3](outputs/311_callback.mp3) and a Spanish sample at [outputs/311_callback_es.mp3](outputs/311_callback_es.mp3), using voice ID `hpp4J3VqNfWAUOO0d1Us`. The Spanish text says, “Hola. Este es un mensaje de prueba para una devolución de llamada municipal. Hemos recibido su solicitud. Una persona del equipo de la ciudad le devolverá la llamada pronto.” The copy has not been reviewed by a fluent speaker; both clips demonstrate TTS generation, not a deployed agent or proof of improved comprehension/routing. Have a fluent speaker verify the translation and pronunciation before any service use.

## Optional speech-to-text benchmark

Scribe calls use ElevenLabs credits. The exploratory pilot used one clip per dataset/language group:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs `
  --datasets fleurs,accent,minds14,massive --per-group 1
```

For a controlled FLEURS cross-language comparison, all languages should use the same sentence ID. This command runs the matched ID 1589 sample, reusing already transcribed clips:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs --paired-fleurs
```

Regenerate analysis, audio-intent scores, and the census index:

```powershell
python -m mississauga_unheard analyze --workspace . --output-dir outputs
python -m mississauga_unheard index --workspace . --output-dir outputs
```

`--per-group` limits newly submitted clips by dataset and language. Transcripts and WER/CER results are stored in `outputs/asr_benchmark.csv`; group means go to `outputs/asr_summary.csv`. The matched FLEURS results are in `outputs/paired_fleurs_benchmark.csv` and `outputs/paired_fleurs_summary.csv`. Spoken-request ASR transcripts are then routed to labeled intents/scenarios; per-clip results and error pairs are in `outputs/audio_intent_predictions.csv` and `outputs/audio_intent_confusions.csv`. Processed clips are skipped on subsequent runs.

## Generate callback audio

Pass reviewed, human-translated callback wording and a real voice ID from your ElevenLabs account's Voices page:

```powershell
python -m mississauga_unheard prototype --workspace . `
  --voice-id hpp4J3VqNfWAUOO0d1Us `
  --text "Your reviewed callback message in the target language." `
  --output outputs/311_callback.mp3
```

The voice ID shown above was successfully tested with this account. Other IDs must be available to the account/API key; a `voice_not_found` error means the ID is unavailable. This command calls ElevenLabs text-to-speech and may use credits. The generated [English callback sample](outputs/311_callback.mp3) demonstrates audio generation but does not itself translate text or validate the service message. Have a fluent speaker review translations and pronunciations before presenting the message as city guidance.

A Spanish-language prototype is also available at [outputs/311_callback_es.mp3](outputs/311_callback_es.mp3). The sample wording is a demonstration translation and requires review by a fluent speaker before real service use.

## Verification completed

- Unit and mocked integration suite: **11 tests passed** using `python -m unittest discover -s tests -v`.
- Offline analysis and index ran successfully against the included data; the index contains 50 ward/neighbourhood rows.
- The authorized Scribe pilot covered all 39 dataset/language groups; 12 additional API requests completed the matched 14-language FLEURS sample, reusing two pilot clips. The per-group sample size is one, so all error-rate and routing findings remain exploratory.
- Audio-intent evaluation uses Scribe transcripts for one held-out spoken request per available language; it is not representative of live 311 calls.
- A Spanish callback was generated with ElevenLabs TTS using voice ID `hpp4J3VqNfWAUOO0d1Us`. Have a fluent speaker verify the text and pronunciation.
- The ElevenLabs onboarding test request returned HTTP 200 and generated [outputs/elevenlabs_test.mp3](outputs/elevenlabs_test.mp3) (29,300 bytes; ID3 MP3 header verified). The SDK/key setup check passed. The MP3 is the CLI's approved test sample; it does not substitute for a Scribe benchmark run.

## Data cautions

- Ward 10 must use the corrected derived census data.
- Toronto 311 request categories are context, not Mississauga request-level data.
- The request datasets cover only some languages; unavailable language/service combinations are left unscored.
- Speech Accent Archive and Speech-MASSIVE have non-commercial and ShareAlike licensing conditions. See [LICENSES.md](LICENSES.md) before publishing.
- The supplied [README.md](README.md) is preserved unchanged; this file documents the Python workflow separately.
