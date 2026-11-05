#!/usr/bin/env python3
"""selftest for PACK_ANIMALS_RESTORE_EMPTY_SADDLES read straight from src (the dump lags src, so it cannot see a src break).

    python3 src/RimMandrake/Utils/selftest_pack_saddles_src.py

Pins: RUT_Jawa_FreeDroidEnclaves' Trader group has a <carriers> node whose every kind is a PawnKindDef in src, and its
races meet the allowedPackAnimals of each fixed biome (RM_LeaningScrub, RM_WeepingStones, RM_FeverWood, RM_Cauldron) as
src builds them: the inline RM_ list plus the Utinni PackAnimals_RestoreSaddles.xml additions (the engine rule:
PawnGroupKindWorker_Trader.CanGenerateFrom = carriers.Any(race in biome.allowedPackAnimals)). Also drives
vanilla_beast_carriers.item_problems (the plain run's exit gate) on fixtures, so it goes red if that gate is loosened.
Also pins that the Trader group's <traders> has a kind defined in src by a mod on the shipped list
(infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml) with no MayRequire off that list.
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vanilla_beast_carriers as v  # noqa: E402

SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
ENCLAVE_XML = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Defs", "FactionDefs", "JawaFreeDroidEnclaves.xml")
SADDLES = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "PackAnimals_RestoreSaddles.xml")
FAILS = []


def check(name, cond):
    print("%s  %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        FAILS.append(name)


def trader_carriers(path, faction):
    """-> [[carrier kind] per Trader group] of that FactionDef in that file; a group with no <carriers> gives []."""
    root = ET.parse(path).getroot()
    out = []
    for fd in root.iter("FactionDef"):
        if (fd.findtext("defName") or "").strip() != faction:
            continue
        for li in fd.findall("pawnGroupMakers/li"):
            if (li.findtext("kindDef") or "").strip() == "Trader":
                c = li.find("carriers")
                out.append([] if c is None else [k.tag for k in c])
    return out


def src_allowed(saddles=SADDLES):
    al = {b: list(r) for b, r in v.src_rm_allowed().items()}
    _, rm, pk = v.parse_patch(open(saddles, encoding="utf-8").read())
    for b, r in rm:
        al[b] = [x for x in al.get(b, []) if x != r]
    for b, r in pk:
        if r not in al.setdefault(b, []):
            al[b].append(r)
    return al


def enclave_problems(groups, allowed, kr, fixed=v.FIXED_BIOMES):
    bad = []
    if not groups:
        return ["%s has no Trader group" % v.ENCLAVE]
    for g in groups:
        if not g:
            bad.append("a %s Trader group has no carriers" % v.ENCLAVE)
        undefined = sorted(k for k in g if k not in kr)
        if undefined:
            bad.append("carrier kinds not PawnKindDefs in src: %s" % undefined)
    races = {kr[k] for g in groups for k in g if k in kr}
    for b in fixed:
        if not set(allowed.get(b, [])) & races:
            bad.append("%s carriers meet nothing in %s allowedPackAnimals %s" % (v.ENCLAVE, b, allowed.get(b)))
    return bad


# ---- the real src
kr = v.src_pawnkinds()
groups = trader_carriers(ENCLAVE_XML, v.ENCLAVE)
allowed = src_allowed()
check("sanity: src has PawnKindDefs (%d) and the enclave file parses (%d Trader group(s))" % (len(kr), len(groups)),
      len(kr) > 50 and len(groups) >= 1)
for b in v.FIXED_BIOMES:
    check("src: %s allowedPackAnimals non-empty (%s)" % (b, ",".join(allowed.get(b, []))), bool(allowed.get(b)))
bad = enclave_problems(groups, allowed, kr)
check("src: %s Trader carriers meet every fixed biome: %s" % (v.ENCLAVE, bad or "ok"), not bad)

# ---- the instrument can see a break (mutants on the real data)
check("mutant: enclave <carriers> deleted -> red", enclave_problems([[] for _ in groups], allowed, kr) != [])
noscrub = dict(allowed, RM_LeaningScrub=[])
check("mutant: RM_LeaningScrub list emptied -> red", enclave_problems(groups, noscrub, kr) != [])
check("mutant: carrier kind cut from src -> red", enclave_problems([g + ["RM_BovineBeetle"] for g in groups], allowed, kr) != [])

# ---- the Trader group's <traders> must resolve on the SHIPPED list (A5 live fail 2026-11-05: the sole trader was
# MayRequire'd on Droid Depot, absent from the list, so the group had no trader and never generated, carriers or not).
SHIPPED = os.path.join(SRC, "..", "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")


def shipped_ids(path=SHIPPED):
    return {(e.text or "").strip().lower() for e in ET.parse(path).getroot().find("activeMods")}


def kind_package(kind, root=SRC):
    """packageId (lowercased) of the src mod that defines PawnKindDef `kind`, or None."""
    needle = "<defName>%s</defName>" % kind
    for d, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".xml") and needle in open(os.path.join(d, f), encoding="utf-8", errors="ignore").read():
                up = d
                while len(up) > len(root):
                    ab = os.path.join(up, "About", "About.xml")
                    if os.path.exists(ab):
                        return (ET.parse(ab).getroot().findtext("packageId") or "").strip().lower()
                    up = os.path.dirname(up)
    return None


def trader_entries(path, faction):
    """-> [[(trader kind, MayRequire or None)] per Trader group]."""
    out = []
    for fd in ET.parse(path).getroot().iter("FactionDef"):
        if (fd.findtext("defName") or "").strip() != faction:
            continue
        for li in fd.findall("pawnGroupMakers/li"):
            if (li.findtext("kindDef") or "").strip() == "Trader":
                t = li.find("traders")
                out.append([] if t is None else [(k.tag, k.get("MayRequire")) for k in t])
    return out


def trader_problems(tgroups, kr, ids, pkg=kind_package):
    bad = []
    for g in tgroups:
        live = [k for k, mr in g if k in kr and (mr is None or mr.lower() in ids) and pkg(k) in ids]
        if not live:
            bad.append("a %s Trader group has no trader kind that resolves on the shipped list: %s" % (v.ENCLAVE, g))
    return bad or ([] if tgroups else ["%s has no Trader group" % v.ENCLAVE])


ids = shipped_ids()
tg = trader_entries(ENCLAVE_XML, v.ENCLAVE)
check("sanity: shipped list parses (%d ids, droidworks on it)" % len(ids), len(ids) > 200 and "mandrake.rsw.droidworks" in ids)
tbad = trader_problems(tg, kr, ids)
check("src: %s Trader <traders> resolve on the shipped list: %s" % (v.ENCLAVE, tbad or tg), not tbad)
check("mutant: Droid Depot trader (the A5 fail) -> red",
      trader_problems([[("OuterRim_ProtocolDroid", "Neronix17.OuterRim.DroidDepot")]], kr, ids) != [])
check("mutant: owned trader gated on a mod off the list -> red",
      trader_problems([[(k, "Neronix17.OuterRim.DroidDepot") for k, _ in g] for g in tg], kr, ids) != [])
check("mutant: empty <traders> -> red", trader_problems([[] for _ in tg], kr, ids) != [])

# ---- vanilla_beast_carriers.item_problems, the plain run's exit gate
ok = {"can_trade": True}
no = {"can_trade": False}
full = {b: {v.ENCLAVE: ok, "X": ok} for b in v.FIXED_BIOMES}
al = {b: ["R"] for b in v.FIXED_BIOMES}
check("gate: all good -> no problems", v.item_problems(full, ["Banned"], al, {"Banned"}) == [])
check("gate: unbanned zero-carrier group -> red", v.item_problems(full, ["Live"], al, {"Banned"}) != [])
m2 = {b: dict(r) for b, r in full.items()}
m2["RM_Cauldron"][v.ENCLAVE] = no
check("gate: enclave cannot reach RM_Cauldron -> red", v.item_problems(m2, [], al, set()) != [])
m3 = {b: dict(r) for b, r in full.items()}
del m3["RM_FeverWood"][v.ENCLAVE]
check("gate: enclave absent from a fixed biome row -> red", v.item_problems(m3, [], al, set()) != [])
check("gate: fixed biome with empty list -> red", v.item_problems(full, [], dict(al, RM_WeepingStones=[]), set()) != [])
check("gate: real banned list names RM_Faction_CombHolds", "RM_Faction_CombHolds" in v.banned_factions())

print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), FAILS)))
sys.exit(1 if FAILS else 0)
