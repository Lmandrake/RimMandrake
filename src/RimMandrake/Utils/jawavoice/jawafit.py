"""Score a set of Jawaese lines for how well they fit the established corpus.

Written BEFORE authoring v2, deliberately, so the targets are read off the
original 639 lines rather than tuned to whatever I happen to produce.

Metrics, all chosen because the corpus sample showed them by eye:
  redup      fraction of lines using reduplication (bab bab / mihsha mihshu /
             toobba toobbu / m'aahhat m'aahhau). The corpus's signature move.
  tic        most frequent word as a share of lines. High = a verbal crutch.
  h_rate     share of words containing breathy h (kaah, neehkooh, shaatoh).
  apos       share of words with a mid-word apostrophe (r'ebmoot, t'inlet).
  vv         share of words with a doubled vowel (oo/aa/ee).
  wlen       mean word length in characters.
  jw         mean Jawaese words per line.
  ratio      gloss words per Jawaese word.
"""
import re, io, glob, sys, statistics as st

PAT = re.compile(r'r_logentry\([^)]*\)(?:-&gt;|->)(.*?)</li>')
WORD = re.compile(r"[A-Za-z']+")


def pairs(files):
    out = []
    for f in files:
        for m in PAT.finditer(io.open(f, encoding="utf-8").read()):
            t = m.group(1).strip()
            g = re.search(r'\(([^()]*)\)\s*$', t)
            if g:
                out.append((t[:g.start()].strip(), g.group(1)))
    seen = set()
    return [r for r in out if not (r in seen or seen.add(r))]


def redup(words):
    """Two adjacent words sharing a 3+ char prefix, or identical."""
    for a, b in zip(words, words[1:]):
        a, b = a.lower(), b.lower()
        if a == b and len(a) >= 2:
            return True
        n = min(len(a), len(b))
        if n >= 3 and a[:3] == b[:3] and a != b:
            return True
    return False


def score(P, name):
    lines = [WORD.findall(j) for j, e in P]
    allw = [w.lower() for ws in lines for w in ws]
    freq = {}
    for w in allw:
        freq[w] = freq.get(w, 0) + 1
    top, topn = max(freq.items(), key=lambda kv: kv[1]) if freq else ("-", 0)
    # count LINES containing the top word, not raw occurrences
    topl = sum(1 for ws in lines if top in [w.lower() for w in ws])
    m = {
        "redup": 100.0 * sum(redup(ws) for ws in lines) / len(lines),
        "tic": 100.0 * topl / len(lines),
        "h_rate": 100.0 * sum('h' in w for w in allw) / len(allw),
        "apos": 100.0 * sum("'" in w for w in allw) / len(allw),
        "vv": 100.0 * sum(bool(re.search(r"(aa|oo|ee)", w)) for w in allw) / len(allw),
        "wlen": st.mean(len(w) for w in allw),
        "jw": st.mean(len(ws) for ws in lines),
        "ratio": st.mean(len(WORD.findall(e)) / max(1, len(WORD.findall(j)))
                         for j, e in P),
    }
    print("%-10s n=%-4d redup %5.1f%%  tic %5.1f%% (%s)  h %4.1f%%  apos %4.1f%%  "
          "vv %4.1f%%  wlen %4.2f  jw %4.2f  ratio %4.2f"
          % (name, len(P), m["redup"], m["tic"], top, m["h_rate"], m["apos"],
             m["vv"], m["wlen"], m["jw"], m["ratio"]))
    return m


if __name__ == "__main__":
    import os
    # Resolved from this file, not hardcoded: the repo moved G: -> D: on
    # 2026-08-12 and is reached differently from Windows Python and WSL.
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    os.chdir(os.path.join(_root, "src", "Jawa", "JawaVoice", "Patches"))
    mine = ["JawaVoice_Insults.xml", "JawaVoice_Ideology.xml"]
    extra = [f for f in sys.argv[1:]]
    O = pairs([f for f in glob.glob("*.xml") if f not in mine and f not in extra])
    print("TARGET = the original corpus. Closer to this row is better.\n")
    t = score(O, "ORIGINAL")
    score(pairs(["JawaVoice_Insults.xml"]), "v1 insult")
    score(pairs(["JawaVoice_Ideology.xml"]), "v1 ideo")
    for f in extra:
        if os.path.exists(f):
            score(pairs([f]), os.path.basename(f)[:10])
