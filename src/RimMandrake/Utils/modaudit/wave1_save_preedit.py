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
  4. the five Precept_Relic <thingDef>s on retired VWE guns (VWE_Gun_ChargeLMG_Unique x3, VWE_Gun_MarksmanRifle x2)
     -> the owner-approved KotOR uniques (RELIC_MAP; card 2026-10-14). Otherwise Precept_ThingDef.ExposeData
     re-rolls each to a random relic. Measured 2026-10-14: no placed relic Thing (generatedRelic null), zero
     references to the five Precept_<ID> load IDs, so only the thingDef changes. The VWE names left in
     CaravanAdventures filters and VTE price history are not relics and drop as logged noise. Idempotent: a precept
     already on its replacement counts as repaired, so --relics is pending + already done.
Writes OUT.input.bak (a byte copy of the input) before OUT, and prints the relic census before and after.
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


# Fourth repair. Owner approved by card 2026-10-14 ("Approve all five"), design/RimMandrake/relic_replacements_proposal.md:
# (precept ID in the canonical save, precept name, retired VWE thingDef, KotOR unique in src/RimStarWars/Armoury,
# mandrake.rsw.armoury, relicChance 3, not made from stuff). Keyed on ID AND name AND old def: "Rifle of Self" is
# also the name of precept 2590 (AM_M700A), which this repair must not touch.
RELIC_MAP = (
    (2402, "Hexlink", "VWE_Gun_ChargeLMG_Unique", "guy762_disrifle_baragwin"),        # Astropolitan
    (2591, "Loccorpus", "VWE_Gun_ChargeLMG_Unique", "guy762_brifle_jurgan"),          # the Contract
    (3605, "Animal Blaster", "VWE_Gun_ChargeLMG_Unique", "guy762_bowcaster_zaalbar"),  # the Green Oath
    (2701, "Strong Rifle", "VWE_Gun_MarksmanRifle", "guy762_carbine_hogra"),          # the Ascendant Genome
    (2810, "Rifle of Self", "VWE_Gun_MarksmanRifle", "guy762_hvypistol_nadd"),        # the Balance
)


def relic_spans(d):
    """(pending, done): pending = byte spans of <thingDef>OLD</thingDef> inside a RELIC_MAP precept; done = labels of
    precepts already carrying the replacement (so a re-run over an edited save changes nothing)."""
    pending, done = [], []
    for m in re.finditer(rb'<li Class="Precept_Relic">', d):
        e = d.find(b"</li>", m.end())
        body = d[m.start():e]
        pid = re.search(rb"<ID>(\d+)</ID>", body)
        name = re.search(rb"<name>([^<]*)</name>", body)
        td = re.search(rb"<thingDef>([^<]*)</thingDef>", body)
        if not (pid and name and td):
            continue
        for rid, rname, old, new in RELIC_MAP:
            if int(pid.group(1)) != rid or name.group(1).decode() != rname:
                continue
            label = "%s:%s->%s" % (rname, old, new)
            if td.group(1).decode() == new:
                done.append(label)
            elif td.group(1).decode() == old:
                pending.append((m.start() + td.start(), m.start() + td.end(), label,
                                ("<thingDef>%s</thingDef>" % new).encode()))
    return pending, done


def relic_census(path):
    """Streaming parse: (ID, name, thingDef) of every Precept_Relic."""
    rows = []
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "li" and el.get("Class") == "Precept_Relic":
            rows.append((el.findtext("ID"), el.findtext("name"), el.findtext("thingDef")))
    return rows


def relic_summary(rows):
    old = {o for _, _, o, _ in RELIC_MAP}
    new = {n for _, _, _, n in RELIC_MAP}
    return "Precept_Relic %d; on retired VWE defs %d; on the approved KotOR uniques %d" % (
        len(rows), sum(1 for r in rows if r[2] in old), sum(1 for r in rows if r[2] in new))


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
    ap.add_argument("--relics", type=int, default=len(RELIC_MAP),
                    help="RELIC_MAP precepts expected, pending + already repaired")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    d = open(a.inp, "rb").read()
    ws, qs, ps = wall_spans(d), quest_spans(d), passion_spans(d)
    rs, rdone = relic_spans(d)
    before = relic_census(a.inp)
    print("relics before: " + relic_summary(before))
    print("relic precepts: %d to repair, already %d repaired (expected %d in all)" % (len(rs), len(rdone), a.relics))
    for _, _, t, _ in rs:
        print("  relic %s" % t)
    print("input %s: %d bytes; minified walls %d (expected %d); dead futureQuests %d (expected %d); custom passions %d (expected %d)"
          % (a.inp, len(d), len(ws), a.walls, len(qs), a.quests, len(ps), a.passions))
    from collections import Counter
    for (v, t), n in sorted(Counter((v, passion_target(v)) for _, _, v, _ in ps).items()):
        print("  passion %-28s -> %-5s x%d" % (v, t, n))
    for s, e, t in ws + qs:
        print("  remove %-28s bytes %d-%d (%d)" % (t, s, e, e - s))
    if len(ws) != a.walls or len(qs) != a.quests or len(ps) != a.passions or len(rs) + len(rdone) != a.relics:
        sys.exit("REFUSED: counts differ from expected; re-census before editing")
    spans = sorted([(s, e, t, b"") for s, e, t in ws + qs] + ps + rs)
    for (s1, e1, _, _), (s2, _, _, _) in zip(spans, spans[1:]):
        if s2 < e1:
            sys.exit("REFUSED: overlapping spans")
    if not a.apply:
        print("PLAN ONLY (pass --apply to write %s)" % a.out)
        return
    if os.path.exists(a.out):
        sys.exit("REFUSED: %s exists" % a.out)
    bak = a.out + ".input.bak"                 # backup first: a byte copy of the input beside the output
    if os.path.exists(bak):
        sys.exit("REFUSED: %s exists" % bak)
    with open(bak, "wb") as f:
        f.write(d)
    print("backup %s (%d bytes)" % (bak, len(d)))
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
    after = relic_census(a.out)
    want = {(str(i), n, new) for i, n, _, new in RELIC_MAP}
    relics_ok = (len(after) == len(before) and want <= set(after)
                 and [r for r in before if r[0] not in {w[0] for w in want}]
                 == [r for r in after if r[0] not in {w[0] for w in want}])
    print("relics after:  " + relic_summary(after) + (" -> OK" if relics_ok else " -> FAILED"))
    ok = (size == len(d) - removed and not gone and not deadq and len(minis) >= 1 and relics_ok
          and open(a.inp, "rb").read() == d)
    print("output %s: %d bytes (delta %d, expected %d); MinifiedThing left %s; dead quests/custom passions left %d -> %s"
          % (a.out, size, len(d) - size, removed, minis, len(deadq), "OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
