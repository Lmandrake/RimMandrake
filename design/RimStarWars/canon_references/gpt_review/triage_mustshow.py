#!/usr/bin/env python3
"""Give every bullet of MUSTSHOW_PROPOSALS.md a disposition and apply the accepted ones (CANON_FAUNA_FLORA_GPT_REVIEW_1).
Dispositions: APPLIED (text placed in the entry's ## Must show), MET (the entry already says it: the 2026-10-09 Must-show
rollout rewrote these lists after the proposals were written), OWNER (touches a ## ruling or an owner-supplied line:
delegation_policy.md s2.4, filed as OWNER_ITEM), REJECTED (a default, below). Decided by this seat under delegation_policy
s2 (a Must show line that no ruling names is delegated; the judge did not write the proposals). Idempotent.
usage: triage_mustshow.py"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
OWNER_ITEM = "CANON_RULED_LINES_JUDGE_WIKI_SAYS_OTHERWISE"
DEFAULT = ("Demotes a Must show line to a provenance label or optional, or only comments on it. AGENT_BRIEF: the checklist "
           "follows the images, and Must show is the pass bar; the text being silent is no reason to loosen it.")
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
}
OWNER = {
    ("dewback", 0): "Must show says long heavy tail and NEGATIVE 'not short-tailed'; canon text (A New Hope) says short tails. The ruled image decides: keep or change?",
    ("greaterkraytdragon", 2): "Must show says bright yellow-white spit, no green; canon says greenish-yellow acid. Ruled render: keep or change?",
    ("eopie", 0): "Must show says never brown; canon gives no colour, Legends lists brown. Ruled image: keep or change?",
    ("zakkeg", 1): "The ruled file wookieepedia_kotor2_juvenile.png is a SWTOR Cartel Market pet render, not KOTOR II. Does the ruling stand knowing that?",
    ("gorg", 1): "Your supplied line says two legs only; the wiki gives no limb count and the film gorg has feet front and back. Keep?",
    ("gizka", 1): "The vestigial wording in your ruling: GPT suggests dropping it. Keep?",
}
MET = {("acklay", 0), ("blixus", 1), ("blixus", 2), ("bogwing", 0), ("hssiss", 0), ("insectomorph", 2), ("snoruuk", 0), ("strill", 0),
       ("nerf", 0), ("nuna", 0), ("nuna", 1), ("krykna", 0), ("krykna", 1), ("kreetle", 0), ("dianoga", 1), ("porg", 0), ("cancell", 0),
       ("kwi", 1), ("zeer", 0), ("varactyl", 0), ("voorpak", 0), ("voorpak", 1), ("convor", 1), ("cannok", 0), ("fanback", 1),
       ("kybuck", 0), ("klorslug", 0), ("klorslug", 1), ("falumpaset", 0), ("iridonianreek", 0), ("borcatu", 0), ("scurrier", 0),
       ("wyyyschokk", 1), ("kraytdragon", 0), ("kraytdragon", 1), ("greaterkraytdragon", 0), ("gutkurr", 0), ("dragonsnake", 0)}

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

def main():
    src = open(os.path.join(HERE, "MUSTSHOW_PROPOSALS.md"), encoding="utf-8").read()
    rows = []
    for e in re.split(r"^### ", src, flags=re.M)[1:]:
        slug = e.split("\n")[0].strip()
        for i, b in enumerate(re.findall(r"^- .*$", e, re.M)):
            k = (slug, i)
            if k in APPLY: d, why, text = "APPLIED", "Verified fact, adds to or corrects the bar, conflicts with no ruling.", apply(slug, APPLY[k])
            elif k in OWNER: d, why, text = "OWNER", OWNER[k], None
            elif k in MET: d, why, text = "MET", "The current Must show already carries this (rollout 2026-10-09 or a later ruling).", None
            else: d, why, text = "REJECTED", DEFAULT, None
            rows.append({"entry": slug, "n": i, "proposal": b[2:], "disposition": d, "why": why, "applied_text": text})
    keys = {(r["entry"], r["n"]) for r in rows}
    missing = (set(APPLY) | set(OWNER) | MET) - keys
    if missing: raise SystemExit(f"table names unknown bullets: {sorted(missing)}")
    json.dump({"owner_item": OWNER_ITEM, "rows": rows}, open(os.path.join(HERE, "MUSTSHOW_TRIAGE.json"), "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(len(rows), dict(Counter(r["disposition"] for r in rows)))
main()
