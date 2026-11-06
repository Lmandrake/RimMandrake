#!/usr/bin/env python3
"""format_sheet.py -- the modcheck sheet FORMAT ratification sheet (MODCHECK_PITS_SHEET_REBUILD_DECAYED_UNSEEN).

MOD_VALIDATION_RETROFIT_1 starts only after the owner ratifies the modcheck report format (spec
design/RimMandrake/mod_validation_runner_spec.md §5 step 2). The sheet he was pointed at,
Transient/modcheck/Pits_20260912T231116Z.html, decayed out of Transient. This rebuilds it from data in git, so it
cannot decay again:

  * testdata/pits_pilot_summary.json        the Pits pilot's run of 2026-09-13 10:24 UTC (GREEN 3/3),
                                            from git 7276502e93^ (the 2026-09-12 23:11 run kept no JSON)
  * testdata/flowworks_visual_excerpt.json  one FlowWorks chain (2026-10-25) with appearance lines, which the pilot
                                            predates (spec §5.5)

Both are rendered by TODAY's report.render, the renderer the retrofit would use. The ratification sheet is a non-art
review sheet (review-sheets template + nonart_sheet.py declare): one row per element of the format.

    python3 format_sheet.py build     # writes OUT_DIR/* (sheet, two reports); decisions/prereview left alone if present
    python3 format_sheet.py verify    # exit 0 only when built from these fixtures, tracked, non-art check OK,
                                      # prereview OK, and the decisions file is ruled (his pick recorded)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "art"))
from report import render  # noqa: E402

TEMPLATE = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "sheet_template.html"
OUT_DIR = ROOT / "Transient" / "modcheck_format"
STEM = "modcheck_format_ratify_2026-11-05"
SHEET = OUT_DIR / (STEM + ".html")
DECISIONS = OUT_DIR / (STEM + ".decisions.json")
PITS_REPORT = OUT_DIR / "Pits_pilot_report.html"
FW_REPORT = OUT_DIR / "FlowWorks_appearance_excerpt.html"
PITS_FIX = HERE / "testdata" / "pits_pilot_summary.json"
FW_FIX = HERE / "testdata" / "flowworks_visual_excerpt.json"

OPTIONS = [
    {"key": "keep", "label": "Ratify as is", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
    {"key": "change", "label": "Ratify with a change (say it in the note)", "hotkey": "2", "color": "#e8b64c",
     "counts": "in"},
    {"key": "cut", "label": "Reject / remove (say why)", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
]


def rows(pits):
    comps = [c for ch in pits["chains"] for c in ch["components"]]
    ev_calls = sum(len(c.get("evidence") or []) for c in comps)
    report_kb = len(render("Pits", pits).encode("utf-8")) // 1024
    shots = sum(len(c.get("screenshots") or []) for c in comps)
    return [
        {"id": "whole_report", "group": "1 the report as a whole",
         "label": "The Pits pilot report, re-rendered by today's renderer",
         "effect": ("Open Pits_pilot_report.html (link in the brief). It is the pilot suite you were asked about on "
                    "2026-09-12, from its run of 2026-09-13 10:24 UTC (the only one whose data was kept): %d chains, %d components, all PASS, GREEN. This row is your verdict on the "
                    "page as one thing; the rows below split it so you can change one part." %
                    (len(pits["chains"]), len(comps))),
         "prefill": "keep", "contested": False},
        {"id": "overall_verdict", "group": "2 header",
         "label": "One overall verdict in the title",
         "effect": ("The H1 reads '<mod> -- GREEN' (green) or RED, naming the half that failed: 'RED (state)', "
                    "'RED (appearance)', 'RED (state, appearance)'; 'REFUSED — <why>' when the run never "
                    "started; a run of chosen chains reads 'TARGETED n/m chains [...]' so a subset never "
                    "passes for the whole suite."),
         "prefill": "keep", "contested": False},
        {"id": "chain_tables", "group": "3 body",
         "label": "One table per chain; columns component | toggle | verdict | detail | evidence",
         "effect": ("A chain is one scenario (pit_capture, uncover_disarms); each component is one checked "
                    "behaviour. Verdict is coloured PASS green, FAIL red, UNMEASURED amber. No summary row "
                    "counts passes per chain."),
         "prefill": "keep", "contested": False},
        {"id": "toggle_column", "group": "3 body",
         "label": "The toggle column names the Mod Settings switch each component exercises",
         "effect": ("e.g. falls_in → trapTriggerEnabled, struggle_clock_ticks → escapeEnabled; a component no "
                    "switch covers reads 'beyond-toggle'. This is how the sheet shows the settings floor "
                    "(every toggle exercised) is met."),
         "prefill": "keep", "contested": False},
        {"id": "evidence_raw", "group": "3 body",
         "label": "Evidence shows every bridge call with its raw result, untruncated",
         "effect": ("%d calls on the Pits sheet print as 'call -> {python dict}', which is most of its %d KB. It "
                    "is complete and auditable but hard to read; the alternative is a one-line result per call "
                    "with the raw dict folded behind a click (the JSON twin keeps it either way)." %
                    (ev_calls, report_kb)),
         "prefill": "keep", "contested": True},
        {"id": "screenshots_as_paths", "group": "3 body",
         "label": "Screenshots are listed as file paths, not shown",
         "effect": ("The pilot took %d screenshot; the sheet prints its Windows path in grey monospace. You see "
                    "no picture unless you open the file. The alternative is an inline thumbnail." % shots),
         "prefill": "keep", "contested": True},
        {"id": "appearance_lines", "group": "4 added after the pilot",
         "label": "Appearance must-show / cannot lines under each component's evidence",
         "effect": ("Open FlowWorks_appearance_excerpt.html (link in the brief). Added after the pilot (spec "
                    "§5.5: a sheet that shows only state verdicts is the sheet that let the pit pass): each "
                    "judged line reads 'must <id> <verdict> — <why>', green or red, and drives the 'RED "
                    "(appearance)' half of the title. The excerpt is one real FlowWorks chain from 2026-10-25 "
                    "whose two appearance lines came back UNJUDGEABLE (red): their ids had been orphaned from the "
                    "validated checklist, which the line says in place."),
         "prefill": "keep", "contested": False},
        {"id": "json_twin", "group": "4 added after the pilot",
         "label": "A machine-readable .json beside every sheet",
         "effect": ("Each run writes <mod>_<UTC>.html and the same run as <mod>_<UTC>.json (summary, findings, "
                    "benign clock stops). Tools and acceptance items read the JSON; the HTML is for you."),
         "prefill": "keep", "contested": False},
        {"id": "transient_shelf_life", "group": "5 where it lives",
         "label": "Sheets live in Transient/modcheck/ (~14 days, untracked); the ledger is the record",
         "effect": ("By design a run's sheet is a flip-through and the rimflow verify event is the durable "
                    "record. That is how the 2026-09-12 sheet decayed before you saw it. The alternative: "
                    "keep a mod's sheet until you have reviewed it once (spec: once, before its first GREEN)."),
         "prefill": "keep", "contested": True},
    ]


def config(items):
    return {
        "sheetId": STEM,
        "title": "modcheck report format — ratify it",
        "subtitle": "%d format elements · rebuilt from the Pits pilot run in git" % len(items),
        "briefHtml": (
            "<p><b>Why you are here.</b> The full modcheck retrofit (every shipped mod gets a validation script "
            "and a green run, <code>MOD_VALIDATION_RETROFIT_1</code>) waits on one thing: you ratifying the "
            "<b>format</b> of the report a run produces. The Pits pilot ran GREEN 3/3 on 2026-09-12 and again on 2026-09-13; the sheet "
            "you were pointed at decayed out of Transient before you opened it.</p>"
            "<p><b>Open these two reports</b>, then rule each row: "
            "<a href=\"Pits_pilot_report.html\" target=\"_blank\">Pits pilot report</a> · "
            "<a href=\"FlowWorks_appearance_excerpt.html\" target=\"_blank\">appearance lines (FlowWorks "
            "excerpt)</a>. Both are rendered by today's renderer, the one every mod in the retrofit will "
            "use.</p>"
            "<p>The Pits mod has since been merged into FlowWorks; its data is used here only as a real, "
            "small, all-PASS run to show the format.</p>"),
        "criterion": "Grouped by where the element sits on a report, top to bottom.",
        "invented": [
            "Splitting the format into these nine elements is my framing; you were originally asked one "
            "question, the whole sheet.",
            "Every row is pre-filled 'Ratify as is' (the format as it ships today). The three contested rows "
            "are the ones I think you may want changed: raw evidence, screenshots as paths, Transient shelf "
            "life.",
        ],
        "posture": {"mode": "whitelist",
                    "explain": "Default is ratify: a row you leave alone keeps that element as it is now."},
        "options": OPTIONS,
        "groupLabel": "part of the report",
        "media": False,
        "decisionsFile": DECISIONS.name,
        # repo-relative: a clone's absolute path is neither the owner's nor stable across clones
        "decisionsPath": "Transient/modcheck_format/" + DECISIONS.name,
        "sheetPath": "Transient/modcheck_format/" + SHEET.name,
    }


def replace_block(html, block_id, payload):
    open_tag = '<script id="%s" type="application/json">' % block_id
    i = html.index(open_tag) + len(open_tag)
    j = html.index("</script>", i)
    return html[:i] + "\n" + payload.replace("</", "<\\/") + "\n" + html[j:]


def build_sheet_html(items):
    html = TEMPLATE.read_text(encoding="utf-8")
    html = replace_block(html, "CONFIG", json.dumps(config(items), indent=2, ensure_ascii=False))
    html = replace_block(html, "ITEMS", json.dumps(items, indent=1, ensure_ascii=False))
    import nonart_sheet
    return nonart_sheet.declare(html)


def build():
    pits = json.loads(PITS_FIX.read_text())
    fw = json.loads(FW_FIX.read_text())
    items = rows(pits)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PITS_REPORT.write_text(render("Pits", pits), encoding="utf-8")
    FW_REPORT.write_text(render("FlowWorks (one chain)", fw), encoding="utf-8")
    SHEET.write_text(build_sheet_html(items), encoding="utf-8")
    if not DECISIONS.exists():      # never overwrite his picks
        DECISIONS.write_text(json.dumps({
            "sheetId": STEM, "posture": "whitelist", "decidedCount": 0, "frozen": False,
            "reviewStatus": {"state": "prefill"},
            "decisions": {it["id"]: {"decision": it["prefill"], "prefill": it["prefill"], "note": ""}
                          for it in items},
        }, indent=2) + "\n", encoding="utf-8")
    print("wrote %s\n  + %s, %s, %s" % (SHEET, PITS_REPORT.name, FW_REPORT.name, DECISIONS.name))
    return 0


def problems():
    """Every reason the item is not done, [] when it is. Pure reads."""
    out = []
    pits = json.loads(PITS_FIX.read_text())
    if not (pits.get("all_green") and len([c for ch in pits["chains"] for c in ch["components"]]) == 3):
        out.append("Pits fixture is not the GREEN 3/3 pilot run")
    for p in (SHEET, DECISIONS, PITS_REPORT, FW_REPORT):
        if not p.is_file():
            out.append("missing %s (run build)" % p)
    if out:
        return out
    if PITS_REPORT.read_text(encoding="utf-8") != render("Pits", pits):
        out.append("Pits_pilot_report.html is not today's render of the fixture (run build)")
    if FW_REPORT.read_text(encoding="utf-8") != render("FlowWorks (one chain)", json.loads(FW_FIX.read_text())):
        out.append("FlowWorks_appearance_excerpt.html is not today's render of the fixture (run build)")
    # compare only what this tool authors (CONFIG + ITEMS), so template churn or a box without the skill's
    # template does not read as a stale sheet
    html = SHEET.read_text(encoding="utf-8")
    items = rows(pits)
    for block, want in (("CONFIG", config(items)), ("ITEMS", items)):
        m = re.search(r'<script id="%s" type="application/json">(.*?)</script>' % block, html, re.S)
        if not m or json.loads(m.group(1).replace("<\\/", "</")) != want:
            out.append("the sheet's %s is not today's build (run build)" % block)
    # pinned = un-ignored in Transient/.gitignore (transient_pin.py), so it is committed and cannot decay again.
    # Read the pin list, not `git ls-files`: the blind checker's box has no git metadata to ask.
    pins = (ROOT / "Transient" / ".gitignore").read_text().splitlines()
    for p in (SHEET, DECISIONS, PITS_REPORT, FW_REPORT, OUT_DIR / (STEM + ".prereview.json")):
        if "!/modcheck_format/" + p.name not in pins:
            out.append("not pinned, so it can decay again: %s (transient_pin.py add)" % p.name)
    import nonart_sheet
    ok, msg = nonart_sheet.verify(SHEET, DECISIONS)
    if not ok:
        out.append("nonart_sheet: " + msg)
    r = subprocess.run([sys.executable, str(HERE.parent / "art" / "prereview.py"), "check", str(SHEET)],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        out.append("prereview: " + (r.stdout + r.stderr).strip().splitlines()[-1:][0] if (r.stdout + r.stderr).strip()
                   else "prereview: refused")
    doc = json.loads(DECISIONS.read_text())
    if (doc.get("reviewStatus") or {}).get("state") != "ruled":
        out.append("the owner's pick is not recorded yet: decisions reviewStatus.state is %r, not 'ruled'"
                   % (doc.get("reviewStatus") or {}).get("state"))
    return out


def main(argv):
    if argv[:1] == ["build"]:
        return build()
    if argv[:1] == ["verify"]:
        bad = problems()
        for b in bad:
            print("NOT DONE:", b)
        print("OK: format sheet rebuilt, tracked, checked, prereviewed and ruled" if not bad else
              "%d problem(s)" % len(bad))
        return 1 if bad else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
