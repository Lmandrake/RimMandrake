#!/usr/bin/env python3
r"""gen_matrix.py -- the mineral matrix rebuilt on the painted worldmap's biome list (2026-10-30).

Item MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP (parent BIOME_AUDIT_TRIAGE_NINE_REPAIRS_WAITING).
Authority for the biome list: design/RimMandrake/biome_name_provenance_audit_2026-10-28.md, "The authoritative biome
list": 27 painted world biomes (26 RM_ defs + RUT_Umbra, the Auroral Umbra), plus RM_ChillCrater (aftermath, not
natural) and RM_LanternDeeps (cave layer, not a worldmap biome), both kept and MARKED as what they are.

The round-one generator (gen_matrix.py, 2026-10-28) was a scratch file and is lost; round two (gen_v2.py) read its
output. This script restores the name: it reads the round-two values, which carry every owner ruling so far
(D1 ladder, D2 steel ~10, D3 home + one minor second, D4 15 no-draw biomes, D7-D9) and rebuilds the sheet on the ruled
biome list. Column rules, each from a sibling repair item of the audit:
  * MINERAL_TWIN_COLUMNS_DELETE_RM_WINS: RUT_Desert, RUT_ExtremeDesert, RUT_AridShrubland rows go; their RM_ successor's
    values stand (no owner ruling exists on the twin numbers). RUT_Umbra stays: it is a painted biome.
  * SEA_MINERALS_MERGE_FLOOR_INTO_SEA_ROW: each RM_SeabedFloor_* row's minerals move onto its sea's row (owner
    2026-10-28: "There is only the sea floor"). Where both rows hold a value the larger one stands and the cell is
    marked draft.
  * WARSCAR_LABEL_RESTORE_THE_ARTICLE: RM_Warscar shows "the Warscar" (src still says "Warscar" until that item lands).
  * Labels are read from the BiomeDef XML in src at run time; no "(Jawa)" tag anywhere.
  * OTHER_vanilla is a sheet-only bucket, not a biome (audit class BK): dropped.
Moved or merged cells carry provenance "DRAFT ..." so the page marks them. A cell in a column that did not exist
before would follow D3/D4 and be marked draft; this rebuild adds no new biome, so there are none.

Restored into the repo 2026-11-11 (it was a scratch file in Archmagi D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-30).
Its round-two inputs are committed beside the design docs, in design/RimMandrake/mineral_matrix/round_two_2026-10-28/
(README.md there says what each file is and where it came from). On the same src it writes byte-identical CSVs.

Usage, from any clone:
    python3 src/RimMandrake/Utils/mineral_matrix/gen_matrix.py [--out DIR] [--repo DIR] [--no-page]
Writes into --out (default <repo>/Transient/mineral_matrix/): biomes.csv, draft_matrix.csv, reasons.csv,
mineral_homes.csv, inventory.csv, reach_summary.csv, column_changes.csv, stats.json; then the sheet, page/index.html,
with its pre-review record page/index.prereview.json; then runs check_matrix.py and `prereview.py check` on the sheet.
Exit 0 only if every check passes.
"""
import argparse, collections, csv, glob, json, os, re, sys
import xml.etree.ElementTree as ET

TOOL = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(TOOL, "..", "..", "..", ".."))
R2_REL = "design/RimMandrake/mineral_matrix/round_two_2026-10-28/"
RECORD_REL = "design/RimMandrake/mineral_matrix/index.prereview.json"  # the judged record; valid only while rows match
BASELINE_REL = "design/RimMandrake/mineral_matrix/build_2026-10-30.sha256"  # the 2026-10-30 build's output hashes

# The ruled list (audit table rows 1-27, then the two marked extras). kind: land | sea | aftermath | cave
BIOMES = [
    ("RM_Stillsand", "land", "RUT_ExtremeDesert"), ("RM_LongShade", "land", "RUT_Desert"),
    ("RM_LeaningScrub", "land", "RUT_AridShrubland"), ("RM_Wastes", "land", "RUT_Wastes"),
    ("RM_Abyss", "land", "RUT_Abyss"), ("RM_SleepingIce", "land", "RUT_SleepingIce"),
    ("RM_BlueDesert", "land", "RUT_BlueDesert"), ("RM_TheRot", "land", "RUT_TheRot"),
    ("RM_GelatinousSlime", "land", "RUT_Slime"), ("RM_Contagion", "land", "RUT_Contagion"),
    ("RM_FloodedCanyon", "land", "RUT_CrackedLands"), ("RM_WeepingStones", "land", "RUT_WeepingStones"),
    ("RM_Greentide", "land", "RUT_Greentide"), ("RM_Webwork", "land", "RUT_Webwork"),
    ("RM_Warscar", "land", "RUT_Scarlands"), ("RM_RustCathedral", "land", "RUT_RustCathedral"),
    ("RM_Miasma", "land", "RUT_Miasma"), ("RM_FeverWood", "land", "RUT_FeverWood"),
    ("RM_TheSump", "land", "RUT_Sump"), ("RM_Pyrelands", "land", ""), ("RM_TheForge", "land", "RUT_TheForge"),
    ("RM_Cauldron", "land", "RUT_Cauldron"), ("RUT_Umbra", "land", ""),
    ("RM_TheScald", "sea", "RUT_TheScald"), ("RM_TheChill", "sea", "RUT_PropaneLake"),
    ("RM_GreySea", "sea", "RUT_GreySea"), ("RM_TwilightSea", "sea", "RUT_TwilightSea"),
    ("RM_ChillCrater", "aftermath", ""), ("RM_LanternDeeps", "cave", ""),
]
assert len(BIOMES) == 29 and sum(1 for b in BIOMES if b[1] in ("land", "sea")) == 27
LABEL_OVERRIDE = {"RM_Warscar": ("the Warscar", "src label is 'Warscar'; sheet shows 'the Warscar' per "
                                 "WARSCAR_LABEL_RESTORE_THE_ARTICLE (2026-09-26 every-label-is-the-Xxx ruling)")}
FLOORS = {"RM_SeabedFloor_TheScald": "RM_TheScald", "RM_SeabedFloor_GreySea": "RM_GreySea",
          "RM_SeabedFloor_TwilightSea": "RM_TwilightSea", "RM_SeabedFloor_TheChill": "RM_TheChill"}
TWINS = {"RUT_Desert": "RM_LongShade", "RUT_ExtremeDesert": "RM_Stillsand", "RUT_AridShrubland": "RM_LeaningScrub"}
BUCKETS = {"OTHER_vanilla"}
D4_OLD = ["RM_Abyss", "RM_FeverWood", "RM_GelatinousSlime", "RM_Greentide", "RM_LeaningScrub", "RM_LongShade",
          "RM_Miasma", "RM_Pyrelands", "RM_TheRot", "RM_Webwork", "RM_TheScald", "RM_TwilightSea",
          "RM_SeabedFloor_TwilightSea", "RM_SeabedFloor_TheChill", "RUT_AridShrubland"]
KIND_NOTE = {"aftermath": "not painted: aftermath biome (generatesNaturally=false), made when the Chill burns",
             "cave": "not painted: cave layer injected under cold maps, not a worldmap biome"}
TEXT_FIX = [("RM_SeabedFloor_TheScald", "RM_TheScald"), ("RM_SeabedFloor_GreySea", "RM_GreySea"),
            ("SeabedFloor_TheScald", "TheScald"), ("Fuel Snows gas pockets", "Auroral Umbra gas pockets")]


def fix_text(s):
    for a, b in TEXT_FIX:
        s = s.replace(a, b)
    return s


def src_labels(repo):
    want = {b for b, _, _ in BIOMES}
    out = {}
    for f in glob.glob(repo + "/src/**/*.xml", recursive=True):
        if "BiomeDef" not in open(f, errors="replace").read(4000) and "/Biome" not in f:
            continue
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root.iter("BiomeDef"):
            n = d.findtext("defName")
            if n in want:
                assert n not in out, ("two BiomeDefs named", n, out[n][1], f)
                out[n] = (d.findtext("label"), os.path.relpath(f, repo), d.findtext("generatesNaturally"))
    missing = want - set(out)
    assert not missing, ("no BiomeDef in src for", missing)
    return out


def src_def_folders(repo):
    out = {}
    for f in glob.glob(repo + "/src/RimMandrake/**/Defs/**/*.xml", recursive=True):
        for n in re.findall(r"<defName>(RM_\w+)</defName>", open(f, errors="replace").read()):
            out.setdefault(n, os.path.relpath(f, repo).split("/Defs/")[0])
    return out


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO, help="clone whose src/ BiomeDefs give the labels (default: this one)")
    ap.add_argument("--out", default=None, help="output folder (default <repo>/Transient/mineral_matrix)")
    ap.add_argument("--no-page", action="store_true", help="CSVs and stats only; no sheet, no checks")
    a = ap.parse_args()
    a.repo = os.path.abspath(a.repo)
    R2 = os.path.join(a.repo, R2_REL)
    HERE = os.path.abspath(a.out or os.path.join(a.repo, "Transient", "mineral_matrix")) + "/"
    os.makedirs(HERE, exist_ok=True)
    labels = src_labels(a.repo)

    rows = list(csv.DictReader(open(R2 + "draft_matrix_v2.csv")))
    cols = list(rows[0].keys())
    R = {r["biome"]: dict(r) for r in rows}
    VAL = cols[cols.index("steel"):cols.index("mountain_reason")]
    reasons = list(csv.DictReader(open(R2 + "reasons_v2.csv")))
    RS = {(x["biome"], x["column"]): dict(x) for x in reasons}
    homes = list(csv.DictReader(open(R2 + "mineral_homes_v2.csv")))
    seen = {b for b, _, _ in BIOMES} | set(FLOORS) | set(TWINS) | BUCKETS
    old_biomes = [r["biome"] for r in rows if not r["biome"].startswith("SRC_")]
    assert set(old_biomes) == seen, ("round-two rows not all classified", set(old_biomes) ^ seen)

    changes = []  # one line per dropped/merged column value
    draft_cells = {}  # (biome, column) -> why

    # seas: a sea IS its floor
    for fl, sea in FLOORS.items():
        for c in VAL:
            fv, sv = fnum(R[fl][c]), fnum(R[sea][c])
            if not fv:
                continue
            fr = RS.get((fl, c))
            if not sv:
                R[sea][c] = R[fl][c]
                nr = dict(fr, biome=sea)
                nr["provenance"] = "DRAFT moved from %s (SEA_MINERALS_MERGE_FLOOR_INTO_SEA_ROW); was: %s" % (fl, fr["provenance"])
                RS[(sea, c)] = nr
                draft_cells[(sea, c)] = "moved from " + fl
                changes.append(dict(column=fl, action="merged into " + sea, cell=c, old=R[fl][c], new=R[sea][c],
                                    note="moved unchanged"))
            else:
                keep = max(fv, sv)
                R[sea][c] = "%g" % keep
                sr = RS[(sea, c)]
                sr["reason"] = sr["reason"] + "; on its floor: " + fr["reason"]
                sr["provenance"] = "DRAFT merged: sea %g + floor %g -> the larger stands (%s; floor %s)" % (
                    sv, fv, sr["provenance"], fr["provenance"])
                draft_cells[(sea, c)] = "sea %g and floor %g merged; larger kept" % (sv, fv)
                changes.append(dict(column=fl, action="merged into " + sea, cell=c, old="sea %s / floor %s" % (sv, fv),
                                    new=R[sea][c], note="both rows held a value; the larger stands, marked draft"))
        for k in ("signature_minerals_unique_here", "non_mineral_pull"):
            if R[fl][k].strip():
                R[sea][k] = " ".join(x for x in (R[sea][k].strip(), R[fl][k].strip()) if x)
        if not any(fnum(R[fl][c]) for c in VAL):
            changes.append(dict(column=fl, action="merged into " + sea, cell="(all)", old="empty", new="", note="floor row held nothing"))
    # twins and bucket: dropped, the RM_ row stands
    for tw, succ in list(TWINS.items()) + [(b, "") for b in BUCKETS]:
        nz = [(c, R[tw][c]) for c in VAL if fnum(R[tw][c])]
        for c, v in nz:
            sv = R[succ][c] if succ else ""
            changes.append(dict(column=tw, action=("dropped; %s stands" % succ) if succ else "dropped (not a biome)",
                                cell=c, old=v, new="", note=("%s holds %s" % (succ, sv or "0")) if succ else "sheet-only bucket"))
        if R[tw]["non_mineral_pull"].strip():
            changes.append(dict(column=tw, action="dropped", cell="non_mineral_pull", old=R[tw]["non_mineral_pull"],
                                new="", note="%s pull stays: %r" % (succ, R[succ]["non_mineral_pull"]) if succ else ""))

    # homes: retarget floor/twin references
    for h in homes:
        for k in ("home", "second", "cells", "why_home", "why_second_or_none"):
            h[k] = fix_text(h[k])
        if h["second"] == "RUT_ExtremeDesert":
            assert h["mineral"] == "sand"
            h["second"] = "NONE"
            h["why_second_or_none"] = ("NONE (DRAFT): the round-two second, RUT_ExtremeDesert, is the Stillsand's own frozen "
                                       "twin, so it was never a second biome (audit 2026-10-28). Both owner sand rulings "
                                       "(10-09 transparisteel from the extreme desert's fine sand) sit on the Stillsand; "
                                       "no other painted biome is dune sea. His to set if he wants one.")
            changes.append(dict(column="RUT_ExtremeDesert", action="dropped; RM_Stillsand stands", cell="mineral_homes: sand second",
                                old="RUT_ExtremeDesert", new="NONE", note="sand is now home-only; marked draft"))

    D4 = [b for b in D4_OLD if b in R and b not in FLOORS and b not in TWINS
          and not any(fnum(R[b][c]) for c in VAL if c != "steel")]
    d4_left = [b for b in D4_OLD if b not in D4]

    # unique-here: after D3, minerals with NO second biome are unique to their home
    for b, _, _ in BIOMES:
        R[b]["signature_minerals_unique_here"] = " ".join(sorted(h["mineral"] for h in homes
                                                                 if h["home"] == b and h["second"] == "NONE"))

    # biome registry
    breg = []
    for b, kind, twin in BIOMES:
        lab, path, gen = labels[b]
        shown, why = LABEL_OVERRIDE.get(b, (lab, ""))
        breg.append(dict(biome=b, label=shown, src_label=lab, label_note=why, kind=kind,
                         painted="yes" if kind in ("land", "sea") else "no", mark=KIND_NOTE.get(kind, ""),
                         frozen_twin=twin, src_def=path, generatesNaturally=gen or "",
                         d4_empty="yes" if b in D4 else ""))
        assert "(Jawa)" not in shown and "Fuel Snows" not in shown
    with open(HERE + "biomes.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(breg[0])); w.writeheader(); w.writerows(breg)

    out_rows = []
    for g in breg:
        r = R[g["biome"]]
        r["label"] = g["label"]
        out_rows.append(r)
    out_rows += [R[r["biome"]] for r in rows if r["biome"].startswith("SRC_")]
    with open(HERE + "draft_matrix.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(out_rows)

    keep = {g["biome"] for g in breg} | {r["biome"] for r in rows if r["biome"].startswith("SRC_")}
    rout = []
    for r in out_rows:
        for c in VAL:
            if not fnum(r[c]):
                continue
            x = RS.get((r["biome"], c))
            assert x, ("nonzero cell without a reason", r["biome"], c)
            x = {k: (v if k == "provenance" else fix_text(v)) for k, v in x.items()}
            x["value"] = r[c]
            x["draft"] = draft_cells.get((r["biome"], c), "")
            rout.append(x)
    dropped_reasons = [k for k in RS if k[0] not in keep]
    with open(HERE + "reasons.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rout[0])); w.writeheader(); w.writerows(rout)

    # D3 check on the new rows: each mineral sits in its home plus at most its second
    brow = [R[g["biome"]] for g in breg]
    for h in homes:
        m = h["mineral"]
        mc = [c for c in (m, "DEEP_" + m, "RIVER_" + m) if c in cols]
        where = collections.OrderedDict()
        for r in brow:
            for c in mc:
                if fnum(r[c]):
                    where.setdefault(r["biome"], []).append("%s=%s" % (c, r[c]))
        sec = h["second"].split(" ")[0]
        assert h["home"] in where, (m, "home has no cell", h["home"], where)
        assert set(where) <= {h["home"], sec}, (m, where, h["home"], sec)
        assert len(where) == (1 if h["second"] == "NONE" else 2), (m, where)
        h["n_biomes"] = str(len(where))
        h["cells"] = "; ".join("%s:%s" % (b, ",".join(v)) for b, v in where.items())
    with open(HERE + "mineral_homes.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(homes[0])); w.writeheader(); w.writerows(homes)

    # inventory: mineral rows carried (floor ids retargeted), biome rows rebuilt from the registry
    inv = list(csv.DictReader(open(R2 + "inventory.csv")))
    icol = list(inv[0])
    ib = {r["id"]: r for r in inv if r["kind"] == "biome"}
    newinv = [{k: fix_text(v) for k, v in r.items()} for r in inv if r["kind"] != "biome"]
    # round two stamped every RimMandrake row "RimMandrake: Baroque Biomes"; no such mod exists. Read the real folder.
    dmod = src_def_folders(a.repo)
    for r in newinv:
        if "Baroque Biomes" in r["mod"]:
            names = re.findall(r"\b(RM_\w+)", r["defNames"])
            folders = sorted({dmod[n] for n in names if n in dmod})
            assert folders, ("no src def for", r["id"], names)
            r["mod"] = " + ".join(folders)
    for g in breg:
        r = dict(ib[g["biome"]])
        r["label"] = g["label"]
        r["mod"] = g["src_def"].split("/Defs/")[0]
        r["tier"] = {"land": "painted land", "sea": "painted sea (row includes its floor)", "aftermath": "aftermath (not painted)",
                     "cave": "cave layer (not painted)"}[g["kind"]]
        r["notes"] = fix_text(r["notes"])
        newinv.append(r)
    with open(HERE + "inventory.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=icol); w.writeheader(); w.writerows(newinv)

    reach = list(csv.DictReader(open(R2 + "reach_summary.csv")))
    for r in reach:
        for k in r:
            r[k] = fix_text(r[k])
        if r["material"] == "sand":
            assert "second biome: RUT_ExtremeDesert" in r["routes_beyond_home"], r
            r["routes_beyond_home"] = r["routes_beyond_home"].replace(
                "second biome: RUT_ExtremeDesert", "no second biome (the old one was the Stillsand's own twin)")
            r["biomes"] = "1"
    with open(HERE + "reach_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(reach[0])); w.writeheader(); w.writerows(reach)

    with open(HERE + "column_changes.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["column", "action", "cell", "old", "new", "note"]); w.writeheader(); w.writerows(changes)

    planet = cols[cols.index("steel"):cols.index("DEEP_gold")]
    nonsteel = [c for c in planet if c != "steel"]
    nz = sum(1 for r in brow for c in nonsteel if fnum(r[c]))
    stats = dict(biomes=len(breg), painted=sum(1 for g in breg if g["painted"] == "yes"),
                 marked=[g["biome"] for g in breg if g["painted"] == "no"],
                 planet_nonsteel_nonzero=nz, planet_nonsteel_cells=len(brow) * len(nonsteel),
                 sparsity_pct=round(100 * nz / (len(brow) * len(nonsteel)), 1),
                 nonzero_incl_deep_river=sum(1 for r in brow for c in VAL if not c.startswith("OFF_") and fnum(r[c])),
                 minerals=len(homes), with_second=sum(1 for h in homes if h["second"] != "NONE"),
                 none=[h["mineral"] for h in homes if h["second"] == "NONE"], reasons_rows=len(rout),
                 d4_empty=D4, d4_left=d4_left, draft_cells=len(draft_cells), new_column_cells=0,
                 dropped_columns=sorted(TWINS) + sorted(BUCKETS), merged_columns=FLOORS,
                 dropped_reason_rows=len(dropped_reasons), column_changes=len(changes))
    json.dump(stats, open(HERE + "stats.json", "w"), indent=1)
    print(json.dumps(stats))
    compare_baseline(a.repo, HERE)
    if a.no_page:
        return 0
    return finish(a.repo, HERE)


def compare_baseline(repo, out):
    """Say which outputs differ from the 2026-10-30 build. A difference is not a failure (a src label may have been
    fixed since), but it must be explained: column_changes.csv and biomes.csv say what moved."""
    import hashlib
    same, diff = [], []
    for line in open(os.path.join(repo, BASELINE_REL)):
        h, name = line.split()
        (same if hashlib.sha256(open(out + name, "rb").read()).hexdigest() == h else diff).append(name)
    print("vs the 2026-10-30 build: %d identical%s" % (len(same), "; DIFFERENT: " + " ".join(diff) if diff else " (all)"))
    return diff


def finish(repo, out):
    """Build the sheet from the CSVs just written, put the judged record beside it, and run both checks."""
    import shutil, subprocess
    py = sys.executable
    for step in (["page/build_data.py", out], ["page/build_page.py", out]):
        subprocess.run([py, os.path.join(TOOL, step[0]), step[1]], check=True)
    rec = os.path.join(repo, RECORD_REL)
    if os.path.exists(rec):
        shutil.copyfile(rec, os.path.join(out, "page", "index.prereview.json"))
    rc = 0
    for cmd in ([py, os.path.join(TOOL, "check_matrix.py"), out, "--repo", repo],
                [py, os.path.join(repo, "src/RimMandrake/Utils/art/prereview.py"), "check", os.path.join(out, "page", "index.html")]):
        r = subprocess.run(cmd)
        rc = rc or r.returncode
    print("ALL CHECKS PASS" if rc == 0 else "CHECKS FAILED (see above)", "-", out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
