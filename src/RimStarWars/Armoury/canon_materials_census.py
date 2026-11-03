#!/usr/bin/env python3
"""canon_materials_census.py -- CANON_MATERIALS_BUILD_1 L9: who consumes the four assembly materials, and how.

  python3 canon_materials_census.py [--csv OUT.csv]

Reads the newest DefDump capture (the live mod set, every def after patches of the capture's day). For every player-made
consumer (a buildable building, or a RecipeDef / recipeMaker product) of RSW_Durasteel, Plasteel, RSW_Duranium or RSW_Doonium
it records HOW the material enters:
  fixed  a costList entry, or a recipe ingredient whose filter admits exactly that one def  -> enforces the material
  broad  a recipe ingredient whose filter admits it among others                            -> preference
  stuff  the def takes stuff and the material's stuffProps.categories meet its stuffCategories -> preference
and classifies each consumer into the six key jobs of design section 4 by a stated keyword rule (KEY_JOBS below). A job row is
"enforced" when some consumer in it fixes the job's right material.

Sanity probes (printed beside the result; a census that cannot find these is broken, not clean):
  BionicArm fixes Plasteel (Core costList 15) and is a prosthetics/implants consumer; Door takes Plasteel as stuff and is
  NOT a blast door; Make_BionicArm's ingredient admits only Plasteel (fixed).
The rule it checks (decision taken by question card 2026-10-11; owner typed: "The uses that were hard requirements remain.
But beyond those they are usually interchangeable. Only where unusual attributes beyond the standard mechanical parameters
can make a hard requirement."):
  * a use that was ALREADY hard stays hard: the fixed right-material consumers of the ruling-time capture are frozen in
    canon_materials_l9_baseline.json; one of them that still exists but no longer fixes its material is a defect (loosened);
  * every other key-job use is a preference: a NEW fixed right-material consumer is a defect unless ATTRIBUTE_HARD names it
    with the unusual attribute (beyond strength, weight, speed, cost) that only that material has.
  * a new fixed consumer that is a DONOR's own (one non-mandrake packageId, named by no src .xml/.cs, AND the donor's own
    XML under its manifest rootDir fixes that material) is reported as donor-native,
    not failed: a donor update shipping its own plasteel prosthetic (Outer Rim Core's cybernetics, workshop 2026-10-29) is the
    same kind of use the baseline froze, not a hard rule of ours. Ours (a mandrake def, or a donor def our patch names) fails.
  python3 canon_materials_census.py --freeze-baseline   rewrites the baseline from the newest capture (only on a new ruling)
"""
import csv, glob, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RimMandrake", "Utils"))
from game_paths import LOCALLOW  # noqa: E402
CAPTURES = os.path.join(LOCALLOW, "DefDump", "captures")
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "canon_materials_l9_baseline.json")
# consumer defName -> (material, the unusual non-mechanical attribute that makes it a hard requirement). Empty: no key job
# of section 4 needs more than standard mechanical parameters (single-material jobs such as stygium cloaking are not key jobs).
ATTRIBUTE_HARD = {}
NAMES = set()  # every ThingDef/RecipeDef defName of the censused capture
POP = {}   # job -> {defName: what it costs}, every buildable/crafted def in the job whatever it is made of
MATS = ["RSW_Durasteel", "Plasteel", "RSW_Duranium", "RSW_Doonium"]
# job -> (right material, rule over "defName label" lowercased, extra predicate name)
KEY_JOBS = {
    "hull_plating":         ("RSW_Durasteel", r"hull|substructure|plating"),
    "blast_vault_doors":    ("RSW_Durasteel", r"(blast|vault)"),
    "droid_shells":         ("Plasteel",      r"^rsw_dw_.*(chassis|frame|shell|casing|plating)"),
    "prosthetics_implants": ("Plasteel",      None),   # isTechHediff, or a BodyParts* thingCategory
    "large_frames":         ("RSW_Duranium",  r"frame|gravengine|grav engine|factory"),
    "reactor_cores":        ("RSW_Doonium",   r"reactor|gravcore|core"),
}


def latest():
    c = sorted(glob.glob(os.path.join(CAPTURES, "*", "defs")))
    return c[-1] if c else None


def classify(t):
    """t: dict with defName,label,thingClass,isTechHediff,thingCategories,isDoor. Returns the key jobs it belongs to."""
    s = " ".join([t.get("defName") or "", t.get("label") or ""]).lower()   # thingClass reads "Bed"/"Frame" noise; doors use isDoor
    jobs = []
    for job, (_, rx) in KEY_JOBS.items():
        if job == "prosthetics_implants":
            if t.get("isTechHediff") or any(c.startswith("BodyParts") for c in t.get("thingCategories") or []):
                jobs.append(job)
            continue
        if job == "blast_vault_doors":
            if t.get("isDoor") and re.search(rx, s):
                jobs.append(job)
            continue
        if job == "droid_shells":
            if re.search(rx, (t.get("defName") or "").lower()):
                jobs.append(job)
            continue
        if re.search(rx, s):
            jobs.append(job)
    return jobs


def census(defs_dir):
    T = json.load(open(os.path.join(defs_dir, "ThingDef.json")))["defs"]
    R = json.load(open(os.path.join(defs_dir, "RecipeDef.json")))["defs"]
    byname = {x["defName"]: x for x in T}
    NAMES.clear()
    NAMES.update(byname)
    NAMES.update(r["defName"] for r in R)
    matcats = {}
    for m in MATS:
        sp = ((byname.get(m) or {}).get("fields") or {}).get("stuffProps") or {}
        matcats[m] = set(sp.get("categories") or [])
    rows = []   # (consumer, kind, material, how, jobs, packageId)

    def meta(x):
        f = x.get("fields") or {}
        tc = f.get("thingClass") or ""
        return {"defName": x["defName"], "label": x.get("label"), "thingClass": tc, "isTechHediff": f.get("isTechHediff"),
                "thingCategories": f.get("thingCategories"), "isDoor": "Door" in tc}

    for x in T:
        f = x.get("fields") or {}
        buildable = bool(f.get("designationCategory"))
        crafted = bool(f.get("recipeMaker"))
        if not (buildable or crafted):
            continue
        jobs = classify(meta(x))
        for j in jobs:
            POP.setdefault(j, {})[x["defName"]] = ",".join("%s %s" % (c.get("thingDef"), c.get("count")) for c in f.get("costList") or []) or "stuff:" + ",".join(f.get("stuffCategories") or [])
        for c in f.get("costList") or []:
            if c.get("thingDef") in MATS:
                rows.append((x["defName"], "thing", c["thingDef"], "fixed", jobs, x.get("packageId")))
        if f.get("stuffCategories"):
            sc = set(f["stuffCategories"])
            for m in MATS:
                if matcats[m] & sc:
                    rows.append((x["defName"], "thing", m, "stuff", jobs, x.get("packageId")))
    for r in R:
        f = r.get("fields") or {}
        prods = [p.get("thingDef") for p in f.get("products") or []]
        pj = sorted({j for p in prods if p in byname for j in classify(meta(byname[p]))})
        for ing in f.get("ingredients") or []:
            allowed = ((ing.get("filter") or {}).get("allowedDefs")) or []
            for m in MATS:
                if m in allowed:
                    rows.append((r["defName"], "recipe", m, "fixed" if len(allowed) == 1 else "broad", pj, r.get("packageId")))
    return rows


def summarize(rows):
    out = {}
    for job, (right, _) in KEY_JOBS.items():
        jr = [r for r in rows if job in r[4]]
        fixed_right = sorted({r[0] for r in jr if r[2] == right and r[3] == "fixed"})
        out[job] = {"right": right, "consumers": len({r[0] for r in jr}), "fixed_right": fixed_right,
                    "preference_right": len({r[0] for r in jr if r[2] == right and r[3] != "fixed"}),
                    "enforced": bool(fixed_right)}
    return out


def fixed_right(rows):
    """job -> sorted consumers fixing the job's right material."""
    return {job: sorted({r[0] for r in rows if job in r[4] and r[2] == right and r[3] == "fixed"})
            for job, (right, _) in KEY_JOBS.items()}


SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


def src_named(cands, root=SRC):
    """The subset of cands that some .xml/.cs file under src/ names as a whole word (our def, or our patch onto a donor's).
    Raises on a missing root or an unreadable file: a scan that could not look must not read as 'nobody names it'."""
    cands = set(cands)
    if not cands:
        return set()
    if not os.path.isdir(root):
        raise OSError("src root missing: %s" % root)
    pat = re.compile(r"(?<![\w])(%s)(?![\w])" % "|".join(re.escape(c) for c in sorted(cands, key=len, reverse=True)))
    hit = set()

    def boom(e):
        raise e
    for dp, dn, fn in os.walk(root, onerror=boom):
        dn[:] = [d for d in dn if d not in (".git", "bin", "obj")]
        for f in fn:
            if f.lower().endswith((".xml", ".cs")):
                with open(os.path.join(dp, f), encoding="utf-8", errors="replace") as fh:
                    hit.update(pat.findall(fh.read()))
    return hit


def _winpath(p):
    """C:\\x\\y -> /mnt/c/x/y under WSL; anything else unchanged."""
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p or "")
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m and os.name != "nt" else p


def donor_xml_fixes(capdir, cands):
    """Provenance from the donor's OWN files, not from our silence. cands: [(consumer, packageId, material)]. For each, find the
    mod's rootDir in the capture's manifest, read every XML under a Defs folder there, and find the def (a Make_X recipe is
    judged by its product X): True when that def's own costList names the material, or its own ingredients list it as their
    only thingDef. Anything not found (no manifest row, no rootDir, def inherited or patched in) is False: fail closed."""
    import xml.etree.ElementTree as ET
    man = os.path.join(os.path.dirname(capdir), "manifest.json")
    roots = {}
    if os.path.exists(man):
        for m in json.load(open(man, encoding="utf-8")).get("mods") or []:
            if m.get("packageId") and m.get("rootDir"):
                roots[m["packageId"].lower()] = _winpath(m["rootDir"])
    want = {}
    for c, pkg, mat in cands:
        want.setdefault((pkg or "").lower(), []).append((c, c[5:] if c.startswith("Make_") else c, mat))
    out = {c: False for c, _, _ in cands}
    for pkg, items in want.items():
        root = roots.get(pkg)
        if not root or not os.path.isdir(root):
            continue
        need = {d for _, d, _ in items}
        found = {}
        for dp, dn, fn in os.walk(root):
            if "Defs" not in dp.replace("\\", "/").split("/"):
                continue
            for f in fn:
                if not f.lower().endswith(".xml"):
                    continue
                try:
                    tree = ET.parse(os.path.join(dp, f))
                except (ET.ParseError, OSError):
                    continue
                for el in tree.getroot():
                    dn_ = el.findtext("defName")
                    if dn_ in need:
                        found.setdefault(dn_, []).append(el)
        for c, d, mat in items:
            for el in found.get(d, []):
                cost = el.find("costList")
                if cost is not None and cost.find(mat) is not None:
                    out[c] = True
                for ing in el.findall("ingredients/li"):
                    tds = [x.text for x in ing.findall("filter/thingDefs/li")]
                    if tds == [mat]:
                        out[c] = True
    return out


def new_hard(rows, baseline, attribute_hard=None):
    """job -> consumers fixing the right material now that the ruling-time baseline did not hold (ATTRIBUTE_HARD excepted)."""
    ah = ATTRIBUTE_HARD if attribute_hard is None else attribute_hard
    return {job: [c for c in cons if c not in set(baseline.get(job) or []) and c not in ah] for job, cons in fixed_right(rows).items()}


def new_hard_cands(rows, baseline, attribute_hard=None):
    """[(consumer, packageId, right material)] for every new hard consumer, the input donor_xml_fixes() takes."""
    pkg = {}
    for r in rows:
        pkg.setdefault(r[0], set()).add(r[5])
    return sorted({(c, p, KEY_JOBS[job][0]) for job, cs in new_hard(rows, baseline, attribute_hard).items() for c in cs
                   for p in pkg.get(c, {None}) if len(pkg.get(c, ())) == 1})


def donor_native(rows, baseline, named, provenance, attribute_hard=None):
    """New fixed right-material consumers that are a donor's own: exactly one, non-mandrake packageId on its rows; no src file
    names the def; and the donor's own XML fixes that material (provenance: donor_xml_fixes()). The 2026-10-11 ruling binds
    the exclusivity WE build; a donor update shipping its own plasteel prosthetic is the same kind of use the baseline froze
    (vanilla's and the donors' own prosthetics on plasteel), not a rule of ours. Unknown owner or provenance stays ours.
    Returns sorted (job, consumer, packageId)."""
    pkgs = {}
    for r in rows:
        pkgs.setdefault(r[0], set()).add(r[5])
    out = []
    for job, cs in new_hard(rows, baseline, attribute_hard).items():
        for c in cs:
            ps = pkgs.get(c, set())
            if len(ps) != 1:
                continue
            p = next(iter(ps))
            if p and not p.lower().startswith("mandrake.") and c not in named and provenance.get(c) is True:
                out.append((job, c, p))
    return sorted(out)


def rule_check(rows, baseline, names, attribute_hard=None, named=None, provenance=None):
    """The 2026-10-11 rule. baseline: job -> consumers already hard at the ruling. named/provenance: src_named() and
    donor_xml_fixes() of the new consumers, or None to treat every new consumer as ours (strict). Returns the problems."""
    ah = ATTRIBUTE_HARD if attribute_hard is None else attribute_hard
    bad = []
    now = fixed_right(rows)
    native = set() if (named is None or provenance is None) else {c for _, c, _ in donor_native(rows, baseline, named, provenance, ah)}
    for job, cons in now.items():
        old = set(baseline.get(job) or [])
        for c in cons:
            if c not in old and c not in ah and c not in native:
                bad.append("%s: NEW hard requirement %s fixes %s (a preference job; no unusual attribute named)" % (job, c, KEY_JOBS[job][0]))
        for c in sorted(old - set(cons)):
            if c in names:
                bad.append("%s: already-hard use LOOSENED: %s no longer fixes %s" % (job, c, KEY_JOBS[job][0]))
    return bad


def load_baseline():
    return json.load(open(BASELINE, encoding="utf-8"))


def probes(rows):
    """Return the list of failed probes (empty = instrument can see)."""
    bad = []
    have = {(r[0], r[2], r[3]) for r in rows}
    if ("BionicArm", "Plasteel", "fixed") not in have:
        bad.append("BionicArm fixed Plasteel not seen")
    if not any(r[0] == "BionicArm" and "prosthetics_implants" in r[4] for r in rows):
        bad.append("BionicArm not classed prosthetics_implants")
    if ("Door", "Plasteel", "stuff") not in have:
        bad.append("Door as Plasteel stuff not seen")
    if any(r[0] == "Door" and "blast_vault_doors" in r[4] for r in rows):
        bad.append("Door wrongly classed as a blast door")
    if ("Make_BionicArm", "Plasteel", "fixed") not in have:
        bad.append("Make_BionicArm fixed Plasteel not seen")
    return bad


def selftest():
    assert classify({"defName": "Door", "label": "door", "thingClass": "RimWorld.Building_Door", "isDoor": True}) == []
    assert "blast_vault_doors" in classify({"defName": "RSW_BlastDoor", "label": "blast door", "thingClass": "RimWorld.Building_Door", "isDoor": True})
    assert "prosthetics_implants" in classify({"defName": "X", "thingCategories": ["BodyPartsBionic"]})
    # planted defect: a fixed right-material consumer in a key job must read as enforced
    rows = [("RSW_BlastDoor", "thing", "RSW_Durasteel", "fixed", ["blast_vault_doors"], "x")]
    assert summarize(rows)["blast_vault_doors"]["enforced"] is True
    rows = [("RSW_BlastDoor", "thing", "RSW_Durasteel", "stuff", ["blast_vault_doors"], "x")]
    assert summarize(rows)["blast_vault_doors"]["enforced"] is False
    # planted defect: an empty census must fail the four must-see probes (the fifth is a must-not-see)
    assert len(probes([])) == 4, probes([])
    assert probes([("Door", "thing", "Plasteel", "stuff", ["blast_vault_doors"], "x")]).count("Door wrongly classed as a blast door") == 1
    # planted defects for the 2026-10-11 rule
    base = {"prosthetics_implants": ["BionicArm"], "large_frames": []}
    ok = [("BionicArm", "thing", "Plasteel", "fixed", ["prosthetics_implants"], "x")]
    assert rule_check(ok, base, {"BionicArm"}, {}) == []
    new = ok + [("RM_Factory", "thing", "RSW_Duranium", "fixed", ["large_frames"], "mandrake.rm.x")]
    assert len(rule_check(new, base, {"BionicArm", "RM_Factory"}, {})) == 1      # a new hard rule on a mechanical job
    assert rule_check(new, base, {"BionicArm", "RM_Factory"}, {"RM_Factory": ("RSW_Duranium", "x")}) == []
    loose = [("BionicArm", "thing", "Plasteel", "broad", ["prosthetics_implants"], "x")]
    assert len(rule_check(loose, base, {"BionicArm"}, {})) == 1                    # an already-hard use loosened
    assert rule_check([], base, set(), {}) == []                                    # a removed def is not a loosening
    # donor-native new hard use (a donor update): reported, not our rule; ours, or unproven provenance, still fails
    don = ok + [("OuterRim_CyberneticArm", "thing", "Plasteel", "fixed", ["prosthetics_implants"], "neronix17.outerrim.core")]
    yes = {"OuterRim_CyberneticArm": True}
    assert len(rule_check(don, base, {"BionicArm"}, {})) == 1                                         # strict: flagged
    assert rule_check(don, base, {"BionicArm"}, {}, named=set(), provenance=yes) == []
    assert donor_native(don, base, set(), yes, {}) == [("prosthetics_implants", "OuterRim_CyberneticArm", "neronix17.outerrim.core")]
    assert len(rule_check(don, base, {"BionicArm"}, {}, named={"OuterRim_CyberneticArm"}, provenance=yes)) == 1  # our src names it
    assert len(rule_check(don, base, {"BionicArm"}, {}, named=set(), provenance={})) == 1             # donor XML does not fix it
    assert len(rule_check(new, base, {"BionicArm", "RM_Factory"}, {}, named=set(), provenance={"RM_Factory": True})) == 1  # mandrake
    nopkg = ok + [("X_Arm", "thing", "Plasteel", "fixed", ["prosthetics_implants"], None)]
    assert len(rule_check(nopkg, base, {"BionicArm"}, {}, named=set(), provenance={"X_Arm": True})) == 1  # unknown owner
    two = don + [("OuterRim_CyberneticArm", "thing", "Plasteel", "fixed", ["prosthetics_implants"], "mandrake.rsw.x")]
    assert len(rule_check(two, base, {"BionicArm"}, {}, named=set(), provenance=yes)) == 1               # two owners: ours
    assert _winpath("C:\\A b\\c") == ("/mnt/c/A b/c" if os.name != "nt" else "C:\\A b\\c")
    return "census selftest ok"


def main():
    print(selftest())
    d = latest()
    if not d:
        print("UNMEASURED: no DefDump capture")
        return 2
    rows = census(d)
    pb = probes(rows)
    print("capture %s: %d consumer rows; probes %s" % (os.path.basename(os.path.dirname(d)), len(rows), "ok (5/5)" if not pb else "FAILED %r" % pb))
    if "--freeze-baseline" in sys.argv:
        fr = fixed_right(rows)
        fr["_capture"] = os.path.basename(os.path.dirname(d))
        with open(BASELINE, "w", encoding="utf-8") as fh:
            json.dump(fr, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print("baseline frozen:", BASELINE)
    cands = new_hard_cands(rows, load_baseline())
    named = src_named(c for c, _, _ in cands)
    prov = donor_xml_fixes(d, cands)
    rc = rule_check(rows, load_baseline(), NAMES, named=named, provenance=prov)
    dn = donor_native(rows, load_baseline(), named, prov)
    if dn:
        print("donor-native hard uses since the baseline (info: the donor's own XML fixes it, no src file names it): %d: %s"
              % (len(dn), ", ".join("%s (%s)" % (c, p) for _, c, p in dn[:8])))
    print("2026-10-11 rule: %s" % ("PASS (already-hard uses kept, no new hard rule)" if not rc else "FAIL %d: %s" % (len(rc), "; ".join(rc[:5]))))
    if "--csv" in sys.argv:
        p = sys.argv[sys.argv.index("--csv") + 1]
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["consumer", "kind", "material", "how", "key_jobs", "packageId"])
            for r in sorted(rows):
                w.writerow([r[0], r[1], r[2], r[3], ";".join(r[4]), r[5]])
        print("csv:", p)
        pp = os.path.splitext(p)[0] + "_jobs.csv"
        with open(pp, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["key_job", "def", "cost"])
            for j in sorted(POP):
                for d2, c in sorted(POP[j].items()):
                    w.writerow([j, d2, c])
        print("csv:", pp)
    for job, s in summarize(rows).items():
        print("%-21s defs=%-4d right=%-13s consumers=%-4d fixed_right=%-3d pref_right=%-4d %s" % (
            job, len(POP.get(job, {})), s["right"], s["consumers"], len(s["fixed_right"]), s["preference_right"],
            ("ENFORCED by " + ", ".join(s["fixed_right"][:6]) + (" ..." if len(s["fixed_right"]) > 6 else "")) if s["enforced"] else "preference only"))
    return 1 if (pb or rc) else 0


if __name__ == "__main__":
    sys.exit(main())
