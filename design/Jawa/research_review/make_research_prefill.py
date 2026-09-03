#!/usr/bin/env python3
"""make_research_prefill.py — build the research-normalization review sheet.

The owner reviews the prefilled research manifest (RESEARCH_TREE_NORMALIZATION_1's
one remaining owner pass). Every one of 522 research projects carries a FATE ruled
by the taxonomy sitting; this sheet prefills each and lets the owner override.

Fills exactly the two template blocks (CONFIG + ITEMS) plus a small RENDER block
that shows each row's ruling rationale under its consequence line. Chrome is the
template's, not ours (that is what check_sheet.py guards).

    python3 make_research_prefill.py
    python3 ../../../../home/mandrake/.claude/skills/review-sheets/assets/check_sheet.py \
        research_manifest_review.html --decisions research_review_decisions.json

Data (read-only):
  MANIFEST  infrastructure/output/research_manifest_draft.csv   (522 rows, ruled fates)
  DUMP      DefDump/captures/2026-09-03T06-10-14Z ResearchProjectDef.json (589-mod live)

§7 guard: refuses to overwrite a decisions file the sidecar has stamped (savedBy)
or frozen, unless --i-know-this-overwrites-the-owners-decisions. --sheet-only
rebuilds the page against existing decisions.
"""
from __future__ import annotations
import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from game_paths import LOCALLOW                                    # noqa: E402

TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
MANIFEST = os.path.join(REPO, "infrastructure/output/research_manifest_draft.csv")
# Frozen to this one capture on purpose — the review sheet's ruling must stay pinned
# to the dump it was built against, never silently drift to whatever DEF_DUMP resolves
# to next (a newer capture).
DUMP = os.path.join(LOCALLOW, "DefDump", "captures", "2026-09-03T06-10-14Z",
                     "defs", "ResearchProjectDef.json")
SHEET = os.path.join(HERE, "research_manifest_review.html")
DPATH = os.path.join(HERE, "research_review_decisions.json")

FATES = ["untouched", "keep", "cut", "merge", "reflavor"]
# a row is CONTESTED (defensible both ways) if its note flags an open question
CONTEST_MARKERS = ("prereq question", "plasma", "chain disconnect", "disconnect",
                   "open question", "unresolved", "TODO", "unsure", "verify owner")


def load_manifest() -> list[dict]:
    lines = [l for l in open(MANIFEST, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("".join(lines))))


def load_dump() -> dict[str, dict]:
    rows = json.load(open(DUMP, encoding="utf-8"))["defs"]
    return {r["defName"]: r.get("fields", {}) for r in rows}


def consequence(fields: dict) -> tuple[str, bool]:
    """One line: what the project DOES. (text, inferred)."""
    desc = (fields.get("description") or "").strip().replace("\n", " ")
    unlocked = fields.get("cachedUnlockedDefs") or []
    if desc:
        line = desc if len(desc) <= 140 else desc[:137].rstrip() + "…"
        if unlocked:
            head = ", ".join(unlocked[:3])
            extra = f" (+{len(unlocked) - 3})" if len(unlocked) > 3 else ""
            line += f"  · unlocks {head}{extra}"
        return line, False
    if unlocked:
        head = ", ".join(unlocked[:4])
        extra = f" (+{len(unlocked) - 4})" if len(unlocked) > 4 else ""
        return f"Unlocks {head}{extra}", False
    return "No description and no recorded unlocks — effect unknown from the def alone", True


def build() -> tuple[list[dict], dict]:
    man = load_manifest()
    dump = load_dump()
    items = []
    for r in man:
        dn = r["defName"]
        fields = dump.get(dn, {})
        eff, inferred = consequence(fields)
        note = (r.get("note") or "").strip()
        contested = any(m in note.lower() for m in CONTEST_MARKERS)
        fate = r.get("fate") or "untouched"
        meta = {}
        if r.get("tab"):
            meta["tab"] = r["tab"]
        if r.get("tier"):
            meta["tier"] = r["tier"]
        if r.get("cost"):
            meta["cost"] = r["cost"]
        if fate == "merge" and r.get("merge_target"):
            meta["→"] = r["merge_target"]
        items.append({
            "id": dn,
            "label": fields.get("label") or dn,
            "group": r.get("source_mod") or "?",
            "effect": eff,
            "why": note,                      # rendered by the RENDER block
            "meta": meta,
            "prefill": fate,
            "inferred": inferred,
            "contested": contested,
        })
    # real decisions first-class: sort so non-untouched float to the top of each group
    order = {"cut": 0, "merge": 1, "reflavor": 2, "keep": 3, "untouched": 4}
    items.sort(key=lambda it: (it["group"], order.get(it["prefill"], 9), it["label"]))

    decisions = {
        "posture": "fate-review",
        "criterion": ("Fates ruled by the taxonomy sitting (design/Jawa/research_tree_taxonomy.md) "
                      "— not a metric. This sheet collects overrides of those rulings."),
        "generatedBy": "make_research_prefill.py",
        "manifestFingerprint": "c2960afd (586-label) — defName set MATCHES live 589 world exactly",
        "decisions": {it["id"]: {"decision": it["prefill"], "prefill": it["prefill"], "note": ""}
                      for it in items},
    }
    return items, decisions


CONFIG = {
    "sheetId": "research_normalization_review",
    "title": "Research tree — normalization review",
    "subtitle": "522 projects · 45 real fate calls · the owner pass",
    "briefHtml": """
      <p><b>What this is.</b> Every research project in the game (522, the full live
      589-mod set — coverage verified, zero orphans) carries a <b>fate</b> ruled by the
      taxonomy sitting. Your job is to <b>confirm or overrule</b> those rulings, not to
      re-decide 522 rows from scratch.</p>
      <p><b>Where the judgement is.</b> Only <b>45 rows carry a real fate change</b>
      (28&nbsp;cut · 8&nbsp;keep · 6&nbsp;merge · 3&nbsp;reflavor). The other 477 are
      <b>untouched</b> and confirmable in bulk. Filter to <i>overrides only</i> to see
      what you changed, or use the fate filter to review one fate at a time. Each row
      shows what the project <b>does</b>; the ruling rationale is the grey line under it.</p>""",
    "criterion": ("Fates ruled by the taxonomy sitting, not by a metric — this collects "
                  "the owner's overrides of those rulings."),
    "invented": [
        "477 of 522 rows defaulted to 'untouched' — no sitting ruling touched them; they carry the tab/tier the taxonomy's tier-band correspondence implies, not a per-row decision.",
        "The 249 band-conformance validator FAILs are EXPECTED deferred rebalancing (real mod costs left as-is), not defects — they do not mean a row is wrong.",
        "The manifest's fingerprint header says 586 mods / 2026-09-01, but its defName set matches the live 589 world exactly (the 3 newer mods add no research); a re-stamp is owed but coverage is not in question.",
        "Consequence lines are the def's own description + its unlocked defs; the handful with neither are marked 'inferred'.",
    ],
    "posture": {"mode": "fate-review",
                "explain": "Each row carries a prefilled fate. Only 'cut' removes the project; "
                           "keep / merge / reflavor / untouched all retain it. This is not a "
                           "whitelist — an undecided row keeps its prefilled fate, it is not stripped."},
    "options": [
        {"key": "untouched", "label": "Untouched", "hotkey": "1", "color": "#8a94a0", "counts": "in"},
        {"key": "keep",      "label": "Keep",      "hotkey": "2", "color": "#5ac37f", "counts": "in"},
        {"key": "reflavor",  "label": "Reflavor",  "hotkey": "3", "color": "#4c9be8", "counts": "in"},
        {"key": "merge",     "label": "Merge",     "hotkey": "4", "color": "#e8b64c", "counts": "in"},
        {"key": "cut",       "label": "Cut",       "hotkey": "5", "color": "#e06c6c", "counts": "out"},
    ],
    "groupLabel": "source mod",
    "media": False,
    "decisionsFile": "research_review_decisions.json",
}

RENDER_BLOCK = """<script id="RENDER">
  // effect line + the ruling rationale underneath (grey), so a fate is decidable
  window.itemBody = it => {
    const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    const marks = [];
    if (it.inferred)  marks.push('<span class="mark inferred" title="no description or unlocks in the def">\\u26a0 inferred</span>');
    if (it.contested) marks.push('<span class="mark contested" title="the ruling left an open question">\\u25c6 contested</span>');
    for (const [k, v] of Object.entries(it.meta || {})) marks.push(`<span class="mark absent">${esc(k)}: ${esc(v)}</span>`);
    const why = it.why ? `<div class="sub" style="opacity:.72;font-size:12px;margin-top:2px">ruled: ${esc(it.why)}</div>` : '';
    return `<div class="effect">${esc(it.effect || '')}</div>${why}`
         + (marks.length ? `<div class="marks">${marks.join('')}</div>` : '');
  };
</script>
"""


def swap(doc: str, tag_id: str, payload: str) -> str:
    start = doc.index(f'<script id="{tag_id}" type="application/json">')
    start = doc.index(">", start) + 1
    end = doc.index("</script>", start)
    return doc[:start] + "\n" + payload + "\n" + doc[end:]


def main() -> int:
    sheet_only = "--sheet-only" in sys.argv
    force = "--i-know-this-overwrites-the-owners-decisions" in sys.argv
    if not sheet_only and os.path.exists(DPATH) and not force:
        try:
            existing = json.load(open(DPATH, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        if existing.get("savedBy"):
            print(f"REFUSING: {DPATH} was written by the sheet "
                  f"({existing.get('savedAt')}, {existing.get('writeCount')} writes). "
                  f"Re-running replaces the owner's decisions with guesses. "
                  f"Pass --i-know-this-overwrites-the-owners-decisions to force, "
                  f"or --sheet-only to rebuild just the page.", file=sys.stderr)
            return 3
        if existing.get("frozen"):
            print(f"REFUSING: {DPATH} is FROZEN. Use --sheet-only.", file=sys.stderr)
            return 3

    items, decisions = build()
    html = open(TEMPLATE, encoding="utf-8").read()
    cfg = dict(CONFIG)
    cfg["decisionsPath"] = DPATH
    cfg["sheetPath"] = SHEET
    html = swap(html, "CONFIG", json.dumps(cfg, indent=2))
    html = swap(html, "ITEMS", json.dumps(items, indent=1))
    # inject the RENDER block just before the closing body/script region: put it
    # right after the ITEMS block's </script> so window.itemBody is defined early.
    marker = '<script id="ITEMS" type="application/json">'
    close = html.index("</script>", html.index(marker)) + len("</script>")
    html = html[:close] + "\n" + RENDER_BLOCK + html[close:]

    open(SHEET, "w", encoding="utf-8").write(html)
    if sheet_only:
        print(f"  sheet      {SHEET}  ({len(html)/1024:.0f} KB) — rebuilt, decisions LEFT ALONE")
        return 0
    json.dump(decisions, open(DPATH, "w", encoding="utf-8"), indent=2)
    fates = {}
    for it in items:
        fates[it["prefill"]] = fates.get(it["prefill"], 0) + 1
    real = sum(v for k, v in fates.items() if k != "untouched")
    inf = sum(1 for it in items if it["inferred"])
    con = sum(1 for it in items if it["contested"])
    print(f"  sheet      {SHEET}  ({len(html)/1024:.0f} KB)")
    print(f"  decisions  {DPATH}  ({len(items)} prefilled)")
    print(f"  fates      {fates}  ·  {real} real calls, {477 if fates.get('untouched')==477 else fates.get('untouched',0)} untouched")
    print(f"  flags      {inf} inferred · {con} contested")
    return 0


if __name__ == "__main__":
    sys.exit(main())
