from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).resolve().parent / "Mississauga_Unheard_Findings.pptx"

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
    header(slide, "The signal", "A measurable gap—and a clear caveat", "All 14 FLEURS language groups were processed; open request-audio coverage remains sparse.")
    metric_card(slide, 0.72, 2.08, 3.8, "26.43%", "Highest mean FLEURS CER", "Cantonese • 40 clips", TEAL)
    metric_card(slide, 4.77, 2.08, 3.8, "10,765", "Cantonese home-language speakers", "2021 census count", BLUE)
    metric_card(slide, 8.82, 2.08, 3.8, "659 / 2,653", "Clips transcribed so far", "Scribe quota stopped the full run", AMBER)
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
    header(slide, "01  /  Understood?", "Cantonese and Urdu stand out on CER", "Mean character error rate across 40 FLEURS clips per language; lower is better.")
    groups = [
        ("Cantonese", 26.4271, TEAL),
        ("Urdu", 20.5865, RED),
        ("Punjabi", 8.2493, AMBER),
        ("Hindi", 6.7597, BLUE),
        ("Mandarin Chinese", 2.9404, BLUE),
        ("Tamil", 2.6203, BLUE),
        ("Gujarati", 1.7254, BLUE),
        ("Spanish", 0.5666, BLUE),
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
    add_text(slide, "Matched prompt ID 1589: one clip per language. It controls text, not speaker, gender, or dialect.", 0.9, 6.18, 11.7, 0.45, 11, MUTED)
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
    header(slide, "03  /  Routed?", "Transcription is only one part of understanding", "The available request-audio sample is a smoke test; neither dataset is a Mississauga 311 corpus.")
    add_box(slide, 0.75, 2.08, 5.78, 3.75, PANEL)
    add_text(slide, "Audio → transcript → intent", 1.05, 2.38, 5.0, 0.38, 17, WHITE, True)
    add_text(slide, "MInDS-14", 1.08, 3.05, 1.65, 0.34, 13, MUTED, True)
    add_box(slide, 2.65, 3.08, 2.8, 0.28, GRID, rounded=False)
    add_box(slide, 2.65, 3.08, 2.8, 0.28, TEAL, rounded=False)
    add_text(slide, "5 / 5 correct", 5.55, 3.03, 0.75, 0.32, 11, TEAL, True)
    add_text(slide, "Speech-MASSIVE", 1.08, 3.82, 1.65, 0.34, 13, MUTED, True)
    add_box(slide, 2.65, 3.85, 2.8, 0.28, GRID, rounded=False)
    add_box(slide, 2.65, 3.85, 0.56, 0.28, AMBER, rounded=False)
    add_text(slide, "1 / 5 correct", 5.55, 3.8, 0.75, 0.32, 11, AMBER, True)
    add_text(slide, "Arabic qa → play • Polish recommendation → transport\nPortuguese play → transport • Vietnamese calendar → recommendation", 1.08, 4.6, 5.1, 0.85, 11, WHITE)
    add_box(slide, 6.83, 2.08, 5.72, 3.75, PANEL_ALT)
    add_text(slide, "Separate text-only baseline", 7.13, 2.38, 5.0, 0.38, 17, WHITE, True)
    add_text(slide, "MInDS-14", 7.15, 3.02, 1.8, 0.3, 13, MUTED, True)
    add_text(slide, "90.6–98.1%", 9.2, 2.96, 2.5, 0.42, 23, TEAL, True)
    add_text(slide, "Speech-MASSIVE", 7.15, 3.8, 1.8, 0.3, 13, MUTED, True)
    add_text(slide, "55.2–62.1%", 9.2, 3.74, 2.5, 0.42, 23, AMBER, True)
    add_text(slide, "Classifier input is reference text—not Scribe audio output. Tasks are banking and virtual-assistant labels, not city services.", 7.15, 4.55, 4.95, 0.9, 11, MUTED)
    add_text(slide, "Design implication: confirm the interpreted request and offer a human/alternate-language fallback.", 0.9, 6.15, 11.7, 0.42, 12, WHITE, True)
    footer(slide, 5, "Sources: outputs/audio_intent_evaluation.csv; outputs/intent_evaluation.csv; sample sizes n=1 per audio language.")

    # 6. Index
    slide = new_slide(prs)
    header(slide, "04  /  Where to prioritize?", "The index points to places for follow-up", "Higher scores combine language-group errors with census speaker counts; they are not failure probabilities.")
    add_box(slide, 0.75, 2.05, 5.72, 3.92, PANEL)
    add_text(slide, "Wards", 1.05, 2.35, 4.8, 0.36, 18, WHITE, True)
    add_text(slide, "Index score", 1.06, 2.8, 1.3, 0.28, 10, MUTED)
    ward_index = [("10", 23.096), ("7", 21.574), ("3", 21.359), ("4", 20.237), ("8", 19.398)]
    for i, (label, value) in enumerate(ward_index):
        bar_row(slide, f"Ward {label}", value, 1.08, 3.25 + 0.49 * i, 1.0, 3.25, f"{value:.1f}", 27, TEAL)
    add_box(slide, 6.82, 2.05, 5.72, 3.92, PANEL)
    add_text(slide, "Populated neighbourhoods", 7.1, 2.35, 4.9, 0.36, 18, WHITE, True)
    hood_index = [("Cooksville (East)", 25.449), ("Clarkson Village CN", 24.786), ("Churchill Meadows", 24.683), ("Sheridan CN", 23.817), ("Streetsville CN", 23.452)]
    for i, (label, value) in enumerate(hood_index):
        bar_row(slide, label, value, 7.12, 3.0 + 0.49 * i, 1.75, 2.25, f"{value:.1f}", 28, BLUE)
    add_text(slide, "Ward 7 has the largest ward-level weighted-error proxy (4,133.6); index leaders differ from proxy-count leaders.", 0.9, 6.2, 11.7, 0.4, 11, AMBER, True)
    footer(slide, 6, "Source: outputs/unheard_index.csv; 50 geographies. Full FLEURS CER + limited audio-intent evidence.")

    # 7. Prototype
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
    footer(slide, 7, "Generated with ElevenLabs TTS voice available to this account. No comprehension study has been run.")

    # 8. What next
    slide = new_slide(prs)
    header(slide, "Next steps", "The evidence is useful—and still incomplete", "The next phase should improve coverage before making service-level claims.")
    add_box(slide, 0.78, 2.02, 5.85, 3.98, PANEL)
    add_text(slide, "Remaining Scribe inventory", 1.08, 2.34, 4.9, 0.36, 17, WHITE, True)
    outstanding = [("Accent Archive", 379), ("MInDS-14", 1045), ("Speech-MASSIVE", 570)]
    for i, (name, value) in enumerate(outstanding):
        bar_row(slide, name, value, 1.1, 3.1 + i * 0.73, 1.55, 2.5, f"{value:,}", 1100, AMBER, bar_h=0.22)
    add_text(slide, "1,994 clips remain\n21 credits left; next clip needed ≥25", 1.1, 5.35, 4.95, 0.5, 12, AMBER, True)
    add_box(slide, 6.88, 2.02, 5.65, 3.98, PANEL)
    add_text(slide, "Recommended next", 7.2, 2.34, 4.7, 0.36, 17, WHITE, True)
    add_rich_lines(
        slide,
        [
            ("01  ", "Resume cached ASR after credits are replenished.", TEAL),
            ("02  ", "Create consented 311-style speech examples in missing languages.", BLUE),
            ("03  ", "Validate the Cantonese audio with fluent speakers and listeners.", AMBER),
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
    footer(slide, 8, "Detailed methods and caveats: outputs/REPORT.md • Original project README preserved.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
