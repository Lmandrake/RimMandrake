#!/usr/bin/env python3
"""
jawaese.py — the build-time "Jawaese agent" for the SpeakUp voice reskin
========================================================================

Turns ordinary RimWorld SpeakUp dialogue lines into Jawa-flavored speech of the
shape:

    <Jawaese>. (English meaning...)

e.g.  "Jit jot zoot goot. (Well, there goes everything...)"

DESIGN (grounded in jawa_dialogue_source_audit.md):
  Canon Jawaese is *untranslated gibberish* on screen — the meaning always lived
  in the subtitle, never the syllables (see audit §6, §11). So the faithful,
  scalable transform is: keep the vetted English as the parenthetical GLOSS (a
  translation "of the situation", which the audit's amended §10 explicitly
  permits) and put believable synthesized chitter in front of it. Where a real
  Ben Burtt phrase genuinely fits the moment, that canonical phrase OVERRIDES
  the synthesis (audit §3 Grade-A palette).

THREE TIERS (in priority order for any given line):
  1. CANON ANCHOR   — an exact §3 Grade-A phrase mapped to the situation.
  2. CHITTER        — a §4 untranslated fragment used verbatim as flavor.
  3. SYNTHESIS      — phonology-constrained invented Jawaese (the long tail).

Synthesis is DETERMINISTIC: seeded by a hash of the source English, so
regenerating produces identical output (clean git diffs, stable review).

POLICY GUARD: synthesized lines are creative pastiche. They must NEVER be
written back into jawa_dialogue_source_audit.md §3/§4 as if attested.

Pure stdlib. No game, no network.
"""

import hashlib
import re

# ---------------------------------------------------------------------------
# TIER 1 — CANON ANCHOR  (audit §3 Grade-A + canon-indexed additions)
# Each entry: canonical Jawa phrase + the licensed English meaning.
# These are matched to game SITUATIONS in speakup_map.py, not to words.
# ---------------------------------------------------------------------------
CANON = {
    "greeting":      ("M'um m'aloo.",     "Hello."),
    "yes":           ("Ibana.",           "Yes."),
    "no":            ("Nyeta.",            "No."),
    "stop":          ("Sabioto!",         "Stop!"),
    "okay":          ("Mambay.",          "Okay."),
    "goodbye":       ("Ubanya.",          "Good day."),
    "discovery":     ("Utinni!",          "A find!"),        # salvage/mineral/triumph
    "hands_off":     ("Togo togu!",       "Hands off!"),
    "mine":          ("Mombay m'bwa!",    "That's mine!"),
    "how_much":      ("Mob un loo?",      "How much?"),
    "thanks":        ("Taa baa.",         "Thanks."),
    "lets_go":       ("Ashuna! Ashuna!",  "Let's go!"),
    "dont_shoot":    ("Ny shootogawa!",   "Don't shoot!"),
    # canon-indexed (secondary): use sparingly
    "egg":           ("Monasuka!",        "The egg!"),
    "shut_up":       ("Omu'sata.",        "Quiet."),
    "bargain":       ("Bom'loo.",         "A bargain."),
}

# ---------------------------------------------------------------------------
# TIER 2 — CHITTER  (audit §4 untranslated fragments; Grade C/D)
# Used verbatim as ambient flavor. NO English gloss is invented for these —
# none is attested, and inventing one is the actual §10 violation. Good for
# idle / low-information moments where a gloss would be noise.
# ---------------------------------------------------------------------------
CHITTER = [
    "Nengo bah.", "Bahbit.", "Areeba.", "Pee netto oh!", "Chee goot.",
    "Bobaloo!", "Habba habba da oon da oon.", "Guak wa neenee cha ba?",
    "Steika ba!", "Bo shuda!", "Zookeyneee wa na be.", "Bowa zootaneenee!",
]

# ---------------------------------------------------------------------------
# TIER 3 — SYNTHESIS  (phonology inferred from the corpus; [inference])
# Consonants/vowels/finals weighted toward observed Jawa forms:
#   doubled vowels (Utinni, m'aloo, Bom'loo), glottal apostrophes (m'um,
#   m'bwa), reduplication (Togo togu, Ashuna Ashuna, habba habba), CV-heavy
#   open syllables, finals in -oo/-ah/-a/-ee/-ay/-o/-oot.
# ---------------------------------------------------------------------------
_ONSETS = ["m", "b", "n", "t", "k", "z", "s", "w", "g", "h", "sh", "ny", "l", "r",
           "m", "b", "n", "t"]  # weight the corpus-frequent ones
_VOWELS = ["a", "o", "u", "e", "i", "oo", "aa", "ee", "a", "o", "oo"]  # weight open/doubled
_FINALS = ["", "", "", "n", "t", "b", "h"]  # most syllables open; light coda
_WORD_FINAL_FLAIR = ["", "", "", "!", "?", "..."]  # applied to whole utterance


def _rng(seed_text):
    """Deterministic PRNG from a string seed (stable across runs)."""
    h = hashlib.sha256(seed_text.encode("utf-8")).digest()
    state = int.from_bytes(h[:8], "big")

    def nxt(n):
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return (state >> 17) % n
    return nxt


def _syllable(nxt):
    on = _ONSETS[nxt(len(_ONSETS))]
    vo = _VOWELS[nxt(len(_VOWELS))]
    fi = _FINALS[nxt(len(_FINALS))]
    return on + vo + fi


def _word(nxt):
    n = 1 + nxt(2)  # 1-2 syllables per word, occasionally reduplicated below
    w = "".join(_syllable(nxt) for _ in range(n))
    # ~1 in 4 words get a glottal apostrophe after the first consonant
    if nxt(4) == 0 and len(w) > 2:
        w = w[0] + "'" + w[1:]
    return w


def synth(english, min_words=None, max_words=None):
    """Synthesize deterministic Jawaese chitter sized to the English line."""
    nxt = _rng(english)
    # scale word count to the English length, clamped to a speakable range
    approx = max(1, len(english.split()))
    lo = min_words if min_words is not None else max(1, min(2, approx))
    hi = max_words if max_words is not None else max(2, min(5, approx))
    n = lo + (nxt(max(1, hi - lo + 1)))
    words = []
    for i in range(n):
        w = _word(nxt)
        # occasional reduplication (corpus: "Togo togu", "habba habba")
        if nxt(6) == 0:
            w = w + " " + (w if nxt(2) else w[:-1] + ("u" if not w.endswith("u") else "a"))
        words.append(w)
    utt = " ".join(words)
    utt = utt[0].upper() + utt[1:]
    tail = _WORD_FINAL_FLAIR[nxt(len(_WORD_FINAL_FLAIR))]
    if not utt.endswith(("!", "?", ".")):
        utt = utt + (tail if tail else ".")
    return utt


# ---------------------------------------------------------------------------
# PUBLIC: transform one English SpeakUp output line into a Jawa line.
# ---------------------------------------------------------------------------
def jawaify(english, anchor=None, chitter=False):
    """
    english : the original SpeakUp output text (kept as the gloss).
    anchor  : optional CANON key; if set and it fits, use the canonical phrase.
    chitter : if True and english is trivial/idle, emit a §4 fragment, no gloss.

    Returns the replacement string.
    """
    english = english.strip()

    # Preserve pure-symbol or empty lines untouched (e.g. "..." or "[symbol]").
    if english in ("", "...") or re.fullmatch(r"\[[^\]]+\]", english):
        # idle/ellipsis -> a soft chitter with no gloss
        if english == "..." :
            nxt = _rng("ellipsis:" + english)
            return "*" + ["chitters", "mutters", "grumbles", "trills"][nxt(4)] + "*"
        return english

    if anchor and anchor in CANON:
        jw, gloss = CANON[anchor]
        return f"{jw} ({english})"

    if chitter:
        nxt = _rng("chit:" + english)
        return CHITTER[nxt(len(CHITTER))]

    return f"{synth(english)} ({english})"


if __name__ == "__main__":
    # quick self-demo
    samples = [
        ("Well, there goes everything...", None, False),
        ("A find!", "discovery", False),
        ("Don't shoot!", "dont_shoot", False),
        ("How much?", "how_much", False),
        ("What nice weather we're having!", None, False),
        ("This tastes a little funny!", None, False),
        ("...", None, False),
    ]
    print("Jawaese synthesis demo (deterministic):\n")
    for en, anc, ch in samples:
        print(f"  EN: {en!r}")
        print(f"  JW: {jawaify(en, anchor=anc, chitter=ch)}\n")
