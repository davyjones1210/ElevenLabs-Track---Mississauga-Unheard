# Mississauga Unheard — Findings Report

This report consolidates measured results and their interpretation for the
Mississauga Unheard challenge. The detailed per-clip transcripts, predictions,
and geographic output remain in the CSV files listed below. All FLEURS clips
(40 per language) were transcribed. Transcription of the other corpora stopped
when the ElevenLabs account ran out of usable credits. No reported error rate
is a population-level probability.

## Executive findings

- **Speech recognition:** In FLEURS (40 clips per language), Cantonese had the
  highest mean CER (26.43%), followed by Urdu (20.59%) and Punjabi (8.25%).
  Cantonese/Mandarin WER is dominated by word-boundary mismatch; CER is more
  useful. Cantonese home-language speakers number 10,765, concentrated most
  in Ward 6 (2,520) and East Credit (2,225). This is an ASR risk signal, not
  the fraction of residents who would fail to be understood.
- **Accented English:** Only 89/468 Accent Archive clips have been
  transcribed: Arabic 40/40, Bengali 21/21, Cantonese 16/35, and one pilot
  clip in each of 12 other groups. There is not yet a full-corpus ranking.
- **Intent routing:** The text-only classifier scored 90.6–98.1% across sampled
  MInDS-14 language splits and 55.2–62.1% across Speech-MASSIVE splits. In the
  separate audio-to-transcript-to-classifier smoke test, MInDS-14 was correct
  on 5/5 clips, while Speech-MASSIVE was correct on 1/5. These evaluations use
  different input/evaluation designs and are not directly comparable.
- **Unheard Index:** Combining full FLEURS CER with the still-small
  spoken-request pilot, Ward 10 ranks highest among wards (23.096);
  Cooksville (East) ranks highest among populated neighbourhoods (25.449).
  These are prioritization proxies, not observed caller failures.
- **Service context and prototype:** Toronto's most frequent listed 2025
  request types were damaged residential bin lids (24,448), property standards
  violations (17,079), and dead-wildlife pickup (15,513). Toronto is only a
  proxy. A brief Cantonese acknowledgment was generated; the remaining
  full-corpus Scribe run is blocked by the account quota.

## Scope and method

The workflow combines the supplied census-derived language/geography files,
FLEURS multilingual speech, Speech Accent Archive English recordings,
MInDS-14 and Speech-MASSIVE spoken requests, and Toronto 311 service request
counts. It uses ElevenLabs Scribe v2 for transcription, normalized WER and CER
against the provided references, a character n-gram text intent/scenario
classifier, and an Unheard Index that weights benchmarked home-language
speakers by measured speech/intent error.

All 560 FLEURS clips were transcribed (40 in each of 14 languages), including
the matched sentence-ID 1589 comparison. Overall, 659 of 2,653 clips have
Scribe results: 560 FLEURS, 89 Speech Accent Archive, five MInDS-14, and five
Speech-MASSIVE. Outstanding: 379 Accent Archive, 1,045 MInDS-14, and 570
Speech-MASSIVE clips. The run stopped when ElevenLabs reported 21 credits
remaining and at least 25 required for the next Scribe request. Spoken-request
audio routing therefore remains a ten-clip smoke test (one per available
language), not a full-dataset evaluation.

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

### Full FLEURS language-group results

All 560 FLEURS clips were transcribed (40 per language). Most clips are not
matched by sentence ID across languages, so these means do not control for
prompt content or speaker mix. The matched sentence-ID 1589 table above is a
one-clip-per-language comparison only.

| Language | Clips | Mean WER | Mean CER | Recorded genders |
|---|---:|---:|---|---|---|
| Cantonese | 40 | 99.84% | 26.43% | 24 female, 16 male |
| Urdu | 40 | 35.66% | 20.59% | 40 female |
| Punjabi | 40 | 11.63% | 8.25% | 40 female |
| Hindi | 40 | 5.60% | 6.76% | 15 female, 25 male |
| Mandarin Chinese | 40 | 99.91% | 2.94% | 15 female, 25 male |
| Tamil | 40 | 4.02% | 2.62% | 18 female, 22 male |
| Gujarati | 40 | 4.11% | 1.73% | 13 female, 27 male |
| Portuguese | 40 | 2.83% | 1.67% | 40 male |
| Tagalog | 40 | 4.35% | 1.44% | 40 male |
| Arabic | 40 | 6.19% | 1.14% | 40 female |
| Polish | 40 | 1.83% | 1.03% | 7 female, 33 male |
| English | 40 | 1.70% | 0.85% | 26 female, 14 male |
| Vietnamese | 40 | 0.96% | 0.69% | 40 male |
| Spanish | 40 | 1.16% | 0.57% | 10 female, 30 male |

Cantonese and Mandarin WER values near 100% are tokenization/word-boundary
artifacts; CER distinguishes their results (26.43% vs 2.94%). The high
Cantonese and Urdu CERs are the strongest measured in-language ASR risk
signals; Punjabi and Hindi follow. These are sample-level transcription
errors, not rates of residents being misunderstood in 311 calls.

### Speech Accent Archive English results (incomplete)

89 of 468 clips have been transcribed: all 40 Arabic clips, all 21 Bengali
clips, 16 of 35 Cantonese clips, and one clip in each of the other 12 groups.
All speakers read the same English paragraph. Most group results are still
single-speaker smoke tests, not a full-corpus accent ranking.

| First language | Clips | Mean WER | Mean CER | Recorded genders |
|---|---:|---:|---:|---|
| Arabic | 40 | 7.25% | 4.19% | 20 female, 20 male |
| Bengali | 21 | 3.86% | 2.60% | 13 female, 8 male |
| Cantonese | 16 | 4.08% | 2.36% | 9 female, 7 male |
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
Tamil, Gujarati, Punjabi, and Urdu have the highest CERs in the matched FLEURS
sample (5.19%, 3.08%, 2.82%, and 2.20%). These are sample rankings only; errors may reflect the sampled speaker,
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

### Audio-to-transcript-to-intent smoke test (partial)

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

The Unheard Index aggregates benchmarked home-language speakers by geography,
using the full per-language mean FLEURS CER and, where available, the separate
audio-intent error rate. Those two evidence sources are averaged equally for a
language with both. The intent error rate still has only one audio clip per
language in this run. The score is a 0–100 prioritization proxy, not a
probability that a particular resident will be misunderstood.
`weighted_error_count_proxy` is an arithmetic projection, not a count of known
failed interactions.

There are 11 ward and 39 neighbourhood rows (50 total). The highest ranked
wards and populated neighbourhoods are:

| Geography | Index | Scored speakers | Coverage | Clips | Weighted-error proxy |
|---|---:|---:|---:|---:|---:|
| Ward 10 | 23.096 | 17,210 | 23.310% | 529 | 3,974.8 |
| Ward 7 | 21.574 | 19,160 | 24.003% | 529 | 4,133.6 |
| Ward 3 | 21.359 | 10,020 | 17.842% | 529 | 2,140.2 |
| Cooksville (East) | 25.449 | 1,005 | 11.957% | 529 | 255.8 |
| Clarkson Village CN | 24.786 | 140 | 5.957% | 529 | 34.7 |
| Churchill Meadows | 24.683 | 13,980 | 28.680% | 529 | 3,450.7 |

Ward 10 now has the highest index among wards; Ward 7 has the largest
weighted-error proxy among wards because its scored speaker count is higher.
Cooksville (East) has the highest index among populated neighbourhoods, while
Clarkson Village CN has a high index but only 140 scored speakers and 5.957%
coverage. Rankings must be read alongside coverage and the single-sample
intent limitation.

### Residents in the highest-error FLEURS groups

FLEURS CER ranks Cantonese highest, then Urdu, Punjabi, and Hindi. Census
home-language counts and concentrations for these groups are:

| Home language | Mean FLEURS CER | Mississauga residents | Highest-count ward | Highest-count neighbourhood |
|---|---:|---:|---|---|
| Cantonese | 26.43% | 10,765 | Ward 6: 2,520 | East Credit: 2,225 |
| Urdu | 20.59% | 22,535 | Ward 10: 4,520 | Churchill Meadows: 3,755 |
| Punjabi | 8.25% | 15,025 | Ward 5: 8,095 | Malton: 7,145 |
| Hindi | 6.76% | 6,640 | Ward 5: 1,315 | DT Core: 930 |

Cantonese residents are also concentrated in Hurontario (1,520), Central Erin
Mills (1,095), and Churchill Meadows (905); Ward 5 (1,270) and Ward 4 (1,125)
follow Ward 6. Urdu concentrations include East Credit (3,395), Meadowvale
Village (1,585), and Hurontario (1,570). These are 2021 census home-language
speaker counts, not counts of people who exclusively speak that language or
who experienced a failed call. Language counts should not be added as unique
people without a validated overlap rule.

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

A short Cantonese acknowledgment was generated at
[outputs/311_callback_yue.mp3](311_callback_yue.mp3), using the configured
voice and the text “你好，我哋收到你嘅請求。” (“Hello, we received your
request.”). This is a brief proof of TTS generation for the highest-CER
language group, not a complete callback or validated Cantonese service
translation. Have a fluent Cantonese speaker review the wording and listen for
dialect/pronunciation before using it. TTS playback alone does not demonstrate
improved caller comprehension. The separate all-corpus Scribe run remains
blocked: at the time it stopped, ElevenLabs reported only 21 credits and
required at least 25 for the next speech-to-text clip.

## Limitations and responsible interpretation

1. **Incomplete/non-representative samples:** FLEURS has 40 clips per language,
   but mostly unmatched prompts and unavailable speaker IDs. Accent Archive
   has 89/468 transcriptions, and spoken-request audio has only one clip per
   available language. Reported rates are descriptive, not confidence-tested
   population estimates.
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
8. **Human review and licensing:** Both the Spanish copy and the new Cantonese
   wording/pronunciation need fluent-speaker validation. Speech Accent Archive and Speech-MASSIVE have
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

Speech results use ElevenLabs credits. The remaining benchmark is resumable
after credits are replenished:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs `
  --datasets fleurs,accent,minds14,massive --per-group 10000
```

The cache skips completed clips and saves each newly completed transcript.
Review the credit limitation in [`../PROJECT-README.md`](../PROJECT-README.md)
before resuming.

| Output | Contents |
|---|---|
| `paired_fleurs_summary.csv` | Matched FLEURS results by language |
| `paired_fleurs_benchmark.csv` | Matched FLEURS per-clip transcripts and scores |
| `asr_summary.csv` | Current per-dataset/language means, speaker metadata, and detected languages |
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
| `311_callback_yue.mp3` | Short Cantonese acknowledgment synthesized with ElevenLabs |

The root [`README.md`](../README.md) is preserved unchanged; see
[`../PROJECT-README.md`](../PROJECT-README.md) for the workflow overview and
challenge summary.
