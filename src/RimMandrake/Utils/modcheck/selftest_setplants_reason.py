#!/usr/bin/env python3
"""MODCHECK_ULTRAFAST_CLOCK_STALL_1, clause 2: jawa/set_plants names the engine's reason for every rejected cell.

The bloom fuzz strip came back "REJECTED 75" of 150 RM_Fuzz with no cause, because set_plants asked the engine
through the bool overload of PlantUtility.CanEverPlantAt, which passes writeNoReason:true and throws the reason away.
This reads the set_plants body in JawaBenchTerrainTools.cs and requires:
  1. the AcceptanceReport overload, with `out Thing blocker` and writeNoReason: false;
  2. no bool-overload call `CanEverPlantAt(cell, map)` left in the body;
  3. the rejection text is built from report.Reason (plus the blocker defName), not a fixed string;
  4. rejectedCells is filled per rejected cell with fertility, fertilityMin, polluted, blocker and reason,
     and is returned in the result object.
Then it mutates the source the way the blind checker named (the pre-fix bool call + generic Reject) and requires
every check above to go red on the mutant, so this test cannot pass a reverted tool. The live half is A2
(setplants_reason_probe.py): what text the engine actually hands back on an infertile cell.
Exit 0 all hold, 1 any fails.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.normpath(os.path.join(HERE, "..", "..", "bridgetools", "JawaBench.BridgeTools",
                                   "JawaBenchTerrainTools.cs"))

# The pre-fix shape the checker named: the bool overload and a reason that names no cause.
MUTANT = (
    "                            if (!plantDef.CanEverPlantAt(cell, map))\n"
    "                            {\n"
    "                                Reject(\"terrain or conditions cannot support \" + plantDef.defName);\n"
    "                                continue;\n"
    "                            }\n"
)


def set_plants_body(src):
    """The method body of the [Tool("jawa/set_plants")] method, up to the next [Tool(."""
    i = src.find('"jawa/set_plants"')
    if i < 0:
        return None
    j = src.find("[Tool(", i)
    return src[i:j if j > 0 else len(src)]


def checks(body):
    """name -> bool for every clause; body None means the tool is gone (all red)."""
    if body is None:
        return {"set_plants tool present": False}
    code = "\n".join(re.sub(r"//.*", "", ln) for ln in body.splitlines())   # comments do not count
    out = {}
    out["AcceptanceReport overload with out blocker and writeNoReason: false"] = bool(re.search(
        r"=\s*plantDef\.CanEverPlantAt\(\s*cell\s*,\s*map\s*,\s*out\s+Thing\s+blocker\b[^;]*writeNoReason\s*:\s*false",
        code, re.S))
    out["no bool-overload CanEverPlantAt(cell, map) call"] = not re.search(
        r"CanEverPlantAt\(\s*cell\s*,\s*map\s*\)", code)
    m = re.search(r"var\s+report\s*=\s*plantDef\.CanEverPlantAt", code)
    out["rejection reason built from report.Reason"] = bool(
        m and re.search(r"report\.Accepted", code) and re.search(r"\bwhy\b[^;]*report\.Reason", code)
        and re.search(r"Reject\([^;]*\+\s*why\s*\)", code))
    out["blocker defName appended to the reason"] = bool(re.search(r"blocker\.def\.defName", code))
    block = re.search(r"rejectedCells\.Add\(\s*new\s*\{(.*?)\}\s*\)", code, re.S)
    fields = set(re.findall(r"\b(\w+)\s*=", block.group(1))) if block else set()
    need = {"x", "z", "terrain", "fertility", "fertilityMin", "polluted", "blocker", "reason"}
    out["rejectedCells rows carry %s" % ",".join(sorted(need))] = need <= fields
    out["rejectedCells fertility read off the map's fertility grid"] = bool(
        block and re.search(r"fertility\s*=\s*map\.fertilityGrid\.FertilityAt\(\s*cell\s*\)", block.group(1)))
    out["rejectedCells returned in the result"] = bool(re.search(r"rejectionReasons\s*=\s*reasons\s*,\s*rejectedCells\s*,",
                                                                 code))
    return out


def mutate(body):
    """Replace the AcceptanceReport block (from `var report` to its `continue; }`) with the pre-fix bool call."""
    a = body.find("var report = plantDef.CanEverPlantAt")
    if a < 0:
        return None
    a = body.rfind("\n", 0, a) + 1
    while True:                                   # walk back over the comment lines that explain the fix
        p = body.rfind("\n", 0, a - 1) + 1
        if p >= a or not body[p:a].strip().startswith("//"):
            break
        a = p
    b = body.find("continue;", a)
    b = body.find("}", b) + 1
    b = body.find("\n", b) + 1
    return body[:a] + MUTANT + body[b:]


def main():
    fails = []

    def check(name, ok):
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            fails.append(name)

    with open(CS, encoding="utf-8") as f:
        src = f.read()
    body = set_plants_body(src)
    for name, ok in checks(body).items():
        check(name, ok)

    # Sanity probe: the instrument must see the pre-fix code as broken, clause by clause.
    mut = mutate(body) if body else None
    check("mutant built (bool overload + generic Reject)", bool(mut) and "CanEverPlantAt(cell, map))" in mut
          and "var report" not in mut)
    if mut:
        red = checks(mut)
        for name in ("AcceptanceReport overload with out blocker and writeNoReason: false",
                     "no bool-overload CanEverPlantAt(cell, map) call",
                     "rejection reason built from report.Reason"):
            check("mutant goes red: " + name, red.get(name) is False)
        check("mutant goes red: rejectedCells rows", not any(v for k, v in red.items() if k.startswith("rejectedCells rows")))
    # A rejectedCells block stripped of fertility must go red too.
    if body:
        nofert = re.sub(r"\n\s*fertility\s*=\s*map\.fertilityGrid\.FertilityAt\(cell\),", "\n", body)
        red = checks(nofert)
        check("fertility-less rejectedCells goes red", nofert != body and not any(
            v for k, v in red.items() if k.startswith(("rejectedCells rows", "rejectedCells fertility"))))
        generic = body.replace('": " + why', '""').replace("+ why)", ")")
        check("generic reason (why dropped) goes red", generic != body
              and checks(generic)["rejection reason built from report.Reason"] is False)
        hidden = re.sub(r"writeNoReason\s*:\s*false", "writeNoReason: true", body)
        check("writeNoReason: true goes red", hidden != body and checks(hidden)[
            "AcceptanceReport overload with out blocker and writeNoReason: false"] is False)

    # The live A2 probe's judge: green on the fixed tool's reply, red on the pre-fix reply and on each hole.
    sys.path.insert(0, HERE)
    import setplants_reason_probe as P
    why = "Need more fertile terrain."
    good = {"planted": 0, "rejected": 1, "rejectionReasons": {P.GENERIC + ": " + why: 1},
            "rejectedCells": [{"x": 1, "z": 1, "terrain": "PackedDirt", "fertility": 0.0, "fertilityMin": 0.05,
                               "polluted": False, "blocker": None, "reason": why}]}
    check("probe judge: fixed reply is ok", P.judge(good)[0] == "ok")
    prefix = {"planted": 0, "rejected": 1, "rejectionReasons": {P.GENERIC: 1}}
    check("probe judge: pre-fix reply (generic, no rejectedCells) fails", P.judge(prefix)[0] == "fail")

    def bent(**kw):
        r = {k: (dict(v) if isinstance(v, dict) else v) for k, v in good.items()}
        r["rejectedCells"] = [dict(good["rejectedCells"][0], **kw.pop("row", {}))]
        r.update(kw)
        return r
    check("probe judge: 'no reason given' fails",
          P.judge(bent(rejectionReasons={P.GENERIC + ": no reason given": 1}, row={"reason": "no reason given"}))[0] == "fail")
    check("probe judge: a non-fertility reason fails",
          P.judge(bent(rejectionReasons={P.GENERIC + ": Too cold": 1}, row={"reason": "Too cold"}))[0] == "fail")
    check("probe judge: fertility not below fertilityMin fails", P.judge(bent(row={"fertility": 1.0}))[0] == "fail")
    check("probe judge: missing fertility fails", P.judge(bent(row={"fertility": None}))[0] == "fail")
    check("probe judge: a blocked cell is retried, not passed", P.judge(bent(row={"blocker": "Wall"}))[0] == "blocker")
    check("probe judge: a planted cell fails", P.judge(bent(planted=1, rejected=0))[0] == "fail")

    print("%d FAIL" % len(fails) if fails else "ALL PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
