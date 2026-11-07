# Data dictionary

All audio is mono. FLAC files open in Audacity, VLC, Python (`soundfile`, `librosa`) and are accepted by ElevenLabs Scribe.

## 01_people_census/

**`ward_language_profile_2021.csv`** (11 rows) and **`neighbourhood_language_profile_2021.csv`** (56 rows; 17 are employment or airport areas with population 0). Neighbourhood suffixes are City planning "character areas": CN community node, MN major node, CC corporate centre, EA employment area, SPA special purpose area, DT downtown. **Ward 10's values are wrong in the source; use `derived/ward_language_profile_2021_corrected.csv`.** In `raw/2021 Census - By Ward.csv`, Ward 10 is also wrong for citizenship, place of birth, visible minority, ethnic origin, generation status and labour force, so don't use raw Ward 10 values. `derived/geo_language_long.csv` is the same data in long form (geo x language), joined to the crosswalk.

| Column | Meaning |
|---|---|
| `ward` / `neighbourhood` | Mississauga ward number (1-11) or neighbourhood name |
| `population_total` | Total population from the census age table. It doesn't always match the other counts at neighbourhood level, so use `population_language_base` as the denominator |
| `population_language_base` | Population counted for "language spoken most often at home" (use as denominator) |
| `knows_neither_english_nor_french` | Residents who cannot conduct a conversation in either official language |
| `pct_knows_neither_english_nor_french` | Same, as a % |
| `immigrants`, `recent_immigrants_2016_2021` | Immigrant population; arrived 2016-2021 |
| `median_total_income_2020` | Median total income in 2020 ($) of persons not in economic families (people living alone or with non-relatives), not the general median |
| `top14_nonofficial_home_language_speakers` | Sum of the 14 language columns below |
| `home_<language>` | Residents who speak that language most often at home (urdu, arabic, mandarin, punjabi, polish, cantonese, tagalog, spanish, tamil, vietnamese, hindi, portuguese, gujarati, bengali) |

`raw/` has the City's full tables and `2021_Census_Legend.pdf`, which explains every variable code.

## 02_speech_home_languages_FLEURS/ · `metadata.csv` (560 rows)

40 sentences (same `fleurs_id` = same sentence in every language) × 14 languages, 16 kHz FLAC.

| Column | Meaning |
|---|---|
| `file` | Path to the audio, relative to this folder |
| `language`, `lang_config`, `iso639_1` | Language name, FLEURS config, language code (two-letter ISO 639-1, except Cantonese, which uses `yue`) |
| `variety_note` | Dialect/script notes (e.g. Brazilian Portuguese) |
| `fleurs_id` | Sentence ID, shared across languages |
| `gender`, `duration_sec` | Speaker gender, clip length. No speaker ID is given; each language has few speakers, and several languages are one gender only |
| `transcription` | Normalised reference transcript (lower-case, no punctuation) |
| `raw_transcription` | Reference transcript as written |

## 03_accented_english_SpeechAccentArchive/ · `metadata.csv` (468 rows)

Everyone reads the paragraph in `elicitation_paragraph.txt`. MP3.

| Column | Meaning |
|---|---|
| `file` | Path to the audio |
| `language` | The speaker's first language, matching `language_crosswalk.csv` (they are all speaking English) |
| `native_language`, `alternative_native_language` | As recorded by the archive |
| `birth_city`, `birth_state_or_province`, `birth_country` | Where the speaker was born |
| `age`, `gender` | |
| `english_onset_age` | Age they started learning English |
| `english_residence`, `length_of_english_residence_years` | Where/how long they've lived in an English-speaking country |
| `learning_style` | How they learned English (academic / naturalistic) |
| `duration_sec` | Clip length |

Speakers per first language (`language` values): English 45 (all born in Canada), Arabic 40, Mandarin Chinese 40, Spanish 40, Portuguese 40, Vietnamese 39, Polish 38, Cantonese 35, Hindi 34, Urdu 29, Tagalog 29, Bengali 21, Gujarati 17, Punjabi 11, Tamil 10.

## 04_spoken_requests/minds14/ · `metadata.csv` (1,050 rows)

Real phone calls to a bank's e-banking line, phone-quality FLAC. 15 calls per intent per locale. 10 calls in non-English locales are actually in English (Polish 4, Portuguese 3, Mandarin 3).

| Column | Meaning |
|---|---|
| `file`, `locale`, `language` | Audio path; en-US, pl-PL, pt-PT, es-ES, zh-CN |
| `intent` | One of 14: abroad, address, app_error, atm_limit, balance, business_loan, card_issues, cash_deposit, direct_debit, freeze, high_value_payment, joint_account, latest_transactions, pay_bill |
| `transcription` | What the caller said, as provided with the dataset (may itself contain transcription errors) |
| `english_transcription` | English translation |

## 04_spoken_requests/speech_massive/ · `metadata.csv` (575 rows)

Voice-assistant commands (115 per language; all 60 intents appear, 1-5 clips each, so analyse by the 18 `scenario`s; 7-8 speakers per language), 16 kHz FLAC.

| Column | Meaning |
|---|---|
| `file`, `locale`, `language` | ar-SA, pl-PL, pt-PT, es-ES, vi-VN |
| `scenario`, `intent` | e.g. `transport` / `transport_ticket` (18 scenarios, 60 intents) |
| `utterance`, `annotated_utterance` | Reference text; slot-annotated version |
| `speaker_*` | Speaker ID, sex, age, first language, country of birth, country of residence |

## 05_city_311_requests/

**`toronto_311_requests_2025.csv`** (500,269 rows): every customer-initiated Toronto 311 service request in 2025.

| Column | Meaning |
|---|---|
| `created`, `status` | Timestamp; current status |
| `postal_fsa` | First 3 characters of the postal code, or the literal "Intersection" |
| `intersection_street_1/2` | Nearest intersection, when given |
| `ward` | Toronto ward (25-ward model) |
| `service_request_type`, `division`, `section` | What the request was about and who handles it |

`toronto_311_request_types_2025.csv` and `toronto_311_ward_by_division_2025.csv` are pre-counted summaries.

**`Mississauga_311_Call_Data_2017.csv` / `_2018.csv`**: daily calls offered/answered/abandoned, handle time and speed of answer at Mississauga's 311 contact centre, business days only. The two years differ: headers (2018 is upper-case), dates (2017 dd/mm/yyyy, 2018 m/d/yyyy), and percentages (2018 stores "97%" as text). Holidays appear as text in `Calls_Offered` (e.g. "Family Day"). 2017 has typo dates ("29/112/2017", "2107", "07/07//2017", and "10/07/2018" for a 2017 day) and 44 blank rows spread through the file. Neither file is in date order. Read with `encoding="utf-8-sig"`.

## language_crosswalk.csv

One row per language with the matching key in every dataset. Blank = not available in that dataset. Speech Accent Archive Tagalog speakers appear as `tagalog` or `filipino` in `native_language`, so join on `language`.

| Column | Meaning |
|---|---|
| `language` | Language name, as used across the pack |
| `census_home_column` | Matching `home_<language>` column in the census tables |
| `fleurs_config` | FLEURS language config (e.g. `ur_pk`) |
| `speech_accent_archive_native_language` | `native_language` value in the Speech Accent Archive |
| `minds14_locale` | MInDS-14 locale (e.g. `pl-PL`) |
| `speech_massive_locale` | Speech-MASSIVE locale (e.g. `vi-VN`) |
| `iso639_1` | Language code: two-letter ISO 639-1, except Cantonese, which uses `yue` |

## 01_people_census/derived/

| File / column | Meaning |
|---|---|
| `ward_language_profile_2021_corrected.csv` | Ward table with Ward 10 rebuilt (Ward 10 = sum of neighbourhoods minus Wards 1-9 and 11). `ward10_corrected` = TRUE on that row. Counts are rounded to 5 by StatCan, so Ward 10 values carry about +/-50 noise |
| `geo_language_long.csv` | One row per ward or populated neighbourhood x language, joined to `language_crosswalk.csv` |
| `geo_level`, `geo` | "ward" or "neighbourhood", and its name/number |
| `home_speakers` | Residents who speak that language most often at home |
| `pct_of_geo` | home_speakers / population_language_base x 100 |
| `share_of_city_speakers` | % of the city's speakers of that language living in this geo (within the same geo_level) |
| `language_coverage.csv` | One row per language: `city_home_speakers` (from neighbourhoods), clips in each speech dataset, `has_service_request_audio` (any MInDS-14 or Speech-MASSIVE clips) |
