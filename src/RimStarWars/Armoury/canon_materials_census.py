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


def rule_check(rows, baseline, names, attribute_hard=None):
    """The 2026-10-11 rule. baseline: job -> consumers already hard at the ruling. Returns the list of problems."""
    ah = ATTRIBUTE_HARD if attribute_hard is None else attribute_hard
    bad = []
    now = fixed_right(rows)
    for job, cons in now.items():
        old = set(baseline.get(job) or [])
        for c in cons:
            if c not in old and c not in ah:
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
    rc = rule_check(rows, load_baseline(), NAMES)
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
