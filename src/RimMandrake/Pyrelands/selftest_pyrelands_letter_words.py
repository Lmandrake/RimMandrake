#!/usr/bin/env python3
"""selftest_pyrelands_letter_words: firehawk_rewards_live.letter_names_ember, the sighting letter's ember test (offline).

Visit 2 (2026-11-20): the live letter read "...in its beak: A burning sprig of ember grass, ..." and the row failed it,
because the ember phrase starts the clause and the game capitalises it (GrammarResolverSimple CapitalizeSentences) while
the row compared case-sensitively. Run: python3 <this file>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import firehawk_rewards_live as R  # noqa: E402

LIVE = ("Fire-hawk is over your colony right now with a live ember in its beak: A burning sprig of ember grass, "
        "snatched from the fire cells to the .")
BURN, PLANT = "a burning twig", "a burning sprig of "
CASES = [
    ("the live letter (capitalised sprig) names its ember", R.letter_names_ember(LIVE, BURN, PLANT) is True),
    ("a burning twig, lower case, names its ember", R.letter_names_ember("...beak: a burning twig, snatched", BURN, PLANT) is True),
    ("a letter with no ember phrase does not", R.letter_names_ember("Fire-hawk is over your colony right now.", BURN, PLANT) is False),
    ("an empty letter does not", R.letter_names_ember("", BURN, PLANT) is False),
]


def main():
    bad = 0
    for what, ok in CASES:
        print("%s %s" % ("PASS" if ok else "FAIL", what))
        bad += 0 if ok else 1
    print("selftest_pyrelands_letter_words: %d of %d checks failed" % (bad, len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
