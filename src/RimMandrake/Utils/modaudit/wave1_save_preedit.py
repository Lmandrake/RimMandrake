#!/usr/bin/env python3
r"""wave1_save_preedit.py -- write an EDITED COPY of a RimWorld save with RETIREMENT WAVE 1's save repairs.

Never edits the input. Binary mode throughout (a text-mode write turns LF into CRLF and corrupts the save:
CLAUDE.md "Savegame text-mode CRLF trap"). Removes exactly:
  1. the map <thing Class="MinifiedThing"> elements whose inner thing is a Wall (MinifyEverything packed them;
     without that mod a minified linked wall has no minifiedDef and may draw wrongly). Measured 2026-10-10:
     11 at cells x 39-54, z 41-46; zero references to their 22 ids anywhere else in the save (scanner proved
     on a positive control: 10/10 Human pawn ids are referenced elsewhere).
  2. VEF GameComponent_QuestChains <futureQuests> rows whose questDef belongs to a retired mod
     (VQE_AncientLabComplex: Ancients leaves in wave 1; VQE_Cryptoforge_Chapter1: already absent since the
     2026-09-28 Cryptoforge retirement).
  3. custom passions written by Vanilla Skills Expanded (VSE_*) and Alpha Skills (AS_*) into SkillRecord
     <passion>: vanilla scribes Passion as an enum (SkillRecord.ExposeData, default None), so without those
     mods every such value fails to parse and the pawn silently loses the passion. Measured 2026-10-10: 198
     values on 99 pawns, 6 of them player colonists. Mapped to the nearest vanilla passion (PASSION_MAP; skills
     stay vanilla by ruling C08). The AS_* hediffs are left: HediffSet drops null-def hediffs on load.
Refuses unless the counts found equal the counts expected (--walls, --quests, --passions), so a changed save cannot be
edited blind. Verifies the output by a streaming parse: the removed ids are gone, every other MinifiedThing
(RM_Graffiti_Vandal) survives, and the size delta equals the bytes removed.

    python3 wave1_save_preedit.py IN.rws OUT.rws            # plan only
    python3 wave1_save_preedit.py IN.rws OUT.rws --apply    # write OUT (refuses if OUT exists)
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

DEAD_QUESTS = (b"VQE_AncientLabComplex", b"VQE_Cryptoforge_Chapter1")
# FOUNDRY default 2026-10-10 (owner may override): strong passions -> Major, negative ones -> None, every other
# conditional Alpha Skills passion -> Minor.
PASSION_MAP = {"VSE_Critical": "Major", "VSE_Natural": "Major", "VSE_Apathy": "None", "AS_DuncePassion": "None",
               "AS_PsychicPassion_Major": "Major", "AS_BlindPassion_Sublime": "Major"}


def passion_target(v):
    return PASSION_MAP.get(v, "Minor")


def wall_spans(d):
    spans = []
    for m in re.finditer(rb'<thing Class="MinifiedThing">', d):
        s = m.start()
        e = d.find(b"</thing>", s)
        if e < 0:
            sys.exit("REFUSED: unterminated MinifiedThing at byte %d" % s)
        body = d[s:e]
        if body.count(b"<thing") != 1:
            sys.exit("REFUSED: nested <thing> inside MinifiedThing at byte %d" % s)
        if b"<def>Wall</def>" in body:
            ls = d.rfind(b"\n", 0, s) + 1          # take the whole line(s): indentation through the newline
            le = d.find(b"\n", e) + 1
            tid = re.search(rb"<id>(MinifiedThing\d+)</id>", body).group(1).decode()
            spans.append((ls, le, tid))
    return spans


def quest_spans(d):
    spans = []
    for q in DEAD_QUESTS:
        for m in re.finditer(rb"<questDef>" + q + rb"</questDef>", d):
            s = d.rfind(b"<li>", 0, m.start())
            e = d.find(b"</li>", m.end())
            if b"<tickToFire>" not in d[s:m.start()] or d.rfind(b"<futureQuests>", 0, s) < d.rfind(b"</futureQuests>", 0, s):
                sys.exit("REFUSED: %s is not inside a futureQuests <li>" % q.decode())
            spans.append((d.rfind(b"\n", 0, s) + 1, d.find(b"\n", e) + 1, q.decode()))
    return spans


def passion_spans(d):
    spans = []
    for m in re.finditer(rb"<passion>((?:VSE|AS)_[A-Za-z_]+)</passion>", d):
        v = m.group(1).decode()
        spans.append((m.start(), m.end(), v, ("<passion>%s</passion>" % passion_target(v)).encode()))
    return spans


def verify(path, removed_ids):
    minis, quests = [], []
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "thing" and el.findtext("def") == "MinifiedThing":
            minis.append(el.findtext("id"))
            el.clear()
        elif el.tag == "questDef":
            quests.append(el.text)
        elif el.tag == "passion" and el.text not in ("None", "Minor", "Major"):
            quests.append("PASSION:" + str(el.text))
    return minis, quests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--walls", type=int, default=11)
    ap.add_argument("--quests", type=int, default=2)
    ap.add_argument("--passions", type=int, default=198)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    d = open(a.inp, "rb").read()
    ws, qs, ps = wall_spans(d), quest_spans(d), passion_spans(d)
    print("input %s: %d bytes; minified walls %d (expected %d); dead futureQuests %d (expected %d); custom passions %d (expected %d)"
          % (a.inp, len(d), len(ws), a.walls, len(qs), a.quests, len(ps), a.passions))
    from collections import Counter
    for (v, t), n in sorted(Counter((v, passion_target(v)) for _, _, v, _ in ps).items()):
        print("  passion %-28s -> %-5s x%d" % (v, t, n))
    for s, e, t in ws + qs:
        print("  remove %-28s bytes %d-%d (%d)" % (t, s, e, e - s))
    if len(ws) != a.walls or len(qs) != a.quests or len(ps) != a.passions:
        sys.exit("REFUSED: counts differ from expected; re-census before editing")
    spans = sorted([(s, e, t, b"") for s, e, t in ws + qs] + ps)
    for (s1, e1, _, _), (s2, _, _, _) in zip(spans, spans[1:]):
        if s2 < e1:
            sys.exit("REFUSED: overlapping spans")
    if not a.apply:
        print("PLAN ONLY (pass --apply to write %s)" % a.out)
        return
    if os.path.exists(a.out):
        sys.exit("REFUSED: %s exists" % a.out)
    out, pos = [], 0
    for s, e, _, rep in spans:
        out.append(d[pos:s])
        out.append(rep)
        pos = e
    out.append(d[pos:])
    blob = b"".join(out)
    with open(a.out, "wb") as f:
        f.write(blob)
    removed = sum(e - s - len(rep) for s, e, _, rep in spans)
    size = os.path.getsize(a.out)
    minis, quests = verify(a.out, [t for _, _, t in ws])
    gone = [t for _, _, t in ws if t in minis]
    deadq = [q for q in quests if q.startswith("PASSION:") or q.encode() in DEAD_QUESTS]
    ok = size == len(d) - removed and not gone and not deadq and len(minis) >= 1
    print("output %s: %d bytes (delta %d, expected %d); MinifiedThing left %s; dead quests/custom passions left %d -> %s"
          % (a.out, size, len(d) - size, removed, minis, len(deadq), "OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
