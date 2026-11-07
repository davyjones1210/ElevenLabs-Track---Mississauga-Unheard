# Mississauga Unheard — Findings Report

This report consolidates the measured pilot results and their interpretation for
the Mississauga Unheard challenge. The detailed per-clip transcripts, predictions,
and geographic output remain in the CSV files listed below. The analysis is
exploratory: most speech results use one clip per dataset/language group and
should not be interpreted as population-level error rates.

## Executive findings

- **Speech recognition:** For the matched FLEURS prompt (sentence ID 1589), the
  highest CERs were Tamil (5.19%), Gujarati (3.08%), Punjabi (2.82%), and Urdu
  (2.20%). WER was 100% for Mandarin and Cantonese even though CER was 0%,
  because the references have character-level spaces and Scribe returns
  unspaced Chinese text. The matched prompt controls content, not speaker,
  gender, or dialect.
- **Accented English:** Mandarin Chinese first-language English had the highest
  error in the one-speaker Accent Archive sample (WER 10.14%, CER 9.52%). The
  transcript repeats a phrase and contains a “sco-scoop” stutter; this is a
  sample-specific observation, not a language-level conclusion.
- **Intent routing:** The text-only classifier scored 90.6–98.1% across sampled
  MInDS-14 language splits and 55.2–62.1% across Speech-MASSIVE splits. In the
  separate audio-to-transcript-to-classifier smoke test, MInDS-14 was correct
  on 5/5 clips, while Speech-MASSIVE was correct on 1/5. These evaluations use
  different input/evaluation designs and are not directly comparable.
- **Unheard Index:** Ward 7 ranked highest among wards (17.573). Clarkson
  Village CN ranked highest among populated neighbourhoods (24.107). The
  index and weighted-error proxy depend on sparse, non-representative samples
  and only cover benchmarked languages.
- **Service context and prototype:** Toronto's most frequent listed 2025
  request types were damaged residential bin lids (24,448), property standards
  violations (17,079), and dead-wildlife pickup (15,513). Toronto is only a
  proxy. ElevenLabs generated English and Spanish callback audio, but neither
  demonstrates a deployed agent or improved service outcome.

## Scope and method

The workflow combines the supplied census-derived language/geography files,
FLEURS multilingual speech, Speech Accent Archive English recordings,
MInDS-14 and Speech-MASSIVE spoken requests, and Toronto 311 service request
counts. It uses ElevenLabs Scribe v2 for transcription, normalized WER and CER
against the provided references, a character n-gram text intent/scenario
classifier, and an Unheard Index that weights benchmarked home-language
speakers by measured speech/intent error.

The Scribe pilot covered the 39 dataset/language groups with one clip per group.
Twelve additional Scribe requests completed a matched FLEURS sentence-ID 1589
comparison for all 14 language groups; two matching clips were reused from the
initial run. The saved per-clip output contains 51 ASR rows. The audio intent
pilot uses one spoken request per available language (10 clips total).

FLEURS Portuguese is Brazilian, Spanish is Latin American, and Arabic is
Egyptian. The Speech Accent Archive sample reads the same English paragraph
across first-language groups. MInDS-14 uses European Portuguese and Spanish;
Speech-MASSIVE Portuguese speakers were born in Portugal and about half its
`es-ES` speakers were born in Mexico. These sample dialects do not represent all
Mississauga residents.

## 1. Understood? Speech-to-text

### Matched FLEURS prompt

All rows below use sentence ID 1589, one clip per language. Percentages are
computed against the supplied reference.

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

The zero CER for Mandarin and Cantonese reflects that punctuation/spacing
normalization removes the Chinese character-spacing mismatch; it does not mean
their WER is meaningful. Urdu was detected as Urdu rather than Hindi in this
clip, and the Cantonese transcription matched the reference's character script
at CER level. Neither observation establishes consistent language or script
behavior.

The gender distribution reinforces the design limitation in the challenge:
Arabic, Punjabi, and Urdu matched clips are female; Portuguese, Tagalog, and
Vietnamese are male. FLEURS does not expose speaker IDs in the supplied
metadata. Matching sentence ID holds text constant, but speaker, gender,
recording, and dialect effects cannot be separated from language effects.

### Combined FLEURS ASR group results

These group means summarize all FLEURS rows in `asr_benchmark.csv`, pooling the
initial language-group sample with the additional matched-prompt clips. Some
clips appear in both the matched-prompt table and these pooled means, but each
clip is counted only once in the group summary. The matched-prompt table above
isolates sentence ID 1589. Group sample counts are shown below.

| Language | Clips | Mean WER | Mean CER | Recorded genders | Detected |
|---|---:|---:|---|---|---|
| Arabic | 2 | 0.00% | 0.00% | 2 female | `ara` |
| Cantonese | 1 | 100.00% | 0.00% | 1 female | `zho` |
| English | 2 | 0.00% | 0.00% | 1 female, 1 male | `eng` |
| Gujarati | 2 | 3.51% | 3.76% | 1 female, 1 male | `guj` |
| Hindi | 2 | 0.00% | 0.00% | 1 female, 1 male | `hin` |
| Mandarin Chinese | 2 | 100.00% | 0.00% | 2 female | `zho` |
| Polish | 2 | 0.00% | 0.00% | 1 female, 1 male | `pol` |
| Portuguese | 2 | 0.00% | 0.00% | 2 male | `por` |
| Punjabi | 2 | 12.38% | 1.41% | 2 female | `pan` |
| Spanish | 2 | 0.00% | 0.00% | 2 male | `spa` |
| Tagalog | 2 | 10.63% | 1.26% | 2 male | `fil` |
| Tamil | 2 | 6.30% | 2.60% | 1 female, 1 male | `tam` |
| Urdu | 1 | 9.52% | 2.20% | 1 female | `urd` |
| Vietnamese | 2 | 0.00% | 0.00% | 2 male | `vie` |

The unmatched initial clips can differ in sentence content; the matched
sentence comparison is the stronger cross-language content control. Both
samples remain too small for general conclusions.

### Speech Accent Archive English pilot

One speaker per first-language group read the shared English passage.

| First language | Clips | WER | CER | Gender |
|---|---:|---:|---:|---|
| Arabic | 1 | 0.00% | 0.00% | female |
| Bengali | 1 | 0.00% | 0.00% | male |
| Cantonese | 1 | 4.35% | 2.93% | male |
| English (Canadian baseline) | 1 | 0.00% | 0.00% | female |
| Gujarati | 1 | 0.00% | 0.00% | female |
| Hindi | 1 | 0.00% | 0.00% | male |
| Mandarin Chinese | 1 | 10.14% | 9.52% | female |
| Polish | 1 | 1.45% | 1.10% | male |
| Portuguese | 1 | 0.00% | 0.00% | female |
| Punjabi | 1 | 1.45% | 0.73% | female |
| Spanish | 1 | 0.00% | 0.00% | male |
| Tagalog | 1 | 0.00% | 0.00% | female |
| Tamil | 1 | 0.00% | 0.00% | female |
| Urdu | 1 | 1.45% | 1.10% | male |
| Vietnamese | 1 | 2.90% | 1.47% | male |

The Mandarin-accented English transcript repeats “We also need a small
plastic” and includes “sco-scoop,” accounting for many observed insertions.
Gujarati, Punjabi, and Urdu have the highest non-zero CER in the matched FLEURS
sample. These are sample rankings only; errors may reflect the sampled speaker,
stutter, reference/transcription conventions, recording, or model behavior.

### Spoken-request ASR samples

One MInDS-14 and one Speech-MASSIVE audio clip per available language were also
transcribed. These are WER/CER against each dataset's reference transcript and
are separate from the matched FLEURS and accent tests.

| Dataset | Language | Clips | WER | CER | Scribe detected |
|---|---|---:|---:|---:|---|
| Speech-MASSIVE | Arabic | 1 | 33.33% | 6.25% | `ara` |
| Speech-MASSIVE | Polish | 1 | 0.00% | 0.00% | `pol` |
| Speech-MASSIVE | Portuguese | 1 | 15.38% | 1.79% | `por` |
| Speech-MASSIVE | Spanish | 1 | 0.00% | 0.00% | `spa` |
| Speech-MASSIVE | Vietnamese | 1 | 0.00% | 0.00% | `vie` |
| MInDS-14 | English | 1 | 0.00% | 0.00% | `eng` |
| MInDS-14 | Mandarin Chinese | 1 | 700.00% | 17.24% | `zho` |
| MInDS-14 | Polish | 1 | 0.00% | 0.00% | `pol` |
| MInDS-14 | Portuguese | 1 | 13.33% | 9.39% | `por` |
| MInDS-14 | Spanish | 1 | 0.00% | 0.00% | `spa` |

The unusually high Mandarin WER is sensitive to tokenization and the very short
sample; CER is the more interpretable character-based comparison here. This
small set does not establish language-specific ASR performance.

## 2. Routed? Intent evaluation and 311 context

### Held-out text-only intent/scenario baseline

The character n-gram classifier receives dataset reference/transcription text,
not audio. Each language split has 53 held-out MInDS-14 examples or 29
Speech-MASSIVE examples.

| Dataset | Language | Correct / total | Accuracy | Target |
|---|---|---:|---:|---|
| MInDS-14 | English | 48 / 53 | 90.6% | banking intent |
| MInDS-14 | Mandarin Chinese | 52 / 53 | 98.1% | banking intent |
| MInDS-14 | Polish | 50 / 53 | 94.3% | banking intent |
| MInDS-14 | Portuguese | 50 / 53 | 94.3% | banking intent |
| MInDS-14 | Spanish | 52 / 53 | 98.1% | banking intent |
| Speech-MASSIVE | Arabic | 16 / 29 | 55.2% | assistant scenario |
| Speech-MASSIVE | Polish | 17 / 29 | 58.6% | assistant scenario |
| Speech-MASSIVE | Portuguese | 17 / 29 | 58.6% | assistant scenario |
| Speech-MASSIVE | Spanish | 17 / 29 | 58.6% | assistant scenario |
| Speech-MASSIVE | Vietnamese | 18 / 29 | 62.1% | assistant scenario |

These scores are not end-to-end voice accuracy and neither corpus represents
Mississauga 311 service categories.

### Audio-to-transcript-to-intent smoke test

For this separate test, Scribe transcripts of the sampled requests were sent to
a classifier trained on other reference transcripts from the same
dataset/language. It correctly routed 5/5 MInDS-14 clips and 1/5
Speech-MASSIVE clips.

| Dataset | Language | True label | Predicted label | Result |
|---|---|---|---|---|
| MInDS-14 | English | `abroad` | `abroad` | correct |
| MInDS-14 | Mandarin Chinese | `pay_bill` | `pay_bill` | correct |
| MInDS-14 | Polish | `balance` | `balance` | correct |
| MInDS-14 | Portuguese | `latest_transactions` | `latest_transactions` | correct |
| MInDS-14 | Spanish | `card_issues` | `card_issues` | correct |
| Speech-MASSIVE | Arabic | `qa` | `play` | incorrect |
| Speech-MASSIVE | Polish | `recommendation` | `transport` | incorrect |
| Speech-MASSIVE | Portuguese | `play` | `transport` | incorrect |
| Speech-MASSIVE | Spanish | `iot` | `iot` | correct |
| Speech-MASSIVE | Vietnamese | `calendar` | `recommendation` | incorrect |

The Polish and Vietnamese ASR pilot transcripts matched their references
(0 WER/CER), yet their intents were misclassified. This demonstrates that
routing can fail downstream of transcription even in these examples. A city
workflow should confirm interpreted requests and provide a human or
alternate-language fallback rather than silently dispatching a possibly wrong
service.

### Toronto 311 context

The top listed request types in the supplied Toronto 2025 extract are:

| Service request type | Requests |
|---|---:|
| Residential Bin Lid Damaged | 24,448 |
| Property Standards and Maintenance Violations | 17,079 |
| Pick up Dead Wildlife | 15,513 |
| Injured - Wildlife | 15,192 |
| General Pruning | 12,873 |
| Road Pothole / Road Damage | 11,304 |
| Residential Bin Body or Handle Damaged | 11,238 |
| Sidewalk Snow Clearing Required | 10,241 |
| Res / Garbage / Not Picked Up | 9,159 |
| Residential Furniture / Not Picked Up | 8,634 |

The supplied Mississauga 311 annual summary reports 250,476 calls offered and
233,547 answered in 2017 (93.2% answer rate), and 253,674 offered and 232,348
answered in 2018 (91.6% answer rate). These counts offer operational context,
not language-specific outcomes. Toronto is not Mississauga, and the provided
request-type data does not label language or urgency.

## 3. Who's unheard, and where?

The Unheard Index aggregates benchmarked home-language speakers by
geography and weights them using the mean available FLEURS CER and audio-intent
error rate. The matched FLEURS CER is preferred; text-only intent results are
fallback evidence where audio-intent results are unavailable. The score is a
0–100 prioritization proxy, not a probability that a particular resident will
be misunderstood. `weighted_error_count_proxy` is an arithmetic projection,
not a count of known failed interactions.

There are 11 ward and 39 neighbourhood rows (50 total). The highest ranked
wards and populated neighbourhoods are:

| Geography | Index | Scored speakers | Coverage | Clips | Weighted-error proxy |
|---|---:|---:|---:|---:|---:|
| Ward 7 | 17.573 | 19,160 | 24.003% | 22 | 3,367.0 |
| Ward 3 | 17.464 | 10,020 | 17.842% | 22 | 1,749.8 |
| Clarkson Village CN | 24.107 | 140 | 5.957% | 22 | 33.8 |
| Cooksville (East) | 23.993 | 1,005 | 11.957% | 22 | 241.1 |
| Dixie EA | 20.000 | 100 | 10.582% | 22 | 20.0 |

Clarkson Village CN has the highest index rate among populated neighbourhoods,
but its scored population and coverage are small. Ward 7 has the largest
weighted-error proxy among wards, driven in part by its larger scored speaker
count. Rankings should always be read alongside coverage and clip counts.

The census's residents who know neither English nor French are reported
separately because this group overlaps home-language speaker counts. Recent
immigration is present in the census output but is not a weight in the current
index. No urgency weight is used because the Toronto request data lacks urgency
labels.

### Coverage gap

The available open request corpora do not include service-request audio in
Urdu, Punjabi, Tamil, Tagalog, Hindi, Gujarati, Bengali, or Cantonese. FLEURS
and the Accent Archive can test language speech or accented English, but they
cannot establish whether a 311 request in those languages is understood or
routed correctly. Those communities' service-request routing risk remains
unmeasured. Suitable next steps include carefully translated evaluation data
or a small, consented recording study; no such data is claimed in this report.

Ward 10 values must come from the corrected
`../Mississauga_Unheard_ElevenLabs_Track/01_people_census/derived/ward_language_profile_2021_corrected.csv`
or neighbourhood-derived data. The raw ward table contains errors (for
example, Urdu is listed as 50 where the neighbourhood-based figure is 7,225).
Seventeen of the 56 supplied "neighbourhoods" are employment or airport areas
with zero population.

## ElevenLabs prototype

ElevenLabs TTS generated:

- [English callback sample](311_callback.mp3)
- [Spanish callback sample](311_callback_es.mp3)
- [Onboarding test sample](elevenlabs_test.mp3)

The SDK/key onboarding check passed. The approved onboarding test request
returned HTTP 200 and generated a 29,300-byte MP3 with an ID3 header; this is a
TTS setup check, not an Scribe benchmark result.

The working voice ID was `hpp4J3VqNfWAUOO0d1Us`. The Spanish demonstration
wording is: “Hola. Este es un mensaje de prueba para una devolución de llamada
municipal. Hemos recibido su solicitud. Una persona del equipo de la ciudad le
devolverá la llamada pronto.” It has not been reviewed by a fluent speaker.
These files demonstrate TTS output only: the prototype does not translate
automatically, establish correct pronunciation for every community, or show
improved caller comprehension or routing. Have a fluent speaker review wording
and pronunciation before any service use.

The earlier user-supplied voice ID `wBXNqKUATyqu0RtYt25i` returned HTTP 402
because the account could not use that library voice. The ID above successfully
generated the later callback audio. Never store or publish the API key; it
remains in the ignored local `.env` file.

## Limitations and responsible interpretation

1. **Very small samples:** Matched FLEURS, Accent Archive, and spoken-request
   audio results use one clip per language/group; the pooled FLEURS summary has
   one or two clips per language. Reported rates are descriptive smoke tests,
   not confidence-tested population estimates.
2. **Speaker confounding:** FLEURS speaker IDs are unavailable; gender,
   dialect, and language composition vary. Matched prompt text controls only
   sentence content.
3. **Metric differences:** WER can be misleading for Chinese and scripts with
   inconsistent word boundaries. Use CER as well, and do not compare WER
   blindly across scripts.
4. **Dataset/task mismatch:** MInDS-14 is banking; Speech-MASSIVE is a
   virtual-assistant benchmark; neither is a set of Mississauga 311 requests.
   The classifier is a simple text baseline, not a deployed agent.
5. **Geographic proxy:** The index uses available benchmark evidence and
   population counts; it cannot measure the experience of unbenchmarked
   languages or individuals.
6. **Demand/urgency mismatch:** Toronto is only a proxy for request types.
   The current source has no language or urgency labels.
7. **Dialect differences:** Benchmark dialects differ from some Mississauga
   communities, including Portuguese and Spanish varieties.
8. **Human review and licensing:** The Spanish copy needs fluent-speaker
   validation. Speech Accent Archive and Speech-MASSIVE have
   non-commercial/ShareAlike conditions; consult [`../LICENSES.md`](../LICENSES.md)
   before publication or reuse.

## Reproducibility and source outputs

Run the workflow from the project root:

```powershell
python -m mississauga_unheard analyze --workspace . --output-dir outputs
python -m mississauga_unheard index --workspace . --output-dir outputs
python -m unittest discover -s tests -v
```

The unit suite passed all 11 tests. Offline analysis and index generation
completed successfully and produced 50 ward/neighbourhood rows.

Speech results use ElevenLabs credits. The benchmark command is deliberately
sample-limited; review commands and cost notes in
[`../PROJECT-README.md`](../PROJECT-README.md) before submitting additional
clips.

| Output | Contents |
|---|---|
| `paired_fleurs_summary.csv` | Matched FLEURS results by language |
| `paired_fleurs_benchmark.csv` | Matched FLEURS per-clip transcripts and scores |
| `asr_summary.csv` | ASR pilot group averages, speaker metadata, and detected languages |
| `asr_benchmark.csv` | Per-clip ASR transcripts and WER/CER |
| `intent_evaluation.csv` | Held-out text-only intent/scenario accuracy |
| `intent_confusions.csv` | Held-out text-only label confusions |
| `audio_intent_evaluation.csv` | Audio-pilot intent/scenario accuracy by dataset/language |
| `audio_intent_predictions.csv` | Per-clip audio transcript intent predictions |
| `audio_intent_confusions.csv` | Audio-pilot true/predicted label pairs |
| `unheard_index.csv` | Ward/neighbourhood score, evidence coverage, and proxy counts |
| `toronto_311_request_types.csv` | Toronto service request type counts |
| `mississauga_311_yearly_calls.csv` | Mississauga 311 annual offered/answered calls |
| `language_coverage.csv` | Home-language speaker and dataset-coverage counts |

The root [`README.md`](../README.md) is preserved unchanged; see
[`../PROJECT-README.md`](../PROJECT-README.md) for the workflow overview and
challenge summary.
