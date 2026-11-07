# Mississauga, Unheard

**ElevenLabs Track · Sheridan Datathon 2026 · November 7-8 · Sheridan College, Hazel McCallion Campus**

## The problem

Mississauga is one of the most linguistically diverse cities in Canada. In the 2021 Census, tens of thousands of residents speak Urdu, Arabic, Mandarin, Punjabi, Polish, Tagalog, Spanish, Tamil, Vietnamese, Hindi, Portuguese and more most often at home, and thousands can't hold a conversation in English or French.

More and more city services are answered by voice AI: phone menus, 311 lines, chatbots that listen. If the AI can't understand you, you go unheard.

**Your challenge:** using real speech and city data, find out **which Mississauga residents are least likely to be understood by voice AI, how many of them there are, and where they live**. Then use ElevenLabs to show what would close the gap.

Every recording in this pack is real human speech.

## What's in the pack

| Folder | What it is | Size |
|---|---|---|
| `01_people_census/` | Who speaks what, where: Mississauga 2021 Census by ward (11) and neighbourhood (56) | small |
| `02_speech_home_languages_FLEURS/` | The same 40 sentences read aloud in 13 home languages + English by real speakers, with transcripts (no Bengali) | 560 clips |
| `03_accented_english_SpeechAccentArchive/` | 423 people reading the same English paragraph, whose first language is Urdu, Punjabi, Tagalog, Arabic, Mandarin…, plus 45 Canadian English speakers as a baseline | 468 clips |
| `04_spoken_requests/minds14/` | Real people calling a bank's phone line with a request (pay a bill, freeze a card…). English, Polish, Portuguese, Spanish, Mandarin. 14 intents, phone quality | 1,050 clips |
| `04_spoken_requests/speech_massive/` | Real people giving voice-assistant commands, with intent labels and speaker background (first language, country of birth). Arabic, Polish, Portuguese, Spanish, Vietnamese | 575 clips |
| `05_city_311_requests/` | What residents call 311 about: every Toronto 311 request in 2025 (500K rows, by ward and type), plus Mississauga 311 daily call volumes (2017-2018) | 75 MB CSV |
| `language_crosswalk.csv` | Census column ↔ FLEURS ↔ Speech Accent Archive ↔ MInDS-14 ↔ Speech-MASSIVE ↔ language code | |

See `DATA_DICTIONARY.md` for every column and `LICENSES.md` for sources.

## Three ways in (do one, or connect them)

**1. Understood?** How well does speech-to-text handle each of Mississauga's languages (FLEURS) and accents (Speech Accent Archive)? Everyone reads the same text, but each FLEURS language was read by only a few speakers (Arabic, Punjabi and Urdu clips are all female; Portuguese, Tagalog and Vietnamese all male), so check whether a "language" effect is really a speaker effect. Which groups does AI fail most often, and why?

**2. Routed?** A 311 line has to figure out *what you need*. Using the real spoken requests (MInDS-14, Speech-MASSIVE), how often does a voice pipeline get the intent right in each language? What happens when it's wrong? Use the Toronto 311 data to see what kinds of requests a city line really gets.

**3. Who's unheard, and where?** Combine 1 or 2 with the census to build an Unheard Index per ward or neighbourhood, for example weighted by people who know neither official language, recent immigrants, or how urgent the calls are.

**Then close the loop with ElevenLabs.** Prototype the fix: a multilingual voice agent for 311, translated or dubbed city announcements, a callback in the caller's own language, or a better way to route accented English. Back it with your numbers.

## A gap worth noticing

There is no open dataset of people making service requests in Urdu, Punjabi, Tamil, Tagalog, Hindi or Gujarati, some of Mississauga's biggest communities. FLEURS and the Speech Accent Archive cover these languages, but the request datasets don't. How you work around that (translation, transfer from accented English, a small consented recording of your own) is part of the challenge.

## Judging

| Criterion | Weight |
|---|---|
| Strength of the data insight | 40% |
| Effective, creative use of ElevenLabs | 30% |
| Communication and storytelling | 20% |
| Feasibility and real-world impact | 10% |

Strong submissions use the audio, not only the tables, and are honest about limits (small samples, different dialects, banking calls vs city calls).

## Where to start

- Open `01_people_census/derived/language_coverage.csv` first: for each language, how many residents speak it and how much audio exists.
- `01_people_census/derived/geo_language_long.csv` is one row per ward/neighbourhood x language, joined to `language_crosswalk.csv`.
- Total audio: FLEURS ~1.6 h, accent ~3.7 h, MInDS-14 ~3.8 h, Speech-MASSIVE ~0.6 h. Every participant gets 1 month of ElevenLabs Creator, and credits are limited, so test on a few clips before running a full set.
- Report CER as well as WER: word boundaries in Urdu, Punjabi and Tamil are inconsistent, and Chinese has none. Urdu transcribed as Hindi, or Cantonese in Simplified characters, is worth reporting.
- ElevenLabs docs: https://elevenlabs.io/docs (Speech-to-Text / Scribe, Text-to-Speech, Dubbing, Agents)

## Good to know

- **Dialects differ.** FLEURS Portuguese is Brazilian, Spanish is Latin American and Arabic was recorded in Egypt. Mississauga's Portuguese community is mostly European/Azorean. MInDS-14 uses European Portuguese and Spanish; Speech-MASSIVE's Portuguese speakers were all born in Portugal, but about half its "es-ES" speakers were born in Mexico.
- **Census quirks.** Many of Ward 10's values are wrong in the City's raw ward table (e.g. Urdu = 50, though 7,225 Ward 10 residents have Urdu as mother tongue). Use `01_people_census/derived/ward_language_profile_2021_corrected.csv`, where Ward 10 is rebuilt from the neighbourhood table, or work at neighbourhood level. 17 of the 56 "neighbourhoods" are employment or airport areas with zero population.
- **Toronto ≠ Mississauga.** Toronto 311 is a stand-in for what a city line receives; Mississauga does not publish request-level 311 data.
- **Non-commercial data.** Some datasets are licensed for non-commercial use only (see `LICENSES.md`). That's fine for this event.
