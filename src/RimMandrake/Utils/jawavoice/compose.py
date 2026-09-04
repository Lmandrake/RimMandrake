"""Composite corpus-fit distance for the JAWAESE. Lower is better.

Each metric's deviation is normalised by the ORIGINAL corpus value so the
percentages and the raw means are comparable, then averaged. 'tic' is excluded: it fires on
the pronoun 'ta' (you), which a set of lines all addressed AT somebody will
legitimately repeat. Content-word concentration is reported separately.
"""
import sys, os, glob, collections

# Resolved from this file, not hardcoded: the repo moved G: -> D: on 2026-08-12
# and is reached by different paths from Windows Python and WSL.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jawafit

KEYS = ["redup", "h_rate", "apos", "vv", "wlen", "jw"]
# "ratio" (gloss words per Jawaese word) is REPORTED BUT NOT SCORED. The
# corpus glosses are fluent English; ours are deliberately clipped pidgin, so
# the corpus is not the target for that column. See README, "Pidgin glosses".
FUNC = {"mi","ta","ma","un","mob","loo","ne","lo","no","noo","to","na","so",
        "be","bu","boo","hah","hmph"}


def content_spread(P):
    lines = [jawafit.WORD.findall(j) for j, e in P]
    c = collections.Counter()
    for ws in lines:
        for w in set(x.lower() for x in ws):
            if w not in FUNC:
                c[w] += 1
    top = c.most_common(5)
    return 100.0 * top[0][1] / len(lines) if top else 0.0


def quiet(P):
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return jawafit.score(P, "x")


def main():
    os.chdir(os.path.join(_REPO_ROOT, "src", "RimStarWars", "JawaVoice", "Patches"))
    mine = ["JawaVoice_Insults.xml", "JawaVoice_Ideology.xml"]
    O = jawafit.pairs([f for f in glob.glob("*.xml") if f not in mine])
    t = quiet(O)

    import lines_insults as v5
    import lines_ideology as ideo
    cands = [("insults", v5.INSULT + v5.SLIGHT), ("ideology", ideo.ALL)]

    # v1 is recoverable from git; v2 is the current file on disk if not overwritten
    print("composite distance from the 639-line corpus (lower is better)\n")
    print("%-6s %8s   %s   %-7s" % ("", "DIST", "  ".join("%-7s" % k for k in KEYS), "ratio*"))
    # The corpus ratio (%.2f) is deliberately NOT printed as a target. Showing a
    # number in this column invites the next reader to converge on it, which is
    # exactly the regression this design rejects. See the footnote below.
    print("%-6s %8s   %s   %-7s" % ("TARGET", "0.000",
          "  ".join("%-7.2f" % t[k] for k in KEYS), "n/a"))
    best = None
    for name, P in cands:
        m = quiet(P)
        d = sum(abs(m[k] - t[k]) / max(1e-9, abs(t[k])) for k in KEYS) / len(KEYS)
        print("%-6s %8.3f   %s   %-7.2f  topword %.0f%%"
              % (name, d, "  ".join("%-7.2f" % m[k] for k in KEYS),
                 m["ratio"], content_spread(P)))
        if best is None or d < best[1]:
            best = (name, d)
    print("\nbest: %s (%.3f)" % best)
    print("""
* ratio (gloss words per Jawaese word) is REPORTED, NEVER SCORED, AND HAS NO
  TARGET. Do not pad the English back out to raise it.

  The corpus sits at %.2f and we sit near 1.67. That gap is the deliverable, not
  a defect. The corpus's own glosses are fluent English; ours are clipped pidgin
  by the owner's call of 2026-08-12, because a fluent gloss puts a paragraph of
  subtitle under four syllables of speech and nobody reads a paragraph floating
  over a pawn's head. Mean gloss went 10.4 words -> 7.3, longest 17 -> 10.

  The proof it was the right change is in this table: when the rewrite landed,
  EVERY Jawaese metric above stayed identical and only ratio moved. The English
  half changed; the language did not.

  See README 'Pidgin glosses', and the headers of JawaVoice_Insults.xml and
  JawaVoice_Ideology.xml, which say the same thing.""" % t["ratio"])


if __name__ == "__main__":
    main()
