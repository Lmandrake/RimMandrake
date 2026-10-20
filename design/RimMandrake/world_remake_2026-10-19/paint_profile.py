#!/usr/bin/env python3
"""PAINT profile (owner card 2026-10-19: the smallest set that NEEDS to represent the world, the gravship and the
player characters). Seeds are listed with their reason; the closure adds (1) About.xml modDependencies (+v1.6),
(2) mod_facts class_ref/hard_dep edges, (3) UNGUARDED def references from a member's Defs XML (a leaf whose text names a
def that only non-members define, with no MayRequire on it or an ancestor) to a fixpoint. Offline.
Usage: paint_profile.py <roots.json> <dump_def_pkg.json> <out.json>   (core_defnames.txt beside out.json)
Only OUR mods' Defs are scanned for (3)."""
import json, os, re, sys, xml.etree.ElementTree as ET
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
M = os.path.join(R, "infrastructure/state/modlists/")
roots = json.load(open(sys.argv[1])); dp = json.load(open(sys.argv[2])); outp = sys.argv[3]
FULL = M + "ModsConfig.FULL.WAVE2_380_2026-10-19.xml"
full = [li.text.strip().lower() for li in ET.parse(FULL).getroot().find("activeMods")]
SEED = {}
for p in full:
    if p.startswith("ludeon."): SEED[p] = "Core + DLC: every list carries all five expansions (owner 2026-09-19/25)"
for p, why in {
    "mandrake.rm.biomes": "WORLD: Baroque Biomes, every RM_ biome (owner: 'obviously needed')",
    "mandrake.rut.patches": "WORLD: 28 RUT_ BiomeDefs, our factions, Scenario_Utinni, the founders' RUT_Jawa_Colonist kind",
    "mandrake.rm.weathersuite": "WORLD: hard dep of rut.patches; terminator/sun geometry engine",
    "mandrake.rut.weathersuite": "WORLD: Ash'karr's PlanetGeometry (substellar point) on the frozen planet",
    "mandrake.rm.inhabited": "WORLD: settlements as world objects (09 sec 6)",
    "mandrake.rut.inhabited": "WORLD: the Ash'karr settlement manifests (09 sec 6)",
    "mandrake.rm.injections": "WORLD: TileMutatorDefs / structure GenSteps named by tiles (09 sec 6)",
    "mandrake.rsw.injections": "WORLD: SW TileMutatorDefs (09 sec 6)",
    "mandrake.rut.injections": "WORLD: Ash'karr TileMutatorDefs (09 sec 6)",
    "mandrake.rut.ishkolandmarks": "WORLD: LandmarkDefs on the world map",
    "mandrake.rut.ashkarrlandmarkart": "WORLD: the landmark icons the map draws",
    "mandrake.rsw.shokk": "WORLD: a FactionDef present at the faction pass (09 sec 6)",
    "mandrake.rsw.droidworks": "WORLD/CHARACTERS: droid pawnkinds used by our factions (09 sec 6)",
    "mandrake.rm.patches": "WORLD: load fixes rut.patches loads after (09 sec 6)",
    "mandrake.rsw.patches": "WORLD: pawnkind/weather fixes rut.patches loads after (09 sec 6)",
    "mandrake.rsw.starwarsraces": "CHARACTERS: RSW_Jawa xenotype, genes, heads, eyes of all six founders; scenario's RSW_MandrakeJawa",
    "mandrake.rut.pawnflavor": "CHARACTERS: faction backstories/traits (founder Wim's RUT_Jawa_ReapsTheFlames)",
    "mandrake.rsw.armoury": "CHARACTERS+SHIP: the founders' Jawa robes/hood/poncho and the ship's guy762 floors + RSW_Durasteel",
    "mandrake.rsw.swbestiary": "CHARACTERS: the founders' Dewback and the scenario's bonded RSW_Ikee",
    "vanillaexpanded.vanillatraitsexpanded": "CHARACTERS: 6 founder traits (VTE_Dunce, VTE_Ecologist, VTE_Insomniac...)",
    "vanillaexpanded.vanillabackstoriesexpanded": "CHARACTERS: 3 founder backstories (Wave 2 HOLD)",
    "vanillaquestsexpanded.generator": "CHARACTERS: founder Nekko's adulthood VQE_PowerArchitect02 (Wave 2 HOLD)",
    "vanillaexpanded.gravship": "SHIP: VGE_AstrofuelPipe in Gravship_v2_ring",
    "vanillaexpanded.vfefactory": "SHIP: 6 VFEFactory machines in Gravship_v2_ring",
    "brrainz.rimbridgeserver": "TOOL: the bridge that stamps the CSV bundle (w9_run.py) and prints the ship",
    "owlchemist.cherrypicker": "TOOL: its cuts define the def set the world is made under",
    "mandrake.rm.planetpresetprime": "TOOL: world-creation page preset (09 sec 6: needed for the paint only)",
    "7f.alienworlds": "TOOL: generator framework Ash'karr was made with (02 sec 2)",
    "7f.alienworlds.tidallylocked": "TOOL: tidal-lock generator (02 sec 2); our JawaWorld_BiomeMix patches it",
    "oblitus.mylittleplanet": "TOOL: planet size until it is baked (09 sec 4)",
}.items():
    SEED[p] = why
facts = {}
for l in open(os.path.join(R, "design/RimMandrake/mod_audit/facts/mod_facts.jsonl")):
    j = json.loads(l); facts[j["packageId"].lower()] = j
CR = {}
for dep, j in facts.items():
    for d in j.get("dependants_detail") or []:
        if {"class_ref", "hard_dep", "hard_dep_v1.6"} & set(d["kinds"]):
            CR.setdefault(d["packageId"].lower(), set()).add(dep)


def hard(p):
    h = set()
    try:
        r = ET.parse(roots[p] + "/About/About.xml").getroot()
    except Exception:
        return h
    for li in r.findall("modDependencies/li"):
        h.add((li.findtext("packageId") or "").strip().lower())
    for v in r.findall("modDependenciesByVersion"):
        for ver in v:
            if ver.tag == "v1.6":
                for li in ver.findall("li"):
                    h.add((li.findtext("packageId") or "").strip().lower())
    return h


owner = {}
for k, v in dp.items():
    owner.setdefault(k.partition("/")[2], set()).update(v)
CORE = set()
_cf = os.path.join(os.path.dirname(outp), "core_defnames.txt")
if os.path.exists(_cf):
    CORE = {l.strip() for l in open(_cf) if l.strip()}  # Core/DLC <defName>s: a def another mod overrides is still present
tok = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]{3,}$")
refcache = {}


def defrefs(p):
    """{defName: count} of unguarded leaf references in p's Defs XML."""
    if p in refcache: return refcache[p]
    out = {}
    if not p.startswith("mandrake."): refcache[p] = out; return out  # third-party Defs use LoadFolders/version dirs: not scanned
    for dpth, dn, fn in os.walk(roots[p]):
        if "/Defs" not in dpth or "/Languages" in dpth: continue
        for f in fn:
            if not f.endswith(".xml"): continue
            try: root = ET.parse(os.path.join(dpth, f)).getroot()
            except Exception: continue
            def walk(e, guarded):
                g = guarded or bool(e.get("MayRequire") or e.get("MayRequireAnyOf"))
                if len(e) == 0 and e.text and tok.match(e.text.strip()) and not g and e.tag not in ("defName", "label", "description"):
                    out[e.text.strip()] = out.get(e.text.strip(), 0) + 1
                for c in e: walk(c, g)
            walk(root, False)
    refcache[p] = out; return out


mem = {p: SEED[p] for p in full if p in SEED}
missing_seed = [p for p in SEED if p not in full]
changed = True
while changed:
    changed = False
    for p in list(mem):
        for q in sorted(hard(p) | CR.get(p, set())):
            if q in full and q not in mem:
                mem[q] = "closure: hard dependency / class_ref of %s" % p; changed = True
        for n, c in defrefs(p).items():
            pk = owner.get(n)
            if not pk or n in CORE or any(x.startswith("ludeon.") or x in mem for x in pk): continue
            cand = sorted(x for x in pk if x in full)
            if len(cand) == 1 and n[0].isupper() or (len(cand) == 1 and "_" in n):
                q = cand[0]
                if q not in mem:
                    mem[q] = "closure: %s's Defs name %s unguarded" % (p, n); changed = True
order = [p for p in full if p in mem]
src = open(FULL, encoding="utf-8").read().split("\n"); o = []; ina = False
for l in src:
    if "<activeMods>" in l: ina = True
    if "</activeMods>" in l: ina = False
    m = re.match(r"\s*<li>([^<]+)</li>\s*$", l)
    if ina and m and m.group(1).strip().lower() not in mem: continue
    o.append(l)
dst = M + "ModsConfig.PAINT.WAVE2_2026-10-19.xml"
open(dst, "w", encoding="utf-8").write("\n".join(o))
lst = [li.text.strip().lower() for li in ET.parse(dst).getroot().find("activeMods")]
miss = [(p, q) for p in lst for q in hard(p) | CR.get(p, set()) if q in full and q not in lst]
json.dump({"n": len(lst), "members": {p: mem[p] for p in order}, "missing_seed": missing_seed, "closure_missing": miss},
          open(outp, "w"), indent=1)
print(dst, len(lst), "missing seeds", missing_seed, "closure missing", miss)
for p in order:
    if mem[p].startswith("closure"): print("  ", p, "<-", mem[p])
