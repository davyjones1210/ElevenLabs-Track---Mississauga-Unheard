# ElevenLabs Track - Mississauga Unheard

## Inspiration

Mississauga is multilingual, but a voice service can fail residents at two
different steps: recognizing what they say and routing the request correctly.
This project explores where speech benchmarks signal potential language-access
barriers, how those signals intersect with census geography, and how a safer
multilingual 311 voice workflow could be evaluated. It demonstrates a short
ElevenLabs text-to-speech callback; it does not yet implement a 311 assistant.

The guiding questions are:

- Which language and accent groups show the largest speech-recognition errors?
- How reliably do speech datasets' requests reach the correct intent or
  scenario?
- Where do speakers of languages with weaker measured results live?
- Could a callback in a resident's language help close part of the service gap?

The project follows four stages: measure speech-recognition gaps; estimate
potential population reach using census geography; design a multilingual
service workflow; and demonstrate how that workflow could be evaluated against
a human-reviewed baseline. Only the benchmark, exploratory index, and short
text-to-speech callback are implemented today.

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

The exploratory Unheard Index ranks Ward 10 highest among wards (23.096) and
Cooksville (East) highest among populated neighbourhoods (25.449). It
population-weights available language risk scores, averaging FLEURS CER with
spoken-request intent error where both are available. The intent evidence is
very limited, so the scores are prioritization proxies, not counts or
probabilities of residents experiencing failed calls. The current score has no
service-urgency weight: the Toronto request data contains no language or
urgency labels.

The [ward map](slides/Mississauga_Unheard_Ward_Map.png) overlays the index on
the [City of Mississauga's public ward boundaries](https://www.arcgis.com/home/item.html?id=f1cad02b3a40422dac2ea99b59cc36a5).
It highlights Ward 10's highest index and Ward 7's largest weighted-error
proxy; the two measures answer different questions. The boundary layer is the
City's current municipal boundary service, while the score is joined by ward
number to 2021-census-derived data. Validate that geography crosswalk before
operational use. Mapped values are exploratory and do not represent known
caller outcomes. Check the City's [terms of use](https://smartcity.mississauga.ca/wp-content/uploads/2021/04/CityofMississauga_TermsofUse.pdf)
before external republication.

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

## Proposed 311 voice-assistant workflow

The following is a design direction, not implemented product functionality.
The current project has a resumable transcription benchmark, offline intent
baselines, geographic summaries, and a short TTS callback. It does not have a
connected ElevenLabs Agent, a Mississauga service-catalogue integration, live
311 telephony, automatic translation, or an end-to-end city-request test.

| Stage | Proposed behavior | Safety and accessibility guardrail |
|---|---|---|
| 1. Start and choose language | A caller reaches 311, selects or says a preferred language, and can request a human at any point. | Keep language selection easy to repeat; provide an accessible route for callers who cannot use speech. |
| 2. Recognize speech | ElevenLabs Scribe converts the request to text in a supported language. | Treat recognition as uncertain; protect transcripts and audio, minimize retention, and disclose recording and processing before collecting them. |
| 3. Identify the service | An intent component matches the transcript to an approved Mississauga service and gathers only the details needed for that request. | Use the City's maintained service information, not Toronto request counts as a routing catalogue. Do not treat benchmark labels as validated city intents. |
| 4. Confirm before action | The assistant reads back the interpreted request and proposed destination in the caller's preferred language, then asks the caller to confirm or correct it. | Do not submit or dispatch a request until the caller confirms. Offer repeat, correction, and human fallback when recognition or intent confidence is low. |
| 5. Respond and route | ElevenLabs text-to-speech can speak an approved response; a confirmed request can be handed to the authorized department or a human representative. | Use reviewed translations and city-approved instructions. Preserve a clear human path and follow official procedures for emergency or out-of-scope requests. |
| 6. Close the loop | Provide a reference number or next step in speech and another accessible format where possible. | Audit failures and handoffs with privacy controls; never claim resolution until the receiving service confirms it. |

ElevenLabs Agents could be evaluated later as the conversation-orchestration
layer, with Scribe for speech recognition and Text-to-Speech for spoken
responses. Dubbing may help publish reviewed, prerecorded municipal
announcements in more languages, but it is not a substitute for an interactive
request-and-confirm workflow. Each component would need separate usability,
translation, privacy, security, and service-routing validation.

## Evaluation plan

Before any service pilot, co-design test scenarios with residents and fluent
speakers, then run a consented, human-reviewed evaluation using representative
311-style requests across languages, accents, devices, and noisy conditions.
Compare the proposed flow with a human-reviewed baseline and report results by
language, including:

- WER and CER against verified transcripts, plus language-identification
  failures;
- intent and destination accuracy, unsupported-request detection, caller
  corrections, and erroneous or duplicate submissions;
- successful completion, human handoff, abandonment, and time to resolution;
- performance with common accessibility needs and noisy or interrupted calls;
- privacy, security, retention, and auditability under City-approved policy.

Set acceptance thresholds with the City and community participants before
testing. A low average error rate must not conceal a high-impact failure for a
smaller language group. The open banking and voice-assistant corpora in this
project are development smoke tests, not evidence that a 311 assistant is
ready for residents.

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

The latest run cached 989/2,653 clips: all 560 FLEURS clips, 419 Accent
Archive clips, and five clips each from MInDS-14 and Speech-MASSIVE. It stopped
with 14 ElevenLabs credits remaining when the next Scribe request required 22.
The 1,664 outstanding clips are resumable after adding quota. The API key must
have the `speech_to_text` permission.

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

- **API credits:** The full inventory is 2,653 clips. Scribe results are
  cached for 989: all 560 FLEURS clips, 419 of 468 Accent Archive clips, five
  of 1,050 MInDS-14 clips, and five of 575 Speech-MASSIVE clips. The latest
  run stopped when ElevenLabs reported 14 credits remaining and 22 required
  for the next request. The remaining 1,664 clips are not processed yet.
- **Language and speaker effects:** The matched FLEURS prompt controls text
  content for only one clip per language. Speaker IDs are unavailable, and
  gender and dialect differ across groups. The full 40-clip language groups
  also do not all contain matched prompts.
- **Metric comparability:** Chinese character spacing can produce near-100%
  WER even when CER is lower. CER is necessary alongside WER and is the
  primary comparison used here for scripts with inconsistent word boundaries.
- **Accent coverage:** The Speech Accent Archive is still incomplete, with
  419/468 clips processed across all 15 first-language groups (423 non-native
  English recordings and 45 Canadian-English baseline recordings in the
  supplied inventory). Among groups with at least ten clips, Mandarin
  Chinese had the highest mean CER (4.33%, 40 clips), followed by Arabic
  (4.18%, 40), Punjabi (3.90%, 11), and Cantonese (2.79%, 35). These
  descriptive results do not isolate accent from speaker or recording
  effects.
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
- Expanded Speech Accent Archive coverage from 89 to 419 of 468 clips; the
  full per-group transcript scores are in `outputs/asr_summary.csv`.
- Identified Cantonese as the highest measured FLEURS CER group and connected
  that finding to census counts by ward and neighbourhood.
- Corrected the index to use all available FLEURS clip-level CER results when
  present, rather than preferring the smaller matched-prompt summary.
- Built a resumable benchmark that writes results incrementally, allowing
  completed work to be retained when API credits run out.
- Generated an ElevenLabs Cantonese acknowledgment for the highest-CER group.
- Mapped the exploratory ward index using the City of Mississauga's public
  ward-boundary service; the mapped scores remain proxies, not resident
  outcomes.
- Preserved the supplied root [README.md](README.md) unchanged.
- Passed all 12 unit tests after the findings refresh.

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

1. **Finish the benchmark:** add Scribe quota and resume the cached run for
   the remaining 49 Accent Archive, 1,045 MInDS-14, and 570 Speech-MASSIVE
   clips. Refresh the analysis and label these corpora as proxies, not 311
   requests.
2. **Design the service workflow with residents and City staff:** settle
   language choice, service-intent taxonomy, confirmation wording, accessible
   interaction, privacy and retention policy, and when/how to transfer to a
   person before selecting an automated routing design.
3. **Build a contained prototype:** evaluate Scribe for speech recognition,
   an intent-to-service matcher grounded in City-approved information, and
   reviewed ElevenLabs TTS responses. Require caller confirmation before
   submission; support corrections and human fallback. Treat ElevenLabs
   Agents as a candidate orchestration layer, not a feature already present in
   this project.
4. **Validate before a live pilot:** collect consented, representative
   311-style examples with fluent-speaker references; compare the human
   baseline and prototype by language; predefine thresholds for recognition,
   intent, routing, task completion, fallback, latency, accessibility, and
   privacy. Test unsafe and out-of-scope requests and verify every service
   handoff.
5. **Review the callback and translated content:** have fluent Cantonese
   speakers review wording and pronunciation, then test comprehension with
   community participants. Consider Dubbing only for reviewed, prerecorded
   announcements.
6. **Strengthen the geography:** verify the current-boundary/2021-census
   ward crosswalk, increase language-specific service-outcome coverage, and
   account for overlapping language populations. Add service urgency only
   when reliable service-level labels are available; the current index does
   not use an urgency weight.

The detailed findings and reproducibility outputs are in
[outputs/REPORT.md](outputs/REPORT.md). The root README remains unchanged.
