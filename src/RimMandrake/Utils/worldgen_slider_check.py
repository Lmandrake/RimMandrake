#!/usr/bin/env python3
"""Check that no mod keeps a biome-rarity slider without its removal owed (the permanent no-worldgen ruling).

A biome-rarity slider is a Mod Settings slider whose value a BiomeWorker's GetScore reads. It acts only when a world is
generated, so it is "a setting that could roll a second world" (design/RimMandrake/standing_rulings.md §There is no
worldgen feature). Item RIMMANDRAKE_CHECK_BIOME_RARITY_SLIDERS_AGAINST_NO_WORLDGEN_RULING.

A mod passes when one of these is true:
  - its source has no such slider; or
  - its design.md does not call the scorer or the slider "not yet his" (the ruling already decides), and its section of
    the conversion list holds a WORLDGEN-SETTING row, which the Designer packet carries into its next version.

Exit 0: every mod passes. 1: a mod fails (named). 2: could not look (cause named). Nothing is printed that could pass
for a verdict before the verdict line.
"""
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = "src/RimMandrake"
CONVERSION_LIST = "design/specs/2026-11-21-guiding-principles/conversion_list.md"
SLIDER = re.compile(r"(\w*[Rr]arity\w*)\s*=\s*\w+\.Slider\(\s*\1\s*,")
SCORE = re.compile(r"override\s+float\s+GetScore\s*\(")
NOT_YET = re.compile(r"not yet his", re.I)
SCORER_WORDS = re.compile(r"rarity|scor(er|ing)|placement worker", re.I)


def read(p):
    with open(p, encoding="utf-8", errors="strict") as f:
        return f.read()


def cs_files(mod_dir):
    for root, dirs, files in os.walk(mod_dir):
        dirs[:] = [d for d in dirs if d not in ("obj", "bin")]
        for n in files:
            if n.endswith(".cs"):
                yield os.path.join(root, n)


def sliders(mod_dir):
    """-> sorted names of rarity sliders whose field a GetScore file of the same mod reads."""
    texts = {p: read(p) for p in cs_files(mod_dir)}
    fields = {m.group(1) for t in texts.values() for m in SLIDER.finditer(t)}
    # A reader is a GetScore override, a Harmony patch on a GetScore, or a kernel's BiomeScore call (Warscar's slider is
    # read by a postfix on BiomeWorker_Scarlands.GetScore, with no override in the mod).
    readers = [t for t in texts.values() if SCORE.search(t) or "BiomeScore(" in t or "GetScore" in t]
    return sorted(f for f in fields if any(re.search(r"\b%s\b" % re.escape(f), t) for t in readers))


def sections(text):
    out, cur, buf = {}, None, []
    for ln in text.split("\n"):
        if ln.startswith("## "):
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur, buf = ln[3:].strip(), []
        elif cur is not None:
            buf.append(ln)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def bullets(text):
    """-> each `- ` bullet of a markdown text joined with its continuation lines."""
    out, cur = [], None
    for ln in text.split("\n"):
        if re.match(r"^\s*- ", ln):
            if cur is not None:
                out.append(cur)
            cur = ln.strip()
        elif cur is not None and ln.startswith("  ") and ln.strip():
            cur += " " + ln.strip()
        else:
            if cur is not None:
                out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    return out


def main(repo=REPO):
    try:
        secs = sections(read(os.path.join(repo, CONVERSION_LIST)))
        mods = sorted(d for d in os.listdir(os.path.join(repo, SRC)) if os.path.isdir(os.path.join(repo, SRC, d)))
    except (OSError, UnicodeDecodeError) as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    fails, owed, looked = [], [], 0
    for mod in mods:
        try:
            found = sliders(os.path.join(repo, SRC, mod))
        except (OSError, UnicodeDecodeError) as e:
            print("COULD NOT LOOK: %s/%s: %s" % (SRC, mod, e))
            return 2
        looked += 1
        if not found:
            continue
        head = next((h for h, b in secs.items() if "`%s/%s/`" % (SRC, mod) in b), None)
        if head is None:
            fails.append("%s: slider %s, and %s has no section whose Folders line names %s/%s/" % (
                mod, ",".join(found), CONVERSION_LIST, SRC, mod))
            continue
        why = []
        if "WORLDGEN-SETTING" not in secs[head]:
            why.append("%s §%s has no WORLDGEN-SETTING row" % (CONVERSION_LIST, head))
        dp = os.path.join(repo, "design", "concepts", head, "design.md")
        try:
            dtext = read(dp)
        except FileNotFoundError:
            dtext = ""
            why.append("design/concepts/%s/design.md is absent" % head)
        except (OSError, UnicodeDecodeError) as e:
            print("COULD NOT LOOK: %s: %s" % (dp, e))
            return 2
        for b in bullets(dtext):
            if NOT_YET.search(b) and SCORER_WORDS.search(b):
                why.append("design/concepts/%s/design.md still calls it not yet his: %s" % (head, b))
        if why:
            fails.append("%s (%s): slider %s: %s" % (mod, head, ",".join(found), "; ".join(why)))
        else:
            owed.append("%s (%s)" % (mod, head))
    if looked == 0:
        print("COULD NOT LOOK: no mod folders under %s" % SRC)
        return 2
    for f in fails:
        print("FAIL  " + f)
    print("%s: %d mod folders read; %d keep a biome-rarity slider with its removal owed (%s); %d fail" % (
        "HOLDS" if not fails else "FAILS", looked, len(owed), ", ".join(owed) or "none", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else REPO))
