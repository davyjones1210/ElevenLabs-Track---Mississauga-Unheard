# ElevenLabs Track - Mississauga Unheard

## Inspiration

Mississauga is multilingual, but a voice service can fail residents at two
different steps: recognizing what they say and routing the request correctly.
This project explores how to measure those gaps with the supplied speech,
census, and 311 data, and demonstrates a multilingual callback with ElevenLabs.

The guiding questions are:

- Which language and accent groups show the largest speech-recognition errors?
- How reliably do speech datasets' requests reach the correct intent or
  scenario?
- Where do speakers of languages with weaker measured results live?
- Could a callback in a resident's language help close part of the service gap?

## What it does

The Python workflow analyzes census language coverage, speech recognition,
request-intent baselines, service-request context, and an Unheard Index by ward
and neighbourhood. It also generates callback audio with ElevenLabs text to
speech.

**FLEURS speech recognition:** All 560 available clips were transcribed with
ElevenLabs Scribe v2 (40 clips in each of 14 languages). The highest mean
character error rates (CER) were:

| Language | Clips | Mean CER | Mean WER |
|---|---:|---:|---:|
| Cantonese | 40 | 26.43% | 99.84% |
| Urdu | 40 | 20.59% | 35.66% |
| Punjabi | 40 | 8.25% | 11.63% |
| Hindi | 40 | 6.76% | 5.60% |
| Mandarin Chinese | 40 | 2.94% | 99.91% |

For Cantonese and Mandarin, WER is dominated by tokenization and word-boundary
differences; CER is more informative. The matched FLEURS sentence ID 1589
controls the prompt for one clip per language, but it does not control speaker,
gender, or dialect. The complete language-group measurements are samples, not
proof that language itself caused an error.

**Who and where:** The 2021 census reports 10,765 Cantonese home-language
speakers in Mississauga. The largest counts are in Ward 6 (2,520) and East
Credit (2,225). Other high-CER groups include 22,535 Urdu speakers (Ward 10:
4,520; Churchill Meadows: 3,755), 15,025 Punjabi speakers (Ward 5: 8,095;
Malton: 7,145), and 6,640 Hindi speakers (Ward 5: 1,315; DT Core: 930).
These are home-language counts, not counts of residents known to have been
misunderstood or who speak only that language.

The current evidence-based Unheard Index ranks Ward 10 highest among wards
(23.096) and Cooksville (East) highest among populated neighbourhoods (25.449).
The index combines FLEURS CER with the available spoken-request intent error
evidence. Because the intent evidence is still very limited, these scores are
prioritization proxies, not resident-level probabilities or verified failed
calls.

**Intent and service context:** A text-only character n-gram baseline reached
90.6–98.1% held-out accuracy across the tested MInDS-14 language splits and
55.2–62.1% across Speech-MASSIVE. Separately, the sampled audio-to-transcript
pipeline routed 5/5 MInDS-14 clips and 1/5 Speech-MASSIVE clips correctly.
These corpora are banking and virtual-assistant tasks, not Mississauga 311
calls. Toronto's top listed 2025 request types were damaged residential bin
lids (24,448), property standards violations (17,079), and dead-wildlife
pickup (15,513); Toronto is only a proxy and its data has no language or
urgency labels.

**ElevenLabs demonstration:** A short Cantonese acknowledgment was generated
with the configured voice: “你好，我哋收到你嘅請求。” (“Hello, we received
your request.”) Listen to [the Cantonese audio
sample](outputs/311_callback_yue.mp3). This demonstrates TTS generation for
the highest-CER language group; it is not a complete callback, a translation
validation, or proof of improved comprehension. A fluent Cantonese speaker
should review the wording and pronunciation before service use.

For the detailed results, full FLEURS table, partial Accent Archive results,
limitations, and all source-output files, see [outputs/REPORT.md](outputs/REPORT.md).

## How we built it

The project is an installable Python package under `src/mississauga_unheard`.
It reads the supplied census-derived language/geography files and speech
metadata, computes normalized WER and CER, trains a character n-gram text
intent baseline, evaluates available audio transcripts against labels, and
builds the ward/neighbourhood index. The index uses the corrected Ward 10
census data through the supplied derived geography table.

ElevenLabs Scribe v2 was used to transcribe audio. Completed results are
cached per dataset and file in `outputs/asr_benchmark.csv`; summary tables and
the index can then be regenerated offline. The ElevenLabs API key is stored
only in the local, gitignored `.env` file.

Install the package and optional ElevenLabs dependencies from the project root:

```powershell
python -m pip install -e ".[elevenlabs]"
```

Run the offline analysis and index:

```powershell
python -m mississauga_unheard analyze --workspace . --output-dir outputs
python -m mississauga_unheard index --workspace . --output-dir outputs
```

The full transcription run can be resumed once the ElevenLabs account has
sufficient credits. Existing results are skipped:

```powershell
python -m mississauga_unheard benchmark --workspace . --output-dir outputs `
  --datasets fleurs,accent,minds14,massive --per-group 10000
```

To generate a callback, provide reviewed text in the target language and a
voice available to the account:

```powershell
python -m mississauga_unheard prototype --workspace . `
  --voice-id hpp4J3VqNfWAUOO0d1Us `
  --text "你好，我哋收到你嘅請求。" `
  --output outputs/311_callback_yue.mp3
```

The saved Cantonese sample used this working voice ID. Speech Accent Archive
and Speech-MASSIVE include non-commercial/ShareAlike licensing conditions;
review [LICENSES.md](LICENSES.md) before publishing or reusing their data.

## Challenges we ran into

- **API credits:** The full inventory is 2,653 clips. Scribe results were
  saved for 659: all 560 FLEURS clips, 89 of 468 Accent Archive clips, five of
  1,050 MInDS-14 clips, and five of 575 Speech-MASSIVE clips. The run stopped
  when ElevenLabs reported 21 credits remaining and at least 25 required for
  the next request. The remaining 1,994 clips are not processed.
- **Language and speaker effects:** The matched FLEURS prompt controls text
  content for only one clip per language. Speaker IDs are unavailable, and
  gender and dialect differ across groups. The full 40-clip language groups
  also do not all contain matched prompts.
- **Metric comparability:** Chinese character spacing can produce near-100%
  WER even when CER is lower. CER is necessary alongside WER and is the
  primary comparison used here for scripts with inconsistent word boundaries.
- **Accent coverage:** The Speech Accent Archive is incomplete: Arabic is
  40/40, Bengali 21/21, Cantonese 16/35, and 12 other groups have one clip
  each. It is not yet possible to make a complete accent-group ranking.
- **Request-data mismatch:** Only ten request clips have been processed. The
  audio pipeline got 5/5 MInDS-14 and 1/5 Speech-MASSIVE sampled clips right;
  that is a smoke test, not a reliable rate. These are not 311 requests.
- **Missing service-language audio:** There is no open request-audio
  evaluation here for Cantonese, Urdu, Punjabi, Hindi, Gujarati, Tamil,
  Tagalog, or Bengali. FLEURS speech is not a substitute for real service
  requests in those languages.
- **Geographic and service-data limits:** Census home-language counts can
  overlap and do not identify failed calls. Toronto is not Mississauga, and
  the available request-type data does not label language or urgency.
- **Prototype validation:** The Cantonese text and generated pronunciation
  need fluent-speaker review. TTS output alone cannot establish service
  readiness or comprehension gains.

## Accomplishments that we're proud of

- Transcribed all 560 FLEURS clips, yielding a stronger comparison than the
  initial one-clip-per-language pilot.
- Identified Cantonese as the highest measured FLEURS CER group and connected
  that finding to census counts by ward and neighbourhood.
- Corrected the index to use all available FLEURS clip-level CER results when
  present, rather than preferring the smaller matched-prompt summary.
- Built a resumable benchmark that writes results incrementally, allowing
  completed work to be retained when API credits run out.
- Generated an ElevenLabs Cantonese acknowledgment for the highest-CER group.
- Preserved the supplied root [README.md](README.md) unchanged.
- Passed all 11 unit tests after the index update.

## What we learned

- The measured gap is not evenly distributed: Cantonese, Urdu, and Punjabi
  had the largest mean FLEURS CERs in this 40-clip-per-language run.
- A very high WER does not always mean a comparable recognition failure:
  Chinese tokenization made CER the more useful metric for Mandarin and
  Cantonese, though Cantonese also had the highest CER.
- Routing can fail independently of transcription. In the sampled pipeline,
  some request transcripts matched their references but their intent labels
  were still wrong.
- A matched script or prompt can reduce one source of variation but cannot
  separate language from speaker, gender, dialect, or recording effects when
  speaker identifiers and matched recordings are unavailable.
- Census counts can show where potentially underserved language groups live,
  but they cannot be multiplied by pilot error rates and described as known
  misunderstood residents. The index is a prioritization aid, not a resident
  outcome estimate.
- TTS can provide a concrete multilingual prototype, but translation and
  pronunciation require fluent-speaker review, and effectiveness needs
  user-centered evaluation.

## What's next for ElevenLabs Track - Mississauga Unheard

1. Replenish the ElevenLabs Scribe credits and resume the cached benchmark for
   the remaining Accent Archive, MInDS-14, and Speech-MASSIVE recordings.
2. Recompute the Accent Archive group comparisons and expand spoken-request
   routing evaluation before drawing language-level conclusions.
3. Collect or create ethically reviewed, consented 311-style request examples
   for languages missing from the open request corpora; test intent accuracy
   and safe human fallback behavior.
4. Ask fluent Cantonese speakers to review the callback wording/audio, then
   test comprehension with community participants before considering service
   use.
5. Improve geographic estimates with language-specific service outcomes and
   validated methods for accounting for overlapping language populations.

The detailed findings and reproducibility outputs are in
[outputs/REPORT.md](outputs/REPORT.md). The root README remains unchanged.
