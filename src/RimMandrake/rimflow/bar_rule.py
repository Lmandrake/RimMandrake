#!/usr/bin/env python3
"""bar_rule.py - a passing bar is an experience a player would notice; it never pins a tuning number or an asset count.

Owner, 2026-11-16 (OWNER.jsonl, note on RIMMANDRAKE_APPLY_CONTAGION_JUDGE_FIXES_EIGHT_REFUSALS_HALTED), after reading the
Contagion coverage judge's 25 refusals: "The mod passing bars should not specify flora and fauna yield rates! That would
mean every time we renormalize every mod must repass its bars... drop that! How do we get the Judges to not demand
pendantic stuff like this? Who cares the halfmade tree has more than one graphic? There's variants all the time."
Ruling: design/RimMandrake/standing_rulings.md §A passing bar is an experience. Item
RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS.

The one-sentence test: would this bar have to be re-passed after we renormalize numbers or add an art variant? Then it is
not a bar.

RULE_TEXT is what a judge brief or a bar-writing brief says (coverage_judge.prompt and delta_prompt carry it).
`blocks(gap)` is the gate: a gap blocks only when it is about an experience. It does not block when its own `bar_kind`
says tuning_number, asset_variant or declared_data, when its demand (what, would_pass, smallest_fix) reads as one of those
to the detector below whatever the judge called it, or when it is `late` with `miss_of` (a new gap at a later look on
material that did not change, after a look that refused and so had to list every gap: that look's miss) and is not a
serious Problem confirmed by the second reader. Owner, by card 2026-11-16 11:36 PM PST (point 26, "Only if a second
reader agrees"): "a late gap blocks only when it is a Problem a player would reject and the judge's second reader
confirms it." So a late gap blocks only with the judge's `severity` `problem` AND the second reader's `late_confirmed`
True (coverage_judge.second_read sets it; the program reader confirms nothing); a late gap the reader has not read yet
is held blocking until it does. A late gap with no refusing look before it still blocks. A gap that does not block is
advisory: stored and shown.

The detector reads only the DEMAND, never `observed` (which quotes the artifact, numbers and all). It is a word list,
measured on the 25 Contagion gaps and the calibration cases (selftest_bar_rule_tuning_numbers.py); a new phrasing it
misses is a line here, with its case in that selftest.
"""
import re

BAR_KINDS = ("experience", "tuning_number", "asset_variant", "declared_data")
ADVISORY_KINDS = ("tuning_number", "asset_variant", "declared_data", "late")

RULE_TEXT = (
    "A passing bar states an experience a player would notice. It never pins a yield rate, a stat value or any other "
    "tuning number a renormalization pass changes, and never an asset-variant count. The test, one sentence: would this "
    "bar have to be re-passed after we renormalize numbers or add an art variant? Then it is not a bar, and a gap that "
    "asks for it is not a gap (owner 2026-11-16, after the Contagion judge's 25 refusals). Named NON-gaps from that "
    "look: 'the selftest covers every rostered plant's ingestible and yield fields'; 'the Halfmade Tree resolves more "
    "than one graphic variant'; 'one row per inventory special, each with its field and expected value'. A def's "
    "declared numbers and flags (yields, MeatAmount, leather, nutrition, market value, speed, size, a docile or pack "
    "flag, a burn or growth rate) are tuning data: a gap about one is advisory at most, never blocking, whatever an "
    "inventory row or impl_evidence lists. A part of a capability is something a player would notice in play (the "
    "thing happens, is seen, can be done, fails visibly), not each number or field its text names. Give every gap a "
    "`bar_kind`: `experience` (a player would notice it missing or wrong), `tuning_number`, `asset_variant` or "
    "`declared_data`; only `experience` gaps block, the rest are stored as advisory.")

_TUNING = [r"\byield (rates?|fields?|values?|amounts?|numbers?)\b", r"\byield and \w+ fields?\b",
           r"\b(ingestible|yield) (and \w+ )?fields?\b", r"\bingestible\b",
           r"\b(meat|leather)\s?amount\b", r"\bmarket ?value\b", r"\bnutrition (value|field)s?\b",
           r"\bstat (values?|bases?|numbers?)\b", r"\bstatbases\b",
           r"\b(yield|burn|spawn|growth|drop|regen\w*|decay|heal\w*|hunger|commonality|fire) ?rates?\b",
           r"\b(spawn|commonality|density) (weights?|values?)\b",
           r"\bexact (number|value|count|amount)s?\b",
           # a stat named with its number: "the beauty stats read -15 and -3", "Beauty -15" (Graffiti ugliness_visible as locked)
           r"\bstats? (reads?|of|at|=)\s*[-\u2212+]?\d",
           r"\b(beauty|cleanliness|comfort|mass|nutrition|armou?r|wealth)\s*[-\u2212+]\d"]
_VARIANT = [r"\b(graphic|texture|sprite|art) ?variants?\b", r"\bvariant (art|graphics?|textures?|sprites?|count)s?\b",
            r"\bmore than one (graphic|variant|texture|sprite)s?\b", r"\b\d+ (graphic|texture|sprite|art) variants?\b",
            r"\bgraphic ?count\b"]
_DECLARED = [r"\b(fields?|values?) and (its |their )?expected values?\b", r"\beach with its field\b",
             r"\bevery (field|stat|number)\b", r"\bdef'?s? (numbers|fields|values)\b",
             r"\bdeclared (numbers|values|fields|data)\b"]
DETECT = (("asset_variant", [re.compile(p, re.I) for p in _VARIANT]),
          ("declared_data", [re.compile(p, re.I) for p in _DECLARED]),
          ("tuning_number", [re.compile(p, re.I) for p in _TUNING]))


def demand(gap):
    """The text a gap ASKS for: what, would_pass and its smallest fix (never `observed`, which quotes the artifact)."""
    fix = gap.get("smallest_fix") if isinstance(gap.get("smallest_fix"), dict) else {}
    return " ".join(str(x or "") for x in (gap.get("what"), gap.get("would_pass"), fix.get("what")))


def detect(gap):
    """-> (kind, the matched words) when the gap's demand pins a tuning number, an asset count or a declared field;
    (None, None) otherwise."""
    text = demand(gap)
    for kind, pats in DETECT:
        for p in pats:
            m = p.search(text)
            if m:
                return kind, m.group(0)
    return None, None


def blocks(gap):
    """-> (True, None) for a gap about an experience; (False, why) for one that is advisory at most."""
    if gap.get("new_since") == "late" and gap.get("miss_of"):
        if gap.get("severity") != "problem":
            return False, ("late: a new gap at a later look on material that did not change is the miss of %s, and the "
                           "judge does not call it a serious Problem a player would reject; recorded, never a new bar"
                           % gap["miss_of"])
        if gap.get("late_confirmed") is False:
            return False, ("late: the miss of %s, called serious by the judge, but the second reader did not confirm "
                           "it a Problem a player would reject; recorded, never a new bar" % gap["miss_of"])
        # late_confirmed True blocks; None (not read yet) is held blocking until the second reader reads it
    kind = gap.get("bar_kind")
    if kind in ADVISORY_KINDS:
        return False, "the judge filed it as %s: not a bar (bar_rule.RULE_TEXT)" % kind
    found, words = detect(gap)
    if found:
        return False, "its demand pins %s (%r): not a bar (bar_rule.RULE_TEXT)" % (found, words)
    return True, None


def split(gaps):
    """-> (blocking, advisory): each advisory gap carries `advisory_why`."""
    keep, adv = [], []
    for g in gaps or []:
        if not isinstance(g, dict):
            continue
        b, why = blocks(g)
        if b:
            keep.append(g)
        else:
            adv.append(dict(g, advisory_why=why))
    return keep, adv


if __name__ == "__main__":
    import json
    import sys
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            v = json.load(f)
        for g in v.get("gaps") or []:
            b, why = blocks(g)
            print("%-5s %-8s %s%s" % (g.get("gid", "?"), "BLOCKS" if b else "advisory", str(g.get("what"))[:90],
                                      "" if b else "  <- %s" % why))
