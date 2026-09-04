#!/usr/bin/env python3
"""Render the v4 tree proposal as a SHUFFLEABLE PowerPoint deck.

Owner's request, 2026-09-04: *"a Powerpoint presentation with each technology
as a small box I can shuffle around. Each of the current tech trees should be
their own slide. Array the little boxes in the order of technology bin
development left (primitive) to right (advanced)."*

Reads restructured_model_v4.json (same source as build_tree_visual_v4.py) and
writes research_trees_boxes.pptx. Each research row is one INDIVIDUAL shape —
movable, editable, deletable in PowerPoint or Google Slides. Boxes sit in five
tier columns (T0 primitive … T4 advanced), cost-sorted within a tier.

⚠️ Once the owner has shuffled the deck, the .pptx holds HIS decisions and this
generator must not be re-run over it — write to a new filename instead.

Run from repo root:  python3 design/Jawa/research_review/build_tree_pptx.py
"""
import json
import os
import sys

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "restructured_model_v4.json")
OUT = os.path.join(HERE, "research_trees_boxes.pptx")

# Slide order and accents — same roster as build_tree_visual_v4.py.
TREES = [
    ("Scavenger", "c2a06a", "the pride-free floor — fire, water, food, hide, door, trap"),
    ("The Hearth", "b98a4e", "comfort & culture — cooking, brew, furniture, art, music, cloth"),
    ("The Refinery", "a8764e", "what sand and wreck become — fuels, chems, drugs, ores, synthetics"),
    ("The Workshop", "bd6f4e", "making & mending — smithing, machining, electronics, vehicles, power"),
    ("Powder & Slug", "8a8a6a", "kills by MASS — guns, cannon, mortars, blades, the Watch"),
    ("Blasterworks", "c25a4a", "kills by HEAT — the blaster spine, plasma, beam, tibanna"),
    ("The Strange Schools", "9c6b8a", "kills by STRANGER physics — ion, sonic, vibro, relics, saber"),
    ("The Shell", "7089a0", "not dying — armors, shields, warcaskets, the maker doctrines"),
    ("Droidsmith", "6f9083", "the scavenger's honest skill — repair, reconstruction, maintenance"),
    ("The Waking Mind", "5f8a74", "minds you make and minds you bind — the AI ladder"),
    ("THE SHIP", "4a7d86", "the Utinni herself — gravtech, her systems, her guns, her memory"),
    ("The Reach", "8a6b9c", "the trap — flesh, genes, bionics, archotech, priced brutally"),
    # Locked (faction-gated) trees follow the twelve.
    ("The Junker Yards", "a8503f", "LOCKED · Junkers — everything warcasket; raid loot and quests only"),
    ("The Foundry Hive", "7d9c5a", "LOCKED · Foundry Hive — sonic, hivetech, battle droids; they trade"),
    ("The Ascendant Ladder", "8a6b9c", "LOCKED · Helix — genes, biosculpting, the flesh ladder"),
    ("The Unbolting", "6f9083", "LOCKED · Free Droid Enclaves — building droids at all"),
]

TIERS = ["T0", "T1", "T2", "T3", "T4"]
TIER_LABEL = {"T0": "T0 · ≤600", "T1": "T1 · 600–1600",
              "T2": "T2 · 1600–3000", "T3": "T3 · 3000–5000",
              "T4": "T4 · 5000+"}
# Bin gradient, light (primitive) -> dark (advanced); text stays dark.
TIER_FILL = {"T0": "f2ead9", "T1": "e8dcc0", "T2": "ddcda6",
             "T3": "cdb989", "T4": "bda36c"}

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
HEADER_H = Inches(0.72)
TIERBAR_H = Inches(0.26)
MARGIN = Inches(0.12)
BOX_H = Emu(int(Inches(0.30)))
VGAP = Emu(int(Inches(0.045)))
HGAP = Emu(int(Inches(0.06)))


def rgb(hexstr):
    return RGBColor.from_string(hexstr)


def tier_of(m):
    return m.get("tier4") or m.get("tier3") or m.get("tier2") or m.get("tier") or "T0"


def cost_of(m):
    for k in ("cost4", "cost2", "cost"):
        v = m.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return 0.0


def no_autofit(tf):
    # Keep the shape the size we set; PowerPoint's autofit would fight shuffling.
    el = tf._txBody
    bodyPr = el.find(qn("a:bodyPr"))
    for tag in ("a:normAutofit", "a:spAutoFit"):
        e = bodyPr.find(qn(tag))
        if e is not None:
            bodyPr.remove(e)
    bodyPr.append(el.makeelement(qn("a:noAutofit"), {}))


def add_box(slide, x, y, w, h, text, fill, line, font_pt, bold=False,
            font_color="2b2418", align=PP_ALIGN.CENTER, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    box = slide.shapes.add_shape(shape, x, y, w, h)
    box.fill.solid()
    box.fill.fore_color.rgb = rgb(fill)
    box.line.color.rgb = rgb(line)
    box.line.width = Pt(0.75)
    box.shadow.inherit = False
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Pt(2)
    tf.margin_top = tf.margin_bottom = Pt(1)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(font_pt)
    r.font.bold = bold
    r.font.color.rgb = rgb(font_color)
    no_autofit(tf)
    return box


def build():
    M = json.load(open(MODEL, encoding="utf-8"))
    surv = [m for m in M if m.get("tab4")]
    by_tab = {}
    for m in surv:
        by_tab.setdefault(m["tab4"], []).append(m)

    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    blank = prs.slide_layouts[6]

    listed = {t for t, _, _ in TREES}
    roster = list(TREES) + [(t, "888888", "(tab not in the roster — check the model)")
                            for t in sorted(by_tab) if t not in listed]

    total_placed = 0
    for tab, accent, desc in roster:
        rows = by_tab.get(tab, [])
        if not rows:
            continue
        slide = prs.slides.add_slide(blank)

        # Header strip.
        add_box(slide, 0, 0, SLIDE_W, HEADER_H, "", "2b2418", "2b2418",
                10, shape=MSO_SHAPE.RECTANGLE)
        title = slide.shapes.add_textbox(MARGIN, Emu(0), SLIDE_W - 2 * MARGIN, HEADER_H)
        tf = title.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        r = p.add_run(); r.text = tab + "  "
        r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = rgb(accent)
        r2 = p.add_run(); r2.text = "%s   (%d techs)" % (desc, len(rows))
        r2.font.size = Pt(11); r2.font.color.rgb = rgb("d8cfc0")
        no_autofit(tf)

        # Five tier columns.
        col_w = (SLIDE_W - 2 * MARGIN) // 5
        top = HEADER_H + Emu(int(Inches(0.06)))
        area_top = top + TIERBAR_H + VGAP
        area_h = SLIDE_H - area_top - MARGIN
        rows_per_col = int((area_h + VGAP) // (BOX_H + VGAP))

        for ti, tier in enumerate(TIERS):
            cx = MARGIN + col_w * ti
            add_box(slide, cx, top, col_w - HGAP, TIERBAR_H, TIER_LABEL[tier],
                    TIER_FILL[tier], accent, 9, bold=True)
            members = sorted((m for m in rows if tier_of(m) == tier),
                             key=lambda m: (cost_of(m), m["label"]))
            # 1 or 2 sub-columns inside the tier column, filled top-down.
            subs = 1 if len(members) <= rows_per_col else 2
            sub_w = (col_w - HGAP - (subs - 1) * HGAP) // subs
            for i, m in enumerate(members):
                sc, sr = divmod(i, rows_per_col)
                if sc >= subs:  # overflow: shrink pitch by thirds column
                    sc, sr = 2, i - 2 * rows_per_col
                    if sc * (sub_w + HGAP) + sub_w > col_w:
                        sub_w = (col_w - HGAP - 2 * HGAP) // 3
                x = cx + sc * (sub_w + HGAP)
                y = area_top + sr * (BOX_H + VGAP)
                fs = 8 if len(m["label"]) <= 34 else 7
                add_box(slide, x, y, sub_w, BOX_H, m["label"],
                        TIER_FILL[tier], accent, fs)
                total_placed += 1

    prs.save(OUT)
    print("wrote %s: %d slides, %d boxes placed / %d surviving rows"
          % (OUT, len(prs.slides.__iter__.__self__._sldIdLst), total_placed, len(surv)))
    if total_placed != len(surv):
        print("MISMATCH: %d rows did not land on any slide" % (len(surv) - total_placed))
        sys.exit(1)


if __name__ == "__main__":
    build()
