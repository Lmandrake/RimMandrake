#!/usr/bin/env python3
"""Selftest for design/Jawa/worldbuilding/founders/import_founders.py.

    python3 src/RimMandrake/Utils/selftest_import_founders.py

🔴 THE REGRESSION THIS FILE EXISTS FOR

MEASURED 2026-09-21: a founders splice that remapped faction/ideo/map/position but
left `<loadID>` alone loaded cleanly, logged NOTHING, and silently dropped the
`Wimp` trait from 5 of the 6 founders. `Wimp` is the only trait they carry with a
non-null `<sourceGene>`; gene loadIDs are save-local, the destination had already
issued 0-1633, and `Gene_342/382/422/462/814` therefore resolved — successfully —
into the destination's own unrelated genes. Sekki's `Gene_2009` sat above the
issued range and kept its trait. 6 of 6 agree, negative case included.

**A loadID collision does not error. It resolves to the wrong object.** No
assertion about pawn COUNT, trait-element count or "it parses" catches it: every
one of those is green in the broken save. The only assertion that catches it is
the one below — no gene loadID is shared between a founder and anybody else in the
destination.

The detector is calibrated against both evidence saves from that run, which is why
it is trusted: `FOUNDER_ROUNDTRIP_2026-09-21.rws` (the broken one) reports 200
colliding gene loadIDs and 5 of 6 colliding `Wimp` sourceGenes; the V2 save and a
fresh splice both report 0. Those fixtures live on the owner's Windows machine and
are absent on the laptop, so the fixture tier SKIPS visibly there while the
synthetic tier — which does not need them — still runs and still catches the bug.

Second guarded behaviour: the id base must be COMPUTED, never a fixed offset. The
proving run's +1,000,000 works only for destinations that happen to sit below it,
so section 2 below builds a destination whose genes run PAST 1,000,000 — where that
constant would collide — and asserts the allocator still lands clear.
"""
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
FOUNDERS = os.path.join(REPO, "design", "Jawa", "worldbuilding", "founders")
sys.path.insert(0, FOUNDERS)
import import_founders as IF                                    # noqa: E402

sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from game_paths import SAVES                                    # noqa: E402
FOUNDER_THING_IDS = {
    "Human470521", "Human470524", "Human470527", "Human470530",
    "Human632207", "Human669116", "AA_Eyeling669122", "RSW_Dewback669123",
}


# --------------------------------------------------------------------------- #
# the detector — the same one that was calibrated against both evidence saves
# --------------------------------------------------------------------------- #

def gene_collisions(save_bytes: bytes) -> tuple[int, int, int]:
    """(colliding gene loadIDs, colliding Wimp sourceGenes, total Wimp traits).

    A gene loadID is "colliding" when it is carried BOTH by an imported founder and
    by somebody already in the destination. That is the state in which the receiving
    game resolves a founder's `<sourceGene>` to the destination's gene instead.
    """
    root = ET.fromstring(save_bytes.decode("utf-8-sig"))
    parent = {ch: p for p in root.iter() for ch in p}

    def is_gene(e):
        cur = parent.get(e)
        while cur is not None:
            if cur.tag in ("endogenes", "xenogenes"):
                return True
            cur = parent.get(cur)
        return False

    founder_genes, other_genes, wimp_refs = set(), set(), set()
    things = root.find("game/maps")[0].find("things")
    for t in things:
        mine = (t.findtext("id") or "") in FOUNDER_THING_IDS
        target = founder_genes if mine else other_genes
        for g in t.iter("loadID"):
            txt = (g.text or "").strip()
            if txt.lstrip("-").isdigit() and is_gene(g):
                target.add(int(txt))
        if not mine:
            continue
        for li in t.iter("li"):
            if li.findtext("def") == "Wimp":
                src = (li.findtext("sourceGene") or "").strip()
                if src.startswith("Gene_"):
                    wimp_refs.add(int(src.split("_", 1)[1]))
    for wp in root.iter("worldPawns"):
        for g in wp.iter("loadID"):
            txt = (g.text or "").strip()
            if txt.lstrip("-").isdigit() and is_gene(g):
                other_genes.add(int(txt))
    return (len(founder_genes & other_genes),
            len(wimp_refs & other_genes),
            len(wimp_refs))


# --------------------------------------------------------------------------- #
# a synthetic destination, so the test runs with no game and no fixtures
# --------------------------------------------------------------------------- #

def synthetic_save(gene_lo: int, gene_hi: int, eol: str = "\r\n",
                   next_gene: int | None = None) -> bytes:
    """A minimal but structurally real .rws whose own pawn already holds genes.

    `gene_lo..gene_hi` is the range the destination has ALREADY issued — the thing
    the importer has to allocate clear of.
    """
    genes = "".join(
        "<li><def>Beauty_Pretty</def><loadID>%d</loadID>"
        "<overriddenByGene IsNull=\"True\" /></li>" % i
        for i in range(gene_lo, gene_hi + 1))
    xml = """<?xml version="1.0" encoding="utf-8"?>
<savegame>
<meta><gameVersion>1.6</gameVersion></meta>
<game>
<currentMapIndex>0</currentMapIndex>
<uniqueIDsManager>
<nextThingID>22801</nextThingID><nextFactionID>18</nextFactionID>
<nextJobID>4</nextJobID><nextHediffID>%(nh)d</nextHediffID>
<nextAbilityID>136</nextAbilityID><nextGeneID>%(ng)d</nextGeneID>
</uniqueIDsManager>
<world><factionManager><allFactions>
<li><def>PlayerColony</def><loadID>17</loadID>
<ideos><primaryIdeo>Ideo_12</primaryIdeo><ideosMinor /></ideos></li>
</allFactions></factionManager></world>
<maps><li>
<uniqueID>0</uniqueID>
<mapInfo><size>(250, 1, 250)</size></mapInfo>
<things>
<li Class="Pawn"><def>Human</def><id>Human22799</id><map>0</map><pos>(120, 0, 70)</pos>
<faction>Faction_17</faction>
<genes><endogenes>%(genes)s</endogenes><xenogenes /></genes>
</li>
</things>
</li></maps>
</game>
</savegame>
""" % {"genes": genes, "ng": next_gene if next_gene is not None else gene_hi + 1,
       "nh": 527}
    return re.sub(r"\r?\n", eol, xml).encode("utf-8")


def splice_synthetic(**kw) -> tuple[bytes, dict]:
    data = synthetic_save(**kw)
    dest = IF.Destination("synthetic.rws", data=data)
    frags = [IF.Fragment(p) for p in IF.fragment_files(FOUNDERS)]
    return IF.splice(dest, frags)


# --------------------------------------------------------------------------- #
# cases
# --------------------------------------------------------------------------- #

def cases() -> list[tuple[str, bool]]:
    out = []

    # --- 1. THE REGRESSION -------------------------------------------------- #
    # Destination genes 0..1633, exactly the range that ate the trait live.
    spliced, report = splice_synthetic(gene_lo=0, gene_hi=1633)
    clashes, wimp_clashes, wimps = gene_collisions(spliced)
    out.append(("all 6 Wimp traits survive the splice as elements", wimps == 6))
    out.append(("🔴 no Wimp sourceGene resolves to a destination gene",
                wimp_clashes == 0))
    out.append(("🔴 no gene loadID is shared with the destination", clashes == 0))

    # The same fragments spliced with the remaps the README originally named —
    # everything EXCEPT the loadID reallocation — must reproduce the defect, or
    # the assertions above are green for the wrong reason.
    naive = naive_splice(gene_lo=0, gene_hi=1633)
    n_clash, n_wimp, n_total = gene_collisions(naive)
    out.append(("control: the same splice WITHOUT id reallocation still shows "
                "6 Wimp elements (the defect is invisible to a count)",
                n_total == 6))
    out.append(("control: it collides on 5 of 6 Wimp sourceGenes — the 2026-09-21 "
                "measurement, Sekki's Gene_2009 the one survivor",
                n_wimp == 5 and n_clash > 0))

    # --- 2. allocation is computed, not a constant -------------------------- #
    base_low = report["bases"]["gene"]
    _, high_report = splice_synthetic(gene_lo=0, gene_hi=1000)
    out.append(("gene base tracks the destination's issued range, not a constant",
                high_report["bases"]["gene"] != base_low))
    out.append(("gene base clears the destination's highest issued gene",
                base_low > 1633))

    # A +1,000,000 offset — the proving run's fixed constant — lands INSIDE this
    # destination. The allocator must not.
    spliced_hi, hi_report = splice_synthetic(gene_lo=1_000_000, gene_hi=1_001_500)
    hi_clash, hi_wimp, _ = gene_collisions(spliced_hi)
    out.append(("🔴 a destination whose genes run past 1,000,000 — where the "
                "proving run's fixed offset would collide — is still clean",
                hi_clash == 0 and hi_wimp == 0))
    out.append(("bases move with that destination too",
                hi_report["bases"]["gene"] > 1_001_500))

    # A counter that has run ahead of the ids actually present must still be
    # respected: allocating from the issued maximum alone would collide with the
    # ids the receiving game is about to hand out.
    _, ahead = splice_synthetic(gene_lo=0, gene_hi=50, next_gene=9000)
    out.append(("a counter ahead of the issued ids still sets the floor",
                ahead["bases"]["gene"] >= 9000))

    # --- 3. counters are raised past everything imported -------------------- #
    root = ET.fromstring(spliced.decode("utf-8-sig"))
    uid = {c.tag: int(c.text) for c in root.find("game/uniqueIDsManager")}
    genes = [int(g.text) for g in root.iter("loadID")
             if (g.text or "").strip().lstrip("-").isdigit()]
    out.append(("nextGeneID is past every gene in the spliced save",
                uid["nextGeneID"] > max(genes)))
    out.append(("nextThingID is past every imported Thing id",
                uid["nextThingID"] > 669123))

    # --- 4. the other three remaps ------------------------------------------ #
    things = root.find("game/maps")[0].find("things")
    founders = [t for t in things if (t.findtext("id") or "") in FOUNDER_THING_IDS]
    out.append(("all 8 fragments arrive", len(founders) == 8))
    out.append(("faction remapped to the destination's PlayerColony",
                {t.findtext("faction") for t in founders} == {"Faction_17"}))
    out.append(("ideo remapped to the destination's primary ideo",
                {t.findtext("ideo/ideo") for t in founders} - {None} == {"Ideo_12"}))
    out.append(("map remapped to the destination map's uniqueID",
                {t.findtext("map") for t in founders} == {"0"}))
    out.append(("positions are inside the destination map",
                all(0 < IF.parse_vec(t.findtext("pos"))[0] < 250 and
                    0 < IF.parse_vec(t.findtext("pos"))[2] < 250 for t in founders)))
    out.append(("the destination's own pawn is untouched",
                any((t.findtext("id") or "") == "Human22799" for t in things)))

    # --- 4b. thing ids: left alone unless the destination forces a rename ---- #
    # The 2026-09-21 run kept the exported Thing ids and the closed 62-reference
    # relation graph resolved, so renaming for no reason would be churn on the one
    # thing that was measured to work. Renaming when the destination already holds
    # one of them is not optional: two Things with one id is a corrupt save.
    out.append(("thing ids are untouched when nothing collides",
                not report["thing_ids_renamed"]))
    collided = synthetic_save(gene_lo=0, gene_hi=40).replace(
        b"<id>Human22799</id>", b"<id>Human470521</id>")
    dest2 = IF.Destination("synthetic.rws", data=collided)
    frags2 = [IF.Fragment(p) for p in IF.fragment_files(FOUNDERS)]
    spliced2, rep2 = IF.splice(dest2, frags2)
    ids2 = [e.text for e in ET.fromstring(spliced2.decode("utf-8-sig")).iter("id")]
    out.append(("a colliding thing id triggers a rename of all 22 declared ids",
                len(rep2["thing_ids_renamed"]) == 22))
    out.append(("🔴 the rename produces no duplicate Thing id — the new numbers "
                "clear the fragments' own, and substitution is a single pass",
                len(ids2) == len(set(ids2))))

    # --- 5. binary mode ------------------------------------------------------ #
    # A CRLF destination must come back CRLF. A lone LF means a text-mode handle
    # or a line-ending translation got into the write path.
    out.append(("a CRLF destination keeps CRLF throughout",
                spliced.count(b"\n") == spliced.count(b"\r\n")))
    lf_only, _ = splice_synthetic(gene_lo=0, gene_hi=40, eol="\n")
    out.append(("an LF destination keeps LF throughout", b"\r\n" not in lf_only))

    tmp = tempfile.mkdtemp(prefix="founders_selftest_")
    try:
        path = os.path.join(tmp, "DEST_COPY.rws")
        with open(path, "wb") as fh:
            fh.write(synthetic_save(gene_lo=0, gene_hi=40))
        stat = IF.write_save(path, spliced)
        on_disk = IF.read_binary(path)
        out.append(("bytes on disk are byte-identical to bytes written",
                    on_disk == spliced and stat["after"] == len(spliced)))
        out.append(("the destination is backed up before it is overwritten",
                    stat["backup"] and os.path.exists(stat["backup"])))

        # --- 6. keeper refusal ---------------------------------------------- #
        refusals = []
        for name in ("CANONICAL_ASHKARR_START_2026-09-12.rws",
                     "ASHKARR_FALLLINE_LABEL26_2026-09-21.rws",
                     "CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-anything"):
            keeper = os.path.join(tmp, name)
            with open(keeper, "wb") as fh:
                fh.write(b"untouchable")
            try:
                IF.write_save(keeper, spliced)
                refusals.append(False)
            except IF.ImportError_:
                refusals.append(IF.read_binary(keeper) == b"untouchable")
        out.append(("🔴 keeper saves (and their backups) are refused by name, "
                    "unwritten", all(refusals) and len(refusals) == 3))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    # --- 7. the evidence fixtures, when this machine has them ---------------- #
    v2 = os.path.join(SAVES, "FOUNDER_ROUNDTRIP_V2_2026-09-21.rws")
    v1 = os.path.join(SAVES, "FOUNDER_ROUNDTRIP_2026-09-21.rws")
    if os.path.exists(v1) and os.path.exists(v2):
        c1, w1, t1 = gene_collisions(IF.read_binary(v1))
        c2, w2, t2 = gene_collisions(IF.read_binary(v2))
        out.append(("fixture: the 2026-09-21 broken save collides on 5 of 6 Wimp "
                    "sourceGenes — the detector sees the real defect",
                    (w1, t1) == (5, 6) and c1 > 0))
        out.append(("fixture: the 2026-09-21 clean save collides on none",
                    (w2, t2) == (0, 6) and c2 == 0))
    else:
        print("note  evidence fixtures absent on this machine "
              "(%s) — fixture tier skipped, synthetic tier still ran" % SAVES)
    return out


def naive_splice(gene_lo: int, gene_hi: int) -> bytes:
    """The 2026-09-21 attempt-1 splice: every remap EXCEPT id reallocation.

    This is the control. Without it, the assertions above could be green because
    the fragments never collided in the first place rather than because the
    importer fixed it.
    """
    data = synthetic_save(gene_lo=gene_lo, gene_hi=gene_hi)
    dest = IF.Destination("synthetic.rws", data=data)
    frags = [IF.Fragment(p) for p in IF.fragment_files(FOUNDERS)]
    identity = {cls: {} for cls in IF.COUNTER_FOR_CLASS}
    for f in frags:
        for cls, ids in f.ids_by_class().items():
            if cls in identity:
                identity[cls].update({i: i for i in ids})
    blocks = []
    for i, f in enumerate(frags):
        body = IF.rewrite(f, dest, identity, (110 + 2 * i, 70), {})
        blocks.append("\r\n" + re.sub(r"\r?\n", "\r\n", body.decode("utf-8")).strip())
    payload = ("".join(blocks) + "\r\n").encode("utf-8")
    return (dest.data[:dest.things_insert_at] + payload
            + dest.data[dest.things_insert_at:])


def main() -> int:
    try:
        results = cases()
    except Exception as exc:                                  # noqa: BLE001
        print("FAIL  the selftest could not run: %r" % (exc,))
        raise
    bad = 0
    for label, ok in results:
        bad += not ok
        print("%s  %s" % ("ok  " if ok else "FAIL", label))
    print("\n%d/%d passed" % (len(results) - bad, len(results)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
