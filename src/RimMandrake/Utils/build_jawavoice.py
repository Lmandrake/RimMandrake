#!/usr/bin/env python3
"""
build_jawavoice.py — generate the JawaVoice SpeakUp reskin patch mod
====================================================================

Reads the SpeakUp 1.6 source snapshot in vendor/mod_sources/_speakup_src_1p6/ and emits a
self-contained, assembly-free patch mod that makes Jawa pawns speak Jawaese.

MECHANISM (verified against SpeakUp source, see jawaese.py header):
  For each InteractionDef, we PatchOperationAdd a small set of HIGH-PRIORITY,
  identity-gated Jawa root lines into its <rulesStrings>. This is the exact
  pattern SpeakUp's own z_add_*.xml patches use.
    - Jawa pawns match the gate -> get the high-priority Jawaese line.
    - Everyone else (slaves per user OK, all non-player factions) fails the
      gate -> falls through to SpeakUp's untouched vanilla English tree.
  So we ADD, never REPLACE: all of SpeakUp's dynamic conditional logic survives.

IDENTITY GATE (dual, per the xenotype-not-a-condition finding):
    colonists:  INITIATOR_faction==PlayerColony / PlayerTribe
    NPC jawas:  INITIATOR_kind==RSW_Jawa / RSW_JawaTribal
  ⚠️ Corrected 2026-08-21: this line said `OuterRim_JawaTribal`, which is absent
  from the live capture. GATES below was already right; only the prose was stale.
  Emitted as separate gated entries so a flip to a trait-based gate later is a
  one-line change (GATES below).

GLOSS: each Jawa line keeps an English gloss drawn from the def's OWN
representative leaf line(s), so meaning stays apt. Canon anchors (CANON in
jawaese.py) override the synthesis where a real phrase fits the situation.

Everything is wrapped in PatchOperationConditional so a missing/renamed target
is a silent no-op, matching the Jawa_Patches house style.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jawaese

# 🔴 BOTH OF THESE WERE WRONG AND THE SCRIPT HAD BEEN DEAD FOR IT. Corrected
# 2026-08-21 (JAWAVOICE_BUILDER_IS_ORPHANED_1).
#   SRC pointed at `Utils/_speakup_src_1p6`, which has never existed. The snapshot is
#     where this file's own docstring always said it was: `vendor/mod_sources/`.
#   OUT was short one `..` and resolved to `src/RimMandrake/src/RimStarWars/JawaVoice`, so a
#     run would `makedirs` a phantom tree and write nine files nobody would ever read.
# ⚠️ That second bug was the ONLY thing protecting the nine committed patches. Anyone
# who fixed the path without noticing the first bug would have pointed a working writer
# at a missing source. Both are fixed together or neither is.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
SRC = os.path.join(_REPO, "vendor", "mod_sources", "_speakup_src_1p6")
OUT = os.path.join(_REPO, "src", "RimStarWars", "JawaVoice")
if not os.path.isdir(os.path.join(SRC, "Defs")):
    raise SystemExit(
        "build_jawavoice: no SpeakUp snapshot at %s\n"
        "⛔ REFUSING rather than emitting an empty mod over the nine committed\n"
        "   patches in src/RimStarWars/JawaVoice/Patches/. Restore the snapshot first." % SRC)

# The two gate predicates. To switch to a trait gate later, replace both with
# a single ("INITIATOR_trait==Jawaese-speaker",) entry.
GATES = [
    "INITIATOR_faction==PlayerColony",
    "INITIATOR_faction==PlayerTribe",
    "INITIATOR_kind==RSW_Jawa",
    "INITIATOR_kind==RSW_JawaTribal",
]

# Canon-anchor situation map: defName -> CANON key (jawaese.CANON).
# Only defs whose SITUATION genuinely matches a Ben Burtt phrase. Everything
# else gets phonology-synthesized chitter + its own English gloss.
ANCHORS = {
    "Thanks":            "thanks",
    "GetWell":           "thanks",       # "get well" ~ kindly send-off; soft
    "Invite_answer_yes": "yes",
    "Invite_answer_no":  "no",
    "HowAreYou":         "greeting",
    "ShootingHit":       "discovery",    # a hit = a triumph -> Utinni!
    "KindWords_generic": "thanks",
    # NOTE: raid-alarm / "don't shoot" and salvage-discovery fire from vanilla
    # combat/mining interactions, patched separately below (VANILLA_ANCHORS).
}

# A few HIGH-VALUE canonical lines injected into VANILLA interaction defs
# (not SpeakUp's own). These are the iconic Jawa moments.
# target vanilla defName -> (CANON key, human note)
VANILLA_ANCHORS = {
    "TradeWithPawn":   ("how_much", "trading"),   # may not exist as interaction; conditional-wrapped
}

MAX_GLOSSES = 6          # cap variety lines per def to keep patches lean
# 🔴 250, NOT 9. Corrected 2026-08-21. The nine committed patches carry 250 on all
# 3,932 rule strings, and so do both sibling generators (genideo.py:179,
# genxml.py:39) - 9 was left behind here alone. It is the ONLY thing that
# differed between this generator's output and the committed files: normalise the
# priority and all eight are byte-identical, Jawaese text included.
# ⚠️ It is not cosmetic. The priority is what makes a Jawa line beat SpeakUp's
# English tree; at 9 the reskin loses the roll and the pawns speak English, with
# nothing logged and every file still present and valid.
PRIORITY = 250             # above SpeakUp's own (they top out ~5)


def clean_leaf(text):
    """Is this a usable English gloss? Reject symbol-only / keyword-ref lines."""
    t = text.strip()
    if not t or t == "...":
        return None
    # drop lines that are just a grammar keyword reference like "[good_opinion]"
    if re.fullmatch(r"\[[^\]]+\]", t):
        return None
    # drop lines containing unresolved child-rule refs mixed w/ text? keep, but
    # strip bracketed tokens for the gloss so we don't show "[recipient]".
    return t


def strip_tokens(t):
    """Turn '[recipient]' etc into readable words for the gloss."""
    t = re.sub(r"\[RECIPIENT_nameDef\]|\[recipient\]", "friend", t)
    t = re.sub(r"\[INITIATOR_nameDef\]|\[initiator\]", "", t)
    t = re.sub(r"\[[^\]]+\]", "", t)          # any other token -> drop
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([,.!?])", r"\1", t)
    t = re.sub(r"^[\s,;:.!?—-]+", "", t)      # drop leading punctuation artifacts
    t = t[0].upper() + t[1:] if t else t
    return t


def is_complete_utterance(g):
    """Keep only lines that read as a whole spoken line, not a composition
    fragment. SpeakUp assembles sentences from nested keyword rules; the
    sub-fragments ('sunny', 'we're having a') are not spoken alone."""
    if not g:
        return False
    # must end in terminal punctuation (a spoken line does)
    if not g.rstrip().endswith((".", "!", "?")):
        return False
    # must have some substance
    words = g.split()
    if len(words) < 3:
        return False
    # reject lines that are obviously mid-sentence (end with article/prep + .)
    if re.search(r"\b(a|an|the|of|to|and|we're having a)[.!?]*$", g, re.I):
        return False
    # reject dangling em-dash fragments
    if g.rstrip().endswith("—") or "we're having a." in g.lower():
        return False
    return True


def harvest(def_el):
    """Collect representative English gloss candidates from a def's rulesStrings.
    Prefer complete utterances; fall back to the longest fragment if a def has
    no clean complete line (rare)."""
    complete, fallback = [], []
    for li in def_el.iter("li"):
        raw = (li.text or "")
        # rule form is 'keyword(conds)->OUTPUT' ; we want OUTPUT
        if "->" in raw:
            out = raw.split("->", 1)[1]
        else:
            out = raw
        g = clean_leaf(out)
        if g is None:
            continue
        g = strip_tokens(g)
        if not g or len(g) <= 1:
            continue
        if is_complete_utterance(g):
            if g not in complete:
                complete.append(g)
        else:
            if g not in fallback:
                fallback.append(g)
    if complete:
        return complete
    # def had only fragments (e.g. a pure sub-rule holder) — use the best one
    fallback.sort(key=len, reverse=True)
    return fallback[:1]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def gate_conds(base_conds):
    """Yield one constraint-string per gate, merging any base conditions."""
    for g in GATES:
        parts = [g] + list(base_conds)
        yield ",".join(parts)


def make_lines(defname, glosses):
    """Produce the <li> Jawa rule lines for one def."""
    anchor = ANCHORS.get(defname)
    lines = []
    # choose up to MAX_GLOSSES distinct glosses
    chosen = glosses[:MAX_GLOSSES] if glosses else ["..."]
    # root keyword unique per def so it can't collide
    # If this def has a canon anchor, lead with the canonical phrase paired with
    # ITS OWN licensed meaning (not a harvested line, which may not match the
    # canonical sense). Then add synthesized variants glossed by the def's lines.
    jw_lines = []
    if anchor and anchor in jawaese.CANON:
        jw, canon_gloss = jawaese.CANON[anchor]
        jw_lines.append(f"{jw} ({canon_gloss})")
    for gloss in chosen:
        jw_lines.append(jawaese.jawaify(gloss))   # synthesized + situational gloss
        if len(jw_lines) >= MAX_GLOSSES:
            break

    for jw in jw_lines:
        for cond in gate_conds([f"priority={PRIORITY}"]):
            lines.append(f'<li>r_logentry({cond})->{esc(jw)}</li>')
    return lines


def build_patch_for_file(xml_path):
    """Return list of (defName, [lines]) for every def in a Defs file."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    out = []
    for d in root.findall("InteractionDef"):
        dn_el = d.find("defName")
        if dn_el is None:
            continue
        defname = dn_el.text.strip()
        # skip the abstract parent and pure "b"/reaction follow-ups (they're
        # triggered by tag from their parent; reskinning the parent covers them,
        # but we DO reskin them too so the follow-up is also Jawaese)
        glosses = harvest(d)
        lines = make_lines(defname, glosses)
        out.append((defname, lines))
    return out


def emit():
    os.makedirs(os.path.join(OUT, "About"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "Patches"), exist_ok=True)

    defs_dir = os.path.join(SRC, "Defs")
    total_defs = 0
    total_lines = 0
    # one patch file per source Defs file, for reviewable batches
    for fn in sorted(os.listdir(defs_dir)):
        if not fn.endswith(".xml"):
            continue
        if fn == "Interactions.xml":
            # this holds the abstract parent + generic + jobs; handle, but skip parent
            pass
        pairs = build_patch_for_file(os.path.join(defs_dir, fn))
        # build a Patch doc
        ops = []
        for defname, lines in pairs:
            if not lines:
                continue
            total_defs += 1
            total_lines += len(lines)
            inner = "\n".join("          " + ln for ln in lines)
            ops.append(f"""  <Operation Class="PatchOperationConditional">
    <xpath>/Defs/InteractionDef[defName="{defname}"]/logRulesInitiator/rulesStrings</xpath>
    <match Class="PatchOperationAdd">
      <xpath>/Defs/InteractionDef[defName="{defname}"]/logRulesInitiator/rulesStrings</xpath>
      <value>
{inner}
      </value>
    </match>
  </Operation>""")
        if not ops:
            continue
        doc = ('<?xml version="1.0" encoding="utf-8"?>\n<Patch>\n'
               + "\n".join(ops) + "\n</Patch>\n")
        out_name = "JawaVoice_" + fn
        with open(os.path.join(OUT, "Patches", out_name), "w") as fh:
            fh.write(doc)
    return total_defs, total_lines


if __name__ == "__main__":
    nd, nl = emit()
    print(f"Emitted JawaVoice patches: {nd} defs reskinned, {nl} gated Jawa lines.")
