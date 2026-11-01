#!/usr/bin/env python3
"""Carry out mustshow_decisions.txt: one hand-judged line per MUSTSHOW_PROPOSALS.md bullet (CANON_FAUNA_FLORA_GPT_REVIEW_1).
Dispositions: APPLIED (edit below placed in the entry's ## Must show), MET (the entry already says it; the line quotes where),
OWNER (touches a ruling and contradicts a source: filed in OWNER_ITEM, delegation_policy.md s2.4), REJECTED (a reason of its own).
There is no default: a bullet without a decision line stops the run. Decided by this seat under delegation_policy s2; every
applied edit is logged `delegated:` on OWNER_ITEM, the ones on a ruled entry named as such. Idempotent.
usage: triage_mustshow.py"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
OWNER_ITEM = "CANON_RULED_LINES_JUDGE_WIKI_SAYS_OTHERWISE"
# (slug, bullet index): (mode, needle or new text); mode 'add' inserts a line before NEGATIVE, 'sub' replaces text.
APPLY = {
    ("acklay", 3): ("add", "Three eyes on the head (canon infobox distinction, *Attack of the Clones*)"),
    ("bantha", 1): ("add", "A long tail dragging on the ground and wide flat four-digit feet, where the fur lets them show (canon page)"),
    ("horax", 0): ("add", "Enormous scale: towers over a humanoid, over 15 m tall (Legends infobox, Databank)"),
    ("lavaflea", 0): ("sub", ("Mount sized: a rider sits on its back, back about waist-to-chest height of a person",
                              "Mount sized: a rider sits on its back; canon height 4-5 m (canon infobox)")),
    ("neebray", 0): ("sub", ("thin whip tendrils trailing below the jaw", "one long tendril under the jaw (canon page; a stub on infants)")),
    ("worrt", 0): ("add", "Long purple prehensile tongue from the very large mouth (canon distinction, *Return of the Jedi*)"),
    ("mynock", 0): ("add", "Adult scale: 1.6 to 2 m long, 8 kg (canon infobox), not cat-sized"),
    ("coloclawfish", 0): ("add", "Giant scale: canon length 40 m (canon infobox, Databank)"),
    ("coloclawfish", 1): ("sub", ("Mandible-like jaw appendages (Legends render) kept subtle, not required in canon art",
                                  "Mandible-like jaw appendages, kept subtle (canon prose lists \"a set of mandibles\")")),
    ("kraytdragon", 2): ("add", "Leviathan scale: 184 m long, 28.68 m tall (canon infobox)"),
    ("shaaks", 0): ("add", "About 1.8 m tall (canon infobox, Databank): giant for its egg shape, not ronto-sized"),
    ("gelagrub", 0): ("add", "About 4 m long (canon infobox)"),
    ("skalders", 1): ("add", "About 3.5 m tall (canon and Legends infoboxes)"),
    ("iridonianreek", 1): ("add", "Scale: about 2.24 m tall, 4 m long (canon infobox)"),
    ("dalgo", 1): ("add", "Three forward-facing nostrils (canon infobox distinction)"),
    ("orray", 0): ("add", "State shown is one of two canon forms: wild with a long intact tail, or arena mount with the tail cut and the stump metal-capped, saddled"),
    ("blixus", 0): ("add", "Canon scale: 6.48 m high, 13.33 m long (Databank infobox)"),
    ("blurrg", 1): ("add", "About 2 m tall, up to 2.5-3 m on Endor (canon page; it gives no hip or shoulder reference point)"),
    ("blurrg", 2): ("add", "Hip joints set unusually high on the body (canon text)"),
    ("lothcat", 1): ("add", "Canon size: 0.54 m tall, 0.94 m long (canon infobox)"),
    ("teemuss", 0): ("sub", ("and a hooked dark lower tusk below the chin", "and two hooked dark tusks on the lower jaw (Legends prose: \"two tusks on their lower jaw\")")),
    ("nuna", 0): ("sub", ("a heavy domed/ridged shell-like back rising to a peak", "a heavy hunched domed/ridged back rising to a peak")),
    ("womprat", 0): ("add", "Canon size: slightly over 2 m (canon text; the axis is not stated)"),
    ("worrt", 1): ("add", "About 1.5 m tall (Databank, canon page)"),
    ("scurrier", 0): ("sub", ("with a near-horizontal trunk", "with a near-horizontal trunk at rest, fully horizontal when running on all fours")),
    ("scurrier", 1): ("sub", ("(males thick and curved, females thin and straight)", "(Legends only: males thick and curved, females thin and straight)")),
    ("varactyl", 0): ("add", "Canon scale: 15 m long, 4 m at the shoulder (Databank)"),
    ("uvak", 2): ("sub", ("a single pale emerald/teal eye on each side", "a single pale emerald/teal eye on each side, set well forward on the skull (prose: \"at the front of their heads\")")),
}
def must_section(t):
    m = re.search(r"^## Must show\n(.*?)(?=^## )", t, re.M | re.S)
    return m.span(1) if m else None

def apply(slug, op):
    p = os.path.join(LIB, slug, "description.md")
    t = open(p, encoding="utf-8").read()
    a, b = must_section(t)
    sec = t[a:b]
    mode, arg = op
    if mode == "sub":
        if arg[1] in sec: return arg[1]
        if arg[0] not in sec: raise SystemExit(f"{slug}: needle gone: {arg[0]}")
        sec, text = sec.replace(arg[0], arg[1]), arg[1]
    else:
        text = arg
        if text not in sec:
            line = f"- [ ] {text}\n"
            i = sec.find("- [ ] NEGATIVE")
            if i < 0: sec = sec.rstrip("\n") + "\n" + line + "\n"
            else: sec = sec[:i] + line + sec[i:]
    open(p, "w", encoding="utf-8").write(t[:a] + sec + t[b:])
    return text

def decisions():
    out = {}
    for ln in open(os.path.join(HERE, "mustshow_decisions.txt"), encoding="utf-8"):
        if ln.startswith("#") or not ln.strip(): continue
        head, why, quote = [x.strip() for x in ln.rstrip("\n").split(" ~", 2)]
        slug, n, d = head.split()
        if (slug, int(n)) in out: raise SystemExit(f"two decisions for {slug} {n}")
        out[(slug, int(n))] = (d, why.strip(), quote.lstrip("~ ").strip())
    return out

def ruled(slug):
    t = open(os.path.join(LIB, slug, "description.md"), encoding="utf-8").read()
    m = re.search(r"^## ruling\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    body = m.group(1).strip() if m else ""
    return bool(body) and not body.startswith("(empty")

def main():
    src = open(os.path.join(HERE, "MUSTSHOW_PROPOSALS.md"), encoding="utf-8").read()
    dec = decisions()
    rows = []
    for e in re.split(r"^### ", src, flags=re.M)[1:]:
        slug = e.split("\n")[0].strip()
        for i, b in enumerate(re.findall(r"^- .*$", e, re.M)):
            k = (slug, i)
            if k not in dec: raise SystemExit(f"no decision for {slug} {i}: {b[:70]}")
            d, why, quote = dec.pop(k)
            if (d == "APPLIED") != (k in APPLY): raise SystemExit(f"{slug} {i}: {d} disagrees with APPLY")
            r = {"entry": slug, "n": i, "proposal": b[2:], "disposition": d, "why": why, "ruled_entry": ruled(slug)}
            if d == "APPLIED": r["applied_text"] = apply(slug, APPLY[k])
            if d == "MET": r["met_quote"] = quote
            rows.append(r)
    if dec: raise SystemExit(f"decisions for unknown bullets: {sorted(dec)}")
    json.dump({"owner_item": OWNER_ITEM, "rows": rows}, open(os.path.join(HERE, "MUSTSHOW_TRIAGE.json"), "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(len(rows), dict(Counter(r["disposition"] for r in rows)))
    print("ruled entries edited:", sorted({r["entry"] for r in rows if r["disposition"] == "APPLIED" and r["ruled_entry"]}))
main()
