#!/usr/bin/env python3
"""check_matrix.py -- check a gen_matrix.py output folder against its authorities, independently of the generator.

    python3 src/RimMandrake/Utils/mineral_matrix/check_matrix.py <out> [--repo DIR]

The generator carries its own biome list; this check does not trust it. It reads:
  * the row set from the audit's table ("The authoritative biome list" in
    design/RimMandrake/biome_name_provenance_audit_2026-10-28.md): numbered rows are the painted biomes, the "-" rows with
    an RM_ defName are the kept extras;
  * every row's label and src from the BiomeDef file the row names, parsed fresh;
  * every output file (CSV, JSON, HTML) for a "(Jawa)" tag, after proving on a planted copy that the scan sees one.
Writes <out>/check.json and prints one line per check. Exit 0 only if all pass.
"""
import argparse, csv, json, os, re, sys, tempfile
import xml.etree.ElementTree as ET

AUDIT = "design/RimMandrake/biome_name_provenance_audit_2026-10-28.md"
EXTRA_KIND = {"RM_ChillCrater": "aftermath", "RM_LanternDeeps": "cave"}
JAWA_TAG = re.compile(r"\(\s*jawa\s*\)", re.I)
SCAN_EXT = (".csv", ".json", ".html", ".txt", ".md")


def audit_rows(repo):
    """(painted, extras) defNames from the audit table, in table order."""
    text = open(os.path.join(repo, AUDIT), encoding="utf-8").read()
    sec = text.split("## The authoritative biome list", 1)[1].split("\n## ", 1)[0]
    painted, extras = [], []
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not line.lstrip().startswith("|"):
            continue
        m = re.search(r"\b((?:RM|RUT)_\w+)", cells[1])
        if cells[0].isdigit() and m:
            painted.append(m.group(1))
        elif cells[0] == "-" and m and m.group(1).startswith("RM_"):
            extras.append(m.group(1))
    return painted, extras


def biome_def(path, name):
    root = ET.parse(path).getroot()
    for d in root.iter("BiomeDef"):
        if d.findtext("defName") == name:
            return d
    return None


def jawa_hits(folder):
    hits = []
    for dp, _, fs in os.walk(folder):
        for f in fs:
            if f.endswith(SCAN_EXT) and f != "check.json":  # this report names the tag in its own check lines
                p = os.path.join(dp, f)
                n = len(JAWA_TAG.findall(open(p, encoding="utf-8", errors="replace").read()))
                if n:
                    hits.append((os.path.relpath(p, folder), n))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
    a = ap.parse_args()
    out, repo = os.path.abspath(a.out), os.path.abspath(a.repo)
    res = []

    def ok(name, cond, detail=""):
        res.append(dict(check=name, ok=bool(cond), detail=detail))
        print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  <- " + json.dumps(detail)[:600]))

    painted, extras = audit_rows(repo)
    ok("audit table parses to 27 painted + 2 extras", len(painted) == 27 and len(set(painted)) == 27
       and sorted(extras) == sorted(EXTRA_KIND), dict(painted=len(painted), extras=extras))
    breg = list(csv.DictReader(open(os.path.join(out, "biomes.csv"), encoding="utf-8")))
    ids = [g["biome"] for g in breg]
    want = set(painted) | set(extras)
    ok("biomes.csv rows = audit list, each once", len(ids) == len(set(ids)) and set(ids) == want,
       dict(missing=sorted(want - set(ids)), extra=sorted(set(ids) - want), dupes=len(ids) - len(set(ids))))
    mrows = [r["biome"] for r in csv.DictReader(open(os.path.join(out, "draft_matrix.csv"), encoding="utf-8"))]
    mb = [b for b in mrows if not b.startswith("SRC_")]
    ok("draft_matrix.csv biome rows = audit list, each once (SRC_ rows are the 4 other-source rows)",
       len(mb) == len(set(mb)) and set(mb) == want and len(mrows) - len(mb) == 4,
       dict(missing=sorted(want - set(mb)), extra=sorted(set(mb) - want), src_rows=[b for b in mrows if b.startswith("SRC_")]))
    ok("painted=yes on exactly the 27 painted", {g["biome"] for g in breg if g["painted"] == "yes"} == set(painted),
       sorted({g["biome"] for g in breg if g["painted"] == "yes"} ^ set(painted)))
    marked = {g["biome"]: (g["kind"], g["painted"], g["mark"]) for g in breg if g["mark"].strip()}
    ok("the two extras are marked as what they are, nothing else is marked",
       set(marked) == set(EXTRA_KIND) and all(marked[b][0] == k and marked[b][1] == "no" for b, k in EXTRA_KIND.items()),
       marked)

    srcres, bad = {}, []
    for g in breg:
        p = os.path.join(repo, g["src_def"])
        d = biome_def(p, g["biome"]) if g["src_def"] and os.path.isfile(p) else None
        if d is None:
            bad.append((g["biome"], g["src_def"], "no such BiomeDef in that file"))
            continue
        lab, gen = d.findtext("label") or "", d.findtext("generatesNaturally") or ""
        srcres[g["biome"]] = dict(src_def=g["src_def"], label_in_def=lab, generatesNaturally=gen, sheet_label=g["label"])
        if g["src_label"] != lab:
            bad.append((g["biome"], "src_label %r != def label %r" % (g["src_label"], lab)))
        if g["label"] != lab and not g["label_note"].strip():
            bad.append((g["biome"], "sheet label %r differs from def label %r with no note" % (g["label"], lab)))
    ok("every row's src_def is a real file holding that BiomeDef, and its label matches", not bad, bad)
    overrides = {g["biome"]: (g["src_label"], g["label"], g["label_note"]) for g in breg if g["label"] != g["src_label"]}
    ok("label overrides are only the noted Warscar article", set(overrides) <= {"RM_Warscar"}, overrides)
    ok("ChillCrater def says generatesNaturally=false", srcres.get("RM_ChillCrater", {}).get("generatesNaturally") == "false",
       srcres.get("RM_ChillCrater"))

    # (Jawa): prove the scan sees a planted tag, then measure the real outputs
    with tempfile.TemporaryDirectory() as t:
        src = os.path.join(out, "biomes.csv")
        txt = open(src, encoding="utf-8").read()
        open(os.path.join(t, "biomes.csv"), "w", encoding="utf-8").write(txt.replace(",the Stillsand,", ",the Stillsand (Jawa),", 1))
        probe = jawa_hits(t)
    ok("sanity probe: the scan finds one planted '(Jawa)'", probe == [("biomes.csv", 1)], probe)
    files = sorted(os.path.relpath(os.path.join(dp, f), out) for dp, _, fs in os.walk(out) for f in fs if f.endswith(SCAN_EXT) and f != "check.json")
    hits = jawa_hits(out)
    ok("no '(Jawa)' tag in any of %d output files" % len(files), not hits, hits)

    json.dump(dict(audit_painted=painted, audit_extras=extras, rows=ids, src=srcres, scanned_files=files,
                   jawa_probe=probe, jawa_hits=hits, checks=res), open(os.path.join(out, "check.json"), "w"), indent=1)
    fails = [r for r in res if not r["ok"]]
    print("check_matrix: %d/%d pass -> %s" % (len(res) - len(fails), len(res), os.path.join(out, "check.json")))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
