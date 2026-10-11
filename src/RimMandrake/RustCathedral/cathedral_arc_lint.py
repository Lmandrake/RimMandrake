"""cathedral_arc_lint.py -- the Cathedral arc's bans gate (CATHEDRAL_STAGE_COMMENTARY_POOLS_1).

Every player-facing string the concealment arc ships is linted against the rulings it lives under:
  - arc spec §3/§8 (design/Jawa/cathedral_concealment_arc_spec.md): before stage 3 (REVEALED) no string attributes
    agency to the place; the reveal itself discloses aliveness and scale only (card A2), never purpose.
  - sheet §6 bans (design/Jawa/worldbuilding/biomes/the_rust_cathedral.md): ban 1 no §GM truth, ban 2 no explanation
    of the droids' mercy, ban 3 no hunting Sentinels, ban 6 no deep-drill description -- at EVERY stage, forever.
  - legends rulings (design/Jawa/worldbuilding/mindstone_arc_legends.md): the Kindled have never been made (no lore,
    no rumor), and no text names the Cathedral as living.
  - droid commentary never names the place at all (it is felt, not named); a stage -1 (any-stage) string speaks at
    every stage, so it is held to the pre-reveal rules.

Usage (exit 1 on any finding):
  python3 cathedral_arc_lint.py                         the shipped commentary pools: coverage + every line
  python3 cathedral_arc_lint.py --xml <file> --stage N  every player-facing text node in a def/patch file
  python3 cathedral_arc_lint.py --text "<line>" --stage N
  python3 cathedral_arc_lint.py --settings               every string a Mod Settings screen of this mod shows
Settings strings are out of fiction, so they may name the place and its mechanics; they are held to one rule
(decision taken by question card 2026-10-11, "Neutral wording"): no settings label or tooltip that names the place
also names learning or knowing (the old "as the Cathedral comes to know you" gave the arc away on the options screen).
Colonists learning ("Colonists learn to read the hum") is not the place learning and passes.
Items 4/5/7/8 of the arc run the --xml form over their own content in their verify.
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ATTITUDE_XML = os.path.join("Defs", "RM_BiomeAttitudeDefs", "RM_RustCathedralAttitude.xml")
ATTITUDE_TAG = "RimMandrake.RustCathedral.Hum.RM_BiomeAttitudeDef"
ATTITUDE_DEF = "RM_RustCathedralAttitude"

REVEALED = 3          # arc spec §1: 0 WARY, 1 TOLERATED, 2 VOUCHED, 3 REVEALED
STAGES = (0, 1, 2, 3)
POOL_MIN = 3          # lines per band x stage pool (the item names no count; 3 keeps a 12h-cooldown voice from repeating)

# (rule, regex) -- every stage, forever
ALWAYS = (
    ("kindled", r"\bkindled\b"),                                   # legends correction 1: never made, no rumor
    ("names-the-place", r"\bcathedral\b"),                         # commentary never names it; legends gate
    ("mercy (ban 2)", r"\bmerc(y|iful|ies)\b|\bspar(e|ed|es|ing)\b|\bprotect(s|ed|ing|ion)?\b|\bpass(es|ed)? (us )?over\b|\blets? us (live|pass|be)\b"),
    ("drill (ban 6)", r"\bdrill(s|ed|ing)?\b|\bdeep[- ]drill\b|\bdig(ging)? deep(er)?\b"),
    ("hunting Sentinels (ban 3)", r"\bhunt(s|ed|ing|er|ers)?\b|\bmanhunt\b"),
    ("§GM truth (ban 1)", r"\bkyber\b|\bcrystals?\b|\bmindstone\b|\bfactor(y|ies)\b|\bplasma\b|\bmicromachines?\b"
                          r"|\bsmart metal\b|\bdynamo\b|\bassailants?\b|\bterramanufacture\b"),
    ("mechanic named (ban 1)", r"\bgoodwill\b|\birritation\b|\bband\b|\bstanding\b|\bregard\b|\bstage\b|\bcomposite\b"),
)
# (rule, regex) -- before stage 3 only: agency attributed to the place
PRE_REVEAL = (
    ("agency before the reveal", r"\balive\b|\bliving\b|\ba mind\b|\baware\b|\bconscious\b|\bsomeone\b|\bsomebody\b"
                                 r"|\bit (wants|knows|chose|decided|hides|likes|dislikes|trusts|watches|forgives|judges|"
                                 r"is (watching|hiding|angry|pleased|listening|waiting))\b"
                                 r"|\bit's (watching|hiding|angry|pleased|listening|waiting)\b|\bwatching us\b"
                                 r"|\blistening to us\b|\bforgiv(e|es|en|ing)\b|\baudition\b|\bquest-?giver\b"),
)

# settings screens (out of fiction): learning / knowing words, in a string that names the place
SETTINGS_PLACE = r"\bcathedral\b|\bthe place\b"
SETTINGS = (
    ("learning named (settings)", r"\bcomes? to know\b|\bgets? to know\b|\bknows?\b|\bknew\b|\blearn(s|ed|ing|t)?\b"
                                  r"|\bremember(s|ed|ing)?\b|\brecogni[sz](e|es|ed|ing)\b|\bfamiliar\b"),
)
SETTINGS_CALLS = re.compile(r"\b(CheckboxLabeled|Label|Group|ButtonText|TextEntryLabeled|SettingControl)\s*\(")
SOURCE_DIR = "Source"

# player-facing text-bearing tags; a <li> counts when its parent is one of LIST_PARENTS
TEXT_TAGS = {"label", "description", "text", "letterLabel", "letterText", "reportString", "baseInspectLine",
             "jobString", "customLabel", "messageText", "successMessage", "failMessage", "rejectInputMessage"}
LIST_PARENTS = {"lines", "rulesStrings", "rulesRaw"}


def findings(text, stage):
    """[(rule, matched term)] for one player-facing string at a conduct-stage (-1 = any stage = pre-reveal rules)."""
    low = (text or "").lower()
    rules = ALWAYS + (PRE_REVEAL if stage < REVEALED else ())
    out = []
    for rule, rx in rules:
        m = re.search(rx, low)
        if m:
            out.append((rule, m.group(0)))
    return out


def _attitude_def(mod_root):
    path = os.path.join(mod_root, ATTITUDE_XML)
    for el in ET.parse(path).getroot():
        if el.tag == ATTITUDE_TAG and (el.findtext("defName") or "").strip() == ATTITUDE_DEF:
            return el
    return None


def pool_problems(mod_root=None):
    """Every required band x stage pool exists with >= POOL_MIN lines, no key or line repeats, every band in range,
    and every line lints clean at its own stage."""
    mod_root = mod_root or HERE
    d = _attitude_def(mod_root)
    if d is None:
        return ["pools: %s not parsed from %s" % (ATTITUDE_DEF, ATTITUDE_XML)]
    bad = []
    bands = len(d.findall("bandThresholds/li")) + 1
    if bands < 2:
        return ["pools: %d bands parsed (sanity probe failed)" % bands]
    pools, seen_lines = {}, {}
    for e in d.findall("commentary/li"):
        band = int((e.findtext("band") or "-99").strip())
        stage = int((e.findtext("stage") or "-1").strip())
        lines = [(li.text or "").strip() for li in e.findall("lines/li")]
        if not 0 <= band < bands:
            bad.append("pools: band %d out of range 0-%d" % (band, bands - 1))
        if (band, stage) in pools:
            bad.append("pools: duplicate pool key band %d stage %d" % (band, stage))
        pools[(band, stage)] = lines
        for ln in lines:
            if not ln:
                bad.append("pools: empty line in band %d stage %d" % (band, stage))
                continue
            if ln in seen_lines:
                bad.append("pools: line repeated (band %d stage %d and %s): %r" % (band, stage, seen_lines[ln], ln[:50]))
            seen_lines[ln] = "band %d stage %d" % (band, stage)
            for rule, term in findings(ln, stage):
                bad.append("pools: %s -- %r in band %d stage %d: %r" % (rule, term, band, stage, ln[:60]))
    for stage in STAGES:
        for band in range(bands):
            n = len([x for x in pools.get((band, stage), []) if x])
            if n < POOL_MIN:
                bad.append("pools: band %d stage %d has %d lines, needs %d" % (band, stage, n, POOL_MIN))
    return bad


def xml_findings(path, stage):
    """Lint every player-facing text node in a def/patch XML file at one stage."""
    out = []
    root = ET.parse(path).getroot()
    parents = {c: p for p in root.iter() for c in p}
    for el in root.iter():
        if not isinstance(el.tag, str) or not (el.text or "").strip():
            continue
        if el.tag in TEXT_TAGS or (el.tag == "li" and parents.get(el) is not None and parents[el].tag in LIST_PARENTS):
            text = el.text.split("->", 1)[-1]
            for rule, term in findings(text, stage):
                out.append("%s: %s -- %r in <%s>: %r" % (os.path.basename(path), rule, term, el.tag, text.strip()[:60]))
    return out


def _call_strings(src):
    """Every C# string literal inside the argument list of a settings-drawing call (labels, tooltips, group titles)."""
    out = []
    for m in SETTINGS_CALLS.finditer(src):
        i, depth, cur = m.end(), 1, None
        while i < len(src) and depth:
            ch = src[i]
            if cur is not None:
                if ch == "\\":
                    cur += src[i:i + 2]
                    i += 2
                    continue
                if ch == '"':
                    out.append(cur)
                    cur = None
                else:
                    cur += ch
            elif ch == '"':
                cur = ""
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
    return out


def settings_findings(mod_root=None, extra=None):
    """Lint every settings string of the mod's C# (files that draw a settings screen). extra = {name: C# source}."""
    mod_root = mod_root or HERE
    srcs = {}
    for d, _, fs in os.walk(os.path.join(mod_root, SOURCE_DIR)):
        for f in fs:
            if f.endswith(".cs"):
                t = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
                if "CheckboxLabeled" in t or "DoSettingsWindowContents" in t:
                    srcs[f] = t
    srcs.update(extra or {})
    out, n = [], 0
    for name, t in sorted(srcs.items()):
        for s in _call_strings(t):
            n += 1
            low = s.lower()
            if not re.search(SETTINGS_PLACE, low):
                continue
            for rule, rx in SETTINGS:
                mm = re.search(rx, low)
                if mm:
                    out.append("%s: %s -- %r in %r" % (name, rule, mm.group(0), s[:70]))
    if n < 10:
        out.append("settings: only %d strings read (sanity probe failed)" % n)
    return out


def selftest():
    bad = settings_findings()
    assert not bad, bad
    planted = settings_findings(extra={"Planted.cs": 'list.CheckboxLabeled("Droids\' remarks change as the Cathedral comes to know you",'
                                                     ' ref x,\n  "Off: " + "the Cathedral learns your ways.");'
                                                     '\nlist.Label("Colonists learn to read the hum");'})
    assert len(planted) == 2 and all("Planted.cs" in p for p in planted), planted
    assert _call_strings('list.Label("a (b)" + f("c")); x("d")') == ["a (b)", "c"]
    return "selftest ok (shipped settings clean; planted label + tooltip caught; colonists learning passes)"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--xml", action="append", default=[])
    ap.add_argument("--text")
    ap.add_argument("--stage", type=int, default=-1)
    ap.add_argument("--settings", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        print(selftest())
        return 0
    if a.settings:
        bad = settings_findings()
    elif a.text is not None:
        bad = ["%s -- %r" % f for f in findings(a.text, a.stage)]
    elif a.xml:
        bad = [b for p in a.xml for b in xml_findings(p, a.stage)]
    else:
        bad = pool_problems()
    print("cathedral_arc_lint: %s" % ("PASS (0 findings)" if not bad else "FAIL (%d)" % len(bad)))
    for b in bad:
        print("  - " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
