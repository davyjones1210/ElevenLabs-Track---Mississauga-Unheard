import csv
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).resolve().parent / "Mississauga_Unheard_Findings.pptx"
WARD_MAP = Path(__file__).resolve().parent / "Mississauga_Unheard_Ward_Map.png"

W, H = 13.333, 7.5
BG = "0B1220"
PANEL = "141F31"
PANEL_ALT = "19263A"
WHITE = "F4F7FB"
MUTED = "A8B5C8"
TEAL = "41D6C3"
BLUE = "62A7FF"
AMBER = "FFBE5C"
RED = "FF7885"
GRID = "2B3A50"


DATASETS = {
    "fleurs": ("FLEURS", "02_speech_home_languages_FLEURS"),
    "accent": ("Accent Archive", "03_accented_english_SpeechAccentArchive"),
    "minds14": ("MInDS-14", "04_spoken_requests/minds14"),
    "massive": ("Speech-MASSIVE", "04_spoken_requests/speech_massive"),
}


def read_output(name):
    with (ROOT / "outputs" / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def current_findings():
    data_root = ROOT / "Mississauga_Unheard_ElevenLabs_Track"
    inventory = {}
    accent_language_inventory = {}
    for dataset, (_, folder) in DATASETS.items():
        with (data_root / folder / "metadata.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            metadata = list(csv.DictReader(stream))
            inventory[dataset] = len(metadata)
            if dataset == "accent":
                for row in metadata:
                    language = row["language"]
                    accent_language_inventory[language] = (
                        accent_language_inventory.get(language, 0) + 1
                    )

    transcripts = read_output("asr_benchmark.csv")
    cached = {
        dataset: sum(row["dataset"] == dataset for row in transcripts)
        for dataset in DATASETS
    }
    fleurs = sorted(
        (row for row in read_output("asr_summary.csv") if row["dataset"] == "fleurs"),
        key=lambda row: float(row["mean_cer"]),
        reverse=True,
    )
    accent_summary = [
        row for row in read_output("asr_summary.csv") if row["dataset"] == "accent"
    ]
    intent_predictions = read_output("audio_intent_predictions.csv")
    audio_intent = {}
    for dataset in ("minds14", "massive"):
        samples = [row for row in intent_predictions if row["dataset"] == dataset]
        audio_intent[dataset] = (
            sum(row["correct"].casefold() == "true" for row in samples),
            len(samples),
        )
    text_intent = {}
    for dataset in ("minds14", "massive"):
        scores = [
            float(row["accuracy"])
            for row in read_output("intent_evaluation.csv")
            if row["dataset"] == dataset and row["status"] == "ok" and row["accuracy"]
        ]
        text_intent[dataset] = (min(scores), max(scores)) if scores else (0.0, 0.0)
    geographies = read_output("unheard_index.csv")
    wards = sorted(
        (
            row
            for row in geographies
            if row["geo_level"] == "ward" and row["unheard_index"]
        ),
        key=lambda row: float(row["unheard_index"]),
        reverse=True,
    )
    neighbourhoods = sorted(
        (
            row
            for row in geographies
            if row["geo_level"] == "neighbourhood"
            and row["unheard_index"]
            and int(float(row["population_language_base"])) > 0
        ),
        key=lambda row: float(row["unheard_index"]),
        reverse=True,
    )
    return {
        "inventory": inventory,
        "cached": cached,
        "total_inventory": sum(inventory.values()),
        "total_cached": len(transcripts),
        "fleurs": fleurs,
        "accent_inventory": accent_language_inventory,
        "accent_summary": accent_summary,
        "audio_intent": audio_intent,
        "text_intent": text_intent,
        "wards": wards,
        "neighbourhoods": neighbourhoods,
    }


def color(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value)


def add_box(slide, x, y, w, h, fill, rounded=True, line=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(
        shape_type, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color(fill)
    shape.line.fill.background() if line is None else None
    if line:
        shape.line.color.rgb = color(line)
    return shape


def add_text(
    slide,
    text,
    x,
    y,
    w,
    h,
    size=16,
    fill=WHITE,
    bold=False,
    font="Aptos",
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
    margin=0,
):
    box = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    for index, line in enumerate(text.split("\n")):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = line
        paragraph.alignment = align
        paragraph.space_after = Pt(3)
        for run in paragraph.runs:
            run.font.name = font
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color(fill)
    return box


def add_rich_lines(slide, lines, x, y, w, h, size=15, gap=7):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0)
    frame.margin_right = Inches(0)
    frame.margin_top = Inches(0)
    frame.margin_bottom = Inches(0)
    for index, (lead, body, accent) in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.space_after = Pt(gap)
        prefix = paragraph.add_run()
        prefix.text = lead
        prefix.font.name = "Aptos"
        prefix.font.size = Pt(size)
        prefix.font.bold = True
        prefix.font.color.rgb = color(accent)
        rest = paragraph.add_run()
        rest.text = body
        rest.font.name = "Aptos"
        rest.font.size = Pt(size)
        rest.font.color.rgb = color(WHITE)
    return box


def new_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color(BG)
    return slide


def header(slide, kicker, title, subtitle=None):
    add_text(slide, kicker.upper(), 0.65, 0.38, 6.5, 0.25, 10, TEAL, True)
    add_text(slide, title, 0.65, 0.78, 12, 0.55, 27, WHITE, True)
    if subtitle:
        add_text(slide, subtitle, 0.68, 1.42, 11.9, 0.48, 12, MUTED)
    add_box(slide, 0.65, 0.70, 0.42, 0.045, TEAL, rounded=False)


def footer(slide, page, source):
    add_box(slide, 0.65, 7.08, 12.02, 0.012, GRID, rounded=False)
    add_text(slide, source, 0.68, 7.14, 11.0, 0.18, 8, MUTED)
    add_text(slide, f"{page:02d}", 12.12, 7.12, 0.5, 0.2, 9, TEAL, True, align=PP_ALIGN.RIGHT)


def metric_card(slide, x, y, w, value, label, detail, accent):
    add_box(slide, x, y, w, 1.52, PANEL)
    add_box(slide, x, y, 0.06, 1.52, accent, rounded=False)
    add_text(slide, value, x + 0.24, y + 0.2, w - 0.42, 0.49, 28, accent, True)
    add_text(slide, label, x + 0.24, y + 0.74, w - 0.42, 0.3, 14, WHITE, True)
    add_text(slide, detail, x + 0.24, y + 1.08, w - 0.42, 0.34, 10, MUTED)


def bar_row(slide, label, value, x, y, label_w, bar_w, value_text, max_value, fill, bar_h=0.18):
    add_text(slide, label, x, y - 0.02, label_w, 0.26, 12, WHITE, True)
    bx = x + label_w + 0.12
    add_box(slide, bx, y + 0.02, bar_w, bar_h, GRID, rounded=False)
    add_box(
        slide,
        bx,
        y + 0.02,
        max(0.035, bar_w * value / max_value),
        bar_h,
        fill,
        rounded=False,
    )
    add_text(slide, value_text, bx + bar_w + 0.12, y - 0.03, 1.05, 0.26, 11, MUTED, True)


def build():
    findings = current_findings()
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    prs.core_properties.title = "Mississauga Unheard — Voice AI Findings"
    prs.core_properties.subject = "Speech recognition, 311 routing, census geography, and ElevenLabs prototype"
    prs.core_properties.author = "Mississauga Unheard project"

    # 1. Cover
    slide = new_slide(prs)
    add_box(slide, 9.0, -0.5, 4.8, 8.5, PANEL, rounded=False)
    add_box(slide, 9.6, 0.9, 2.8, 2.8, TEAL)
    add_box(slide, 10.3, 3.2, 3.4, 3.4, BLUE)
    add_box(slide, 8.7, 4.7, 2.2, 2.2, AMBER)
    add_text(slide, "ELEVENLABS TRACK  /  MISSISSAUGA", 0.78, 0.72, 7.8, 0.28, 11, TEAL, True)
    add_text(slide, "Who gets\nheard by voice AI?", 0.75, 1.55, 8.5, 1.65, 34, WHITE, True)
    add_text(
        slide,
        "Measured speech gaps, where affected language communities live,\n"
        "and a Cantonese callback prototype.",
        0.82,
        3.55,
        7.6,
        0.9,
        17,
        MUTED,
    )
    add_box(slide, 0.82, 5.22, 3.15, 0.52, PANEL_ALT)
    add_text(slide, "FLEURS  •  CENSUS  •  311  •  ELEVENLABS", 0.98, 5.36, 2.85, 0.18, 9, WHITE, True)
    add_text(slide, "Findings snapshot  |  November 2026", 0.82, 6.65, 5.5, 0.25, 10, MUTED)
    footer(slide, 1, "Exploratory analysis; not a resident-level failure estimate.")

    # 2. Executive findings
    slide = new_slide(prs)
    header(slide, "The signal", "A measurable gap—and a clear caveat", "All 14 FLEURS language groups were processed; request-audio coverage is shown separately.")
    lead_fleurs = findings["fleurs"][0]
    metric_card(slide, 0.72, 2.08, 3.8, f"{100 * float(lead_fleurs['mean_cer']):.2f}%", "Highest mean FLEURS CER", f"{lead_fleurs['language']} • {lead_fleurs['samples']} clips", TEAL)
    metric_card(slide, 4.77, 2.08, 3.8, "10,765", "Cantonese home-language speakers", "2021 census count", BLUE)
    metric_card(slide, 8.82, 2.08, 3.8, f"{findings['total_cached']:,} / {findings['total_inventory']:,}", "Clips transcribed", "Cached Scribe results across the inventory", AMBER)
    add_box(slide, 0.72, 4.12, 12.0, 1.9, PANEL)
    add_rich_lines(
        slide,
        [
            ("What we can say  ", "Cantonese has the highest CER in the completed FLEURS sample.", TEAL),
            ("What we cannot say  ", "That 26% of Cantonese callers—or 10,765 residents—will be misunderstood.", AMBER),
            ("Why  ", "FLEURS is read speech, with unmatched prompts and no speaker IDs; service-request audio is missing.", BLUE),
        ],
        1.0,
        4.42,
        11.3,
        1.4,
        size=14,
        gap=10,
    )
    footer(slide, 2, "Sources: outputs/asr_summary.csv; 2021 census-derived language counts; outputs/REPORT.md.")

    # 3. ASR performance
    slide = new_slide(prs)
    top_languages = " and ".join(row["language"] for row in findings["fleurs"][:2])
    header(slide, "01  /  Understood?", f"{top_languages} stand out on CER", "Mean character error rate across 40 FLEURS clips per language; lower is better.")
    accents = [TEAL, RED, AMBER] + [BLUE] * 5
    groups = [
        (row["language"], 100 * float(row["mean_cer"]), accents[index])
        for index, row in enumerate(findings["fleurs"][:8])
    ]
    for i, (name, value, accent) in enumerate(groups):
        bar_row(slide, name, value, 0.88, 2.12 + 0.48 * i, 1.55, 6.75, f"{value:.2f}%", 30, accent)
    add_box(slide, 9.9, 2.1, 2.55, 3.85, PANEL)
    add_text(slide, "Read this carefully", 10.15, 2.4, 2.1, 0.36, 15, AMBER, True)
    add_text(
        slide,
        "Mandarin and Cantonese WER is near 100% because word boundaries/tokenization differ.\n\n"
        "CER is more informative here. Cantonese also has the highest CER, not just a WER artifact.\n\n"
        "FLEURS is read speech—not live 311 calls.",
        10.15,
        2.95,
        2.05,
        2.55,
        12,
        MUTED,
    )
    accent_processed = sum(int(row["samples"]) for row in findings["accent_summary"])
    add_text(
        slide,
        f"Accent Archive: {accent_processed:,}/{findings['inventory']['accent']:,} English-accent clips processed.",
        0.9,
        5.91,
        11.7,
        0.28,
        11,
        AMBER,
        True,
    )
    add_text(slide, "Matched prompt ID 1589: one clip per language. It controls text, not speaker, gender, or dialect.", 0.9, 6.23, 11.7, 0.35, 10, MUTED)
    footer(slide, 3, "Source: outputs/asr_summary.csv and outputs/paired_fleurs_summary.csv; normalized CER/WER.")

    # 4. Population geography
    slide = new_slide(prs)
    header(slide, "02  /  Who and where?", "Cantonese speakers are present across the city", "The census identifies potential reach for better language access—not individual outcomes.")
    add_box(slide, 0.75, 2.05, 5.75, 3.8, PANEL)
    add_text(slide, "Largest ward counts", 1.02, 2.32, 4.8, 0.32, 17, WHITE, True)
    ward_values = [("Ward 6", 2520), ("Ward 5", 1270), ("Ward 4", 1125), ("Ward 8", 1105), ("Ward 11", 1095)]
    for i, (label, value) in enumerate(ward_values):
        bar_row(slide, label, value, 1.05, 2.98 + i * 0.48, 1.0, 2.95, f"{value:,}", 2700, TEAL)
    add_text(slide, "10,765", 5.05, 2.28, 1.15, 0.48, 22, TEAL, True, align=PP_ALIGN.RIGHT)
    add_text(slide, "citywide Cantonese speakers", 4.15, 2.78, 2.0, 0.3, 9, MUTED, align=PP_ALIGN.RIGHT)

    add_box(slide, 6.82, 2.05, 5.75, 3.8, PANEL)
    add_text(slide, "Largest neighbourhood counts", 7.1, 2.32, 4.7, 0.32, 17, WHITE, True)
    hood_values = [("East Credit", 2225), ("Hurontario", 1520), ("Central Erin Mills", 1095), ("Churchill Meadows", 905), ("DT Core", 630)]
    for i, (label, value) in enumerate(hood_values):
        bar_row(slide, label, value, 7.12, 2.98 + i * 0.48, 1.7, 2.35, f"{value:,}", 2400, BLUE)
    add_text(slide, "Counts are home-language speakers and may overlap with other language counts.", 0.9, 6.18, 11.7, 0.42, 11, MUTED)
    footer(slide, 4, "Source: 01_people_census/derived/geo_language_long.csv (corrected derived geography).")

    # 5. Intent pipeline
    slide = new_slide(prs)
    header(slide, "03  /  Routed?", "Transcription is only one part of understanding", "The request-audio corpora are banking and voice-assistant data, not Mississauga 311 calls.")
    add_box(slide, 0.75, 2.08, 5.78, 3.75, PANEL)
    add_text(slide, "Audio → transcript → intent", 1.05, 2.38, 5.0, 0.38, 17, WHITE, True)
    minds_correct, minds_total = findings["audio_intent"]["minds14"]
    massive_correct, massive_total = findings["audio_intent"]["massive"]
    add_text(slide, "MInDS-14", 1.08, 3.05, 1.65, 0.34, 13, MUTED, True)
    add_box(slide, 2.65, 3.08, 2.8, 0.28, GRID, rounded=False)
    add_box(slide, 2.65, 3.08, 2.8 * minds_correct / minds_total if minds_total else 0, 0.28, TEAL, rounded=False)
    add_text(slide, f"{minds_correct:,} / {minds_total:,} correct", 5.55, 3.03, 0.9, 0.32, 11, TEAL, True)
    add_text(slide, "Speech-MASSIVE", 1.08, 3.82, 1.65, 0.34, 13, MUTED, True)
    add_box(slide, 2.65, 3.85, 2.8, 0.28, GRID, rounded=False)
    add_box(slide, 2.65, 3.85, 2.8 * massive_correct / massive_total if massive_total else 0, 0.28, AMBER, rounded=False)
    add_text(slide, f"{massive_correct:,} / {massive_total:,} correct", 5.55, 3.8, 0.9, 0.32, 11, AMBER, True)
    add_text(slide, "Audio transcripts are classified against dataset labels. These remain banking and virtual-assistant tasks, not city services.", 1.08, 4.6, 5.1, 0.85, 11, WHITE)
    add_box(slide, 6.83, 2.08, 5.72, 3.75, PANEL_ALT)
    add_text(slide, "Separate text-only baseline", 7.13, 2.38, 5.0, 0.38, 17, WHITE, True)
    add_text(slide, "MInDS-14", 7.15, 3.02, 1.8, 0.3, 13, MUTED, True)
    minds_low, minds_high = findings["text_intent"]["minds14"]
    add_text(slide, f"{100 * minds_low:.1f}–{100 * minds_high:.1f}%", 9.2, 2.96, 2.5, 0.42, 23, TEAL, True)
    add_text(slide, "Speech-MASSIVE", 7.15, 3.8, 1.8, 0.3, 13, MUTED, True)
    massive_low, massive_high = findings["text_intent"]["massive"]
    add_text(slide, f"{100 * massive_low:.1f}–{100 * massive_high:.1f}%", 9.2, 3.74, 2.5, 0.42, 23, AMBER, True)
    add_text(slide, "Classifier input is reference text—not Scribe audio output. Tasks are banking and virtual-assistant labels, not city services.", 7.15, 4.55, 4.95, 0.9, 11, MUTED)
    add_text(slide, "Design implication: confirm the interpreted request and offer a human/alternate-language fallback.", 0.9, 6.15, 11.7, 0.42, 12, WHITE, True)
    footer(slide, 5, "Sources: outputs/audio_intent_evaluation.csv; outputs/intent_evaluation.csv; sample sizes n=1 per audio language.")

    # 6. Index
    slide = new_slide(prs)
    header(slide, "04  /  Where to prioritize?", "The index points to places for follow-up", "Higher scores combine language-group errors with census speaker counts; they are not failure probabilities.")
    add_box(slide, 0.75, 2.05, 5.72, 3.92, PANEL)
    add_text(slide, "Wards", 1.05, 2.35, 4.8, 0.36, 18, WHITE, True)
    add_text(slide, "Index score", 1.06, 2.8, 1.3, 0.28, 10, MUTED)
    ward_index = [
        (row["geo"], float(row["unheard_index"]))
        for row in findings["wards"][:5]
    ]
    for i, (label, value) in enumerate(ward_index):
        bar_row(slide, f"Ward {label}", value, 1.08, 3.25 + 0.49 * i, 1.0, 3.25, f"{value:.1f}", 27, TEAL)
    add_box(slide, 6.82, 2.05, 5.72, 3.92, PANEL)
    add_text(slide, "Populated neighbourhoods", 7.1, 2.35, 4.9, 0.36, 18, WHITE, True)
    hood_index = [
        (row["geo"], float(row["unheard_index"]))
        for row in findings["neighbourhoods"][:5]
    ]
    for i, (label, value) in enumerate(hood_index):
        bar_row(slide, label, value, 7.12, 3.0 + 0.49 * i, 1.75, 2.25, f"{value:.1f}", 28, BLUE)
    add_text(slide, "Ward 7 has the largest ward-level weighted-error proxy (4,133.6); index leaders differ from proxy-count leaders.", 0.9, 6.2, 11.7, 0.4, 11, AMBER, True)
    footer(slide, 6, "Source: outputs/unheard_index.csv; 50 geographies. Full FLEURS CER + limited audio-intent evidence.")

    # 7. Ward-level map
    slide = new_slide(prs)
    header(
        slide,
        "04  /  Where to prioritize?",
        "A geographic view of the exploratory index",
        "Ward boundaries with population-weighted benchmark signals; not observed caller failures.",
    )
    slide.shapes.add_picture(
        str(WARD_MAP), Inches(0.65), Inches(1.82), height=Inches(5.05)
    )
    metric_card(
        slide,
        5.02,
        2.03,
        3.55,
        "23.096",
        "Highest ward index",
        "Ward 10 • 23.31% coverage",
        TEAL,
    )
    metric_card(
        slide,
        8.82,
        2.03,
        3.55,
        "4,133.6",
        "Largest proxy count",
        "Ward 7 • not known failed calls",
        AMBER,
    )
    add_box(slide, 5.02, 3.82, 7.35, 1.18, PANEL_ALT)
    add_text(slide, "Neighbourhood signal", 5.3, 4.04, 2.8, 0.32, 16, WHITE, True)
    add_text(
        slide,
        "Cooksville (East)  •  index 25.449  •  11.96% coverage",
        5.3,
        4.45,
        6.75,
        0.3,
        13,
        BLUE,
        True,
    )
    add_box(slide, 5.02, 5.2, 7.35, 1.35, PANEL)
    add_text(
        slide,
        "Interpret with care",
        5.3,
        5.43,
        2.4,
        0.3,
        15,
        AMBER,
        True,
    )
    add_text(
        slide,
        "The index combines available FLEURS CER and pilot intent errors. "
        "The request-audio pilot has only one clip per language; scores are "
        "not service-level outcomes or resident-level risk.",
        5.3,
        5.82,
        6.65,
        0.55,
        11,
        MUTED,
    )
    footer(
        slide,
        7,
        "Boundaries: City of Mississauga Ward Boundaries service. "
        "Scores: 2021 census-derived outputs/unheard_index.csv; verify boundary crosswalk.",
    )

    # 8. Prototype
    slide = new_slide(prs)
    header(slide, "05  /  Close the loop", "A Cantonese callback proof of concept", "TTS gives the measured gap a tangible response—but it does not prove service effectiveness.")
    add_box(slide, 0.78, 2.05, 7.0, 3.95, PANEL)
    add_text(slide, "CANTONESE  /  TRADITIONAL CHARACTERS", 1.15, 2.4, 5.9, 0.28, 10, TEAL, True)
    add_text(slide, "你好，我哋收到你嘅請求。", 1.13, 3.02, 6.15, 0.72, 27, WHITE, True)
    add_text(slide, "“Hello, we received your request.”", 1.16, 3.92, 5.8, 0.4, 17, MUTED)
    add_box(slide, 1.15, 4.85, 5.95, 0.68, PANEL_ALT)
    add_text(slide, "Audio: outputs/311_callback_yue.mp3  •  39,749 bytes", 1.38, 5.08, 5.55, 0.22, 11, WHITE, True)
    add_box(slide, 8.1, 2.05, 4.45, 3.95, PANEL_ALT)
    add_text(slide, "Before any real use", 8.45, 2.42, 3.7, 0.36, 18, AMBER, True)
    add_rich_lines(
        slide,
        [
            ("1  ", "Fluent Cantonese review of translation and pronunciation.", TEAL),
            ("2  ", "Test comprehension with community participants.", BLUE),
            ("3  ", "Keep human assistance available; TTS is not automatic translation.", AMBER),
        ],
        8.45,
        3.08,
        3.55,
        2.25,
        size=13,
        gap=12,
    )
    footer(slide, 8, "Generated with ElevenLabs TTS voice available to this account. No comprehension study has been run.")

    # 9. What next
    slide = new_slide(prs)
    header(slide, "Next steps", "The evidence is useful—and still incomplete", "The next phase should improve coverage before making service-level claims.")
    add_box(slide, 0.78, 2.02, 5.85, 3.98, PANEL)
    add_text(slide, "Remaining Scribe inventory", 1.08, 2.34, 4.9, 0.36, 17, WHITE, True)
    outstanding = [
        (DATASETS[dataset][0], findings["inventory"][dataset] - findings["cached"][dataset])
        for dataset in ("accent", "minds14", "massive")
    ]
    for i, (name, value) in enumerate(outstanding):
        bar_row(slide, name, value, 1.1, 3.1 + i * 0.73, 1.55, 2.5, f"{value:,}", 1100, AMBER, bar_h=0.22)
    remaining = sum(value for _, value in outstanding)
    add_text(slide, f"{remaining:,} clips remain\nCached results are preserved for resume.", 1.1, 5.35, 4.95, 0.5, 12, AMBER, True)
    add_box(slide, 6.88, 2.02, 5.65, 3.98, PANEL)
    add_text(slide, "Recommended next", 7.2, 2.34, 4.7, 0.36, 17, WHITE, True)
    add_rich_lines(
        slide,
        [
            ("01  ", "Expand consented 311-style speech examples in missing languages.", TEAL),
            ("02  ", "Validate transcripts and routing with fluent speakers.", BLUE),
            ("03  ", "Test translation, callback comprehension, and human fallback.", AMBER),
            ("04  ", "Revisit geography scores with service-specific outcome evidence.", RED),
        ],
        7.22,
        3.02,
        4.75,
        2.55,
        size=13,
        gap=10,
    )
    add_text(slide, "Treat these findings as a prioritization signal—not as a count of residents already misunderstood.", 0.9, 6.22, 11.7, 0.42, 12, WHITE, True)
    footer(slide, 9, "Detailed methods and caveats: outputs/REPORT.md • Original project README preserved.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
