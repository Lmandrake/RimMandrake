# Sea floor and catch census, 2026-10-29

Item: SEA_FLOOR_AND_CATCH_PASS_1 (FOUNDRY). This is an offline sizing pass: no game, no bridge, no deploy.
It answers one question: for each sea, which catch entries have no living, swimming body on the sea floor, and what is the smallest wave of defs that closes the gap?

## Verdict

- **The floor half is already built on the content tier.** On RM_TheScald, RM_GreySea, RM_TwilightSea and RM_TheChill, 0 catch entries lack a floor body.
  - SEA_FISHABLES_ALIVE_IN_DEPTHS_1 built that coverage. It was validated at L1 at 59790a18c.
  - Two separate instruments agree on the 0 (see Cross-check).
- **Only one gap remains, and it needs a decision, not a build.** `RSW_ColoClawFish` sits in the Twilight rare table as a corpse, and is cast in no wildAnimals anywhere in src.
  - The commission (section 2D.rare) reserves it as Twilight's apex body.
  - The decision is one of two:
    - cast it live, which is one patch row and 0 new defs;
    - or record why it stays catch-only.
  - This is filed as COLOCLAW_DECIDE_APEX_ALIVE_OR_CORPSE_ONLY.
- **The RUT_ tier shows 8, 7, 10 and 7 catches with no body, but this is not a defs gap.**
  - The RUT_ sea BiomeDefs are FROZEN as of 2026-09-25 and only carry the saved world until the Phase B repaint (BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL).
  - Every species they catch already has an RM_ body.
  - A RUT_ tile has no `RM_SeabedAccessExtension.floorBiome`, so `RM_SeabedLayer.FloorBiomeFor()` falls back to the generic, empty `RM_SeabedFloor`.
  - The repaint is what fixes this. New defs would not.

## Definitions used

- **Floor counterpart.** A catch has a floor counterpart when its body race is in the RM_ sea's `wildAnimals`.
  - At startup, `RM_SeabedFloorLife.cs` copies each RM_ sea's wildAnimals, fishTypes and flora onto `RM_SeabedFloor_<Sea>`. The sea-to-floor wiring is in `src/RimMandrake/DivingInteraction/Patches/RM_SeabedFloorBiomeWiring.xml`.
  - The engine has no "swim" flag, so "swimming" cannot be measured as a field.
- **Pairing a catch with its body.** `RM_<X>Catch` pairs with race `RM_<X>`, after stripping the RM_/RUT_/RSW_ prefix and the `Catch` suffix.
  - There is one alias, `RM_Saal` to `RM_Noohm`, which is `CATCH_BODY_ALIAS` in TerminalBiomes/validation.py.

## Measurements (src at 2d69fdab99)

The parse read 2961 XML files with 0 parse errors. It found 3525 ThingDefs, 667 of which are races, and 915 PawnKindDefs.

Probe (proves the instrument can see):
- `RM_Essarn` is a race. `RM_EssarnCatch` is a thing and not a race.
- The same race set that misses `RSW_ColoClawFish` from every wildAnimals list does contain `RSW_Mee` and `RSW_Faa`.

Other checks:
- No catch item is itself a race, so the GREENTIDE bug class is absent.
- Every wildAnimals entry is a race.
- Every body has a PawnKindDef whose race matches.

| sea | catch entries | lacking a body in this sea | wildAnimals | animals only this sea carries (beyond the catch bodies) |
|---|---:|---:|---:|---|
| RUT_TheScald (frozen) | 8 | 8 | 2 | RSW_Faa .5, RSW_Mee .5 |
| RM_TheScald | 9 | **0** | 10 | RM_ScaldWalker |
| RUT_GreySea (frozen) | 7 | 7 | 1 | RSW_Reefback |
| RM_GreySea | 4 | **0** | 9 | RM_Reefback, RM_Fessk, RM_Otheska, RM_Corrik, RM_Orruhmu |
| RUT_TwilightSea (frozen) | 10 (all patch-added, BiomeFishTypes_TwilightDeep.xml) | 10 | 1 | RSW_Lanternwhale |
| RM_TwilightSea | 14 | **0** | 21 (3 via UtinniPatches WildAnimals_TwilightSea.xml) | RM_Bulloo, RM_DancingSkresh, RM_GrippingTerror, RM_Lanternwhale, RM_Loohn, RM_Lunoowa, RSW_SandoAquaMonster |
| RUT_PropaneLake (frozen) | 7 | 7 | 1 | RUT_VWake (animalDensity unset) |
| RM_TheChill (Propane twin) | 9 | **0** | 10 | RM_Hesuun |

Rare tables (`rareCatchesSetMaker`):
- **RM_GreySea:** RM_SaltCameo and Silver. Neither is a species.
- **RM_TwilightSea, via RM_RareTwilightCatches:**
  - Corpse_RSW_ColoClawFish, which is the residual described above;
  - RM_AluunCatch and RM_NiimCatch, which both have bodies in the sea;
  - RUT_LampBlack, which is not a species.
- **RM_TheChill:** Chemfuel and RM_OdduCatch. The RM_OdduCatch body is in the sea.

Notes, none of which is a gap:
- The Sallik family (RM_Sallik, Karrud, Hessal, Oomal, Maalu, Immu, Haarn and their `*Catch` items) was cut from the Grey Sea by an owner card on 2026-10-12. It is now cast nowhere. That was a ruling, not a hole.
- RSW_Mee and RSW_Faa are listed in both RUT_TheScald and RM_TwilightSea. The no-eviction ruling applies, so nothing is proposed.

## Smallest honest wave per sea

| sea | new defs | work |
|---|---:|---|
| The Scald | 0 | none. SCALD_FLOOR_PASS_1 is already done. |
| Grey Sea | 0 | none beyond GREYSEA_FLOOR_PASS_1, which is ready. |
| The Chill / Propane Lake | 0 | none beyond PROPANELAKE_FLOOR_PASS_1, which is proposed. |
| Twilight Sea | 0 | COLOCLAW_DECIDE_APEX_ALIVE_OR_CORPSE_ONLY. Either add one row to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_TwilightSea.xml`, or write down the reason it stays catch-only. Casting it live would not multi-home it, because it is cast nowhere today. |

No child item was filed for the three 0-def seas. Each already has a per-sea pass item, and a fourth item with nothing in it would only duplicate that one.

## Blockers (why the floor is not yet playable)

1. **SEABED_DESCENT_ASCENT_1** is proposed and unbuilt, and it needs the bridge. Until it exists, no ship can fly down to the floor.
2. **SEABED_FLOOR_GENERATORS_1** is done at cbc8adc7c, but its live proof is still owed.
3. **The live L2 floor census is still owed** (SEA_FISHABLES_ALIVE_IN_DEPTHS_1 A3). The aluun art is also owed (its A4, L3).
4. **RUT_ sea tiles fall back to the generic, empty RM_SeabedFloor** until BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL and BIOME_PAINT_ONCE_AT_THE_END_1 land. SEABED_PER_SEA_FLOORS_1 is blocked.

## Not measurable offline

- Which biome the live save carries on its sea tiles, RUT_ or RM_. That decides whether the player currently sees a lifeless floor.
- Whether animals actually spawn on the floor maps (RM_SeabedFloorLife runs at runtime).
- Any "swimming" property. The engine has no such field, so the counterpart is defined as presence in wildAnimals.

## Parser limitation

`census.py` skips a `rareCatchesSetMaker` that is added by a patch. RUT_TwilightSea gets `RUT_RareTwilightCatches` this way, from `src/RimUtinni/UtinniPatches/Patches/BiomeFishTypes_TwilightDeep.xml` line 50. This affects a frozen sea only. Patch-added wildAnimals and fishTypes rows ARE parsed.

## Re-run

From the repo root:

```
mkdir -p /mnt/d/ClaudeWork/rimmandrake/sea_census
awk '/^```python census/{f=1;next} /^```$/{f=0} f' design/RimMandrake/sea_floor_census_2026-10-29.md > /mnt/d/ClaudeWork/rimmandrake/sea_census/census.py
python3 -I /mnt/d/ClaudeWork/rimmandrake/sea_census/census.py src > /mnt/d/ClaudeWork/rimmandrake/sea_census/out.json
python3 -c "import json;o=json.load(open('/mnt/d/ClaudeWork/rimmandrake/sea_census/out.json'));print(o['files_parsed'],o['probe']);[print(s,len(v.get('catches',[])),v.get('catches_without_body_in_sea')) for s,v in o['seas'].items()]"
```

## Cross-check (a second, independent instrument)

```
python3 -c "import sys;sys.path.insert(0,'src/RimMandrake/TerminalBiomes');import validation;print(validation.sea_catch_alive_checks())"   # -> []
python3 src/RimMandrake/TerminalBiomes/selftest_sea_catch_alive.py   # -> ALL OK, 3 mutants red
```

## census.py

```python census
#!/usr/bin/env python3
"""Sea floor/catch census. Run from the repo root: python3 -I census.py [src_dir] > out.json
Parses every .xml under src/ as XML elements (never counts text). Reports, per sea BiomeDef,
wildAnimals (inline + patch-added), fishTypes rows (inline + patch-added), rare-catch set contents,
and for each catch item the living body it pairs with."""
import json, os, re, sys
import xml.etree.ElementTree as ET

SRC = sys.argv[1] if len(sys.argv) > 1 else "src"
PAIRS = [("RUT_TheScald", "RM_TheScald"), ("RUT_GreySea", "RM_GreySea"),
         ("RUT_TwilightSea", "RM_TwilightSea"), ("RUT_PropaneLake", "RM_TheChill")]
ALIAS = {"RM_Saal": "RM_Noohm", "RUT_Saal": "RM_Noohm"}  # TerminalBiomes/validation.py CATCH_BODY_ALIAS
SEAS = {s for p in PAIRS for s in p} | {"RM_SeabedFloor", "RM_SeabedFloor_TheScald", "RM_SeabedFloor_GreySea",
                                        "RM_SeabedFloor_TwilightSea", "RM_SeabedFloor_TheChill"}
things, named, biomes, tsm, patch_wa, patch_ft, parse_err, nfiles = {}, {}, {}, {}, {}, {}, [], 0
XP = re.compile(r'BiomeDef\[defName="([^"]+)"\]((?:/[A-Za-z_]+)*)')


def rows_of(node):
    return [(c.tag, (c.text or "").strip(), c.get("MayRequire")) for c in node if isinstance(c.tag, str)]


def walk_patch(op, fn):
    for o in op.iter():
        xp = o.findtext("xpath")
        val = o.find("value")
        if not xp or val is None:
            continue
        m = XP.search(xp)
        if not m or m.group(1) not in SEAS:
            continue
        b, tail = m.group(1), m.group(2)
        cls = o.get("Class", "")
        if tail.endswith("/wildAnimals"):
            patch_wa.setdefault(b, []).extend((t, v, mr, fn, cls) for t, v, mr in rows_of(val))
        elif "/fishTypes" in tail:
            band = tail.split("/fishTypes")[1].strip("/") or "?"
            for t, v, mr in rows_of(val):
                if band == "?":  # whole bands added
                    sub = val.find(t)
                    for t2, v2, mr2 in rows_of(sub):
                        patch_ft.setdefault(b, []).append((t, t2, v2, fn))
                else:
                    patch_ft.setdefault(b, []).append((band, t, v, fn))
        elif tail == "":
            for w in val.findall("wildAnimals"):
                patch_wa.setdefault(b, []).extend((t, v, mr, fn, cls) for t, v, mr in rows_of(w))
            for f in val.findall("fishTypes"):
                for g in f:
                    if g.tag != "rareCatchesSetMaker":
                        patch_ft.setdefault(b, []).extend((g.tag, t, v, fn) for t, v, mr in rows_of(g))


for dp, _, fns in os.walk(SRC):
    for fn in fns:
        if not fn.endswith(".xml"):
            continue
        p = os.path.join(dp, fn)
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            parse_err.append("%s: %s" % (p, e)); continue
        nfiles += 1
        rel = os.path.relpath(p, SRC)
        if root.tag == "Patch":
            walk_patch(root, rel); continue
        for d in root:
            if not isinstance(d.tag, str):
                continue
            dn = d.findtext("defName")
            if d.get("Name"):
                named[d.get("Name")] = d
            if d.tag == "ThingDef" and dn:
                things[dn] = (d, rel)
            elif d.tag == "BiomeDef" and dn in SEAS:
                biomes[dn] = (d, rel)
            elif d.tag == "ThingSetMakerDef" and dn:
                tsm[dn] = d


def is_race(d, depth=0):
    if d is None or depth > 12:
        return False
    if d.find("race") is not None:
        return True
    return is_race(named.get(d.get("ParentName")), depth + 1)


races = {n for n, (d, _) in things.items() if is_race(d)}


def tsm_items(name):
    d = tsm.get(name)
    if d is None:
        return None
    return sorted({e.text.strip() for e in d.iter() if e.tag in ("thingDef", "def") and e.text}
                  | {c.tag for e in d.iter() if e.tag in ("filter", "thingDefs") for c in e.iter()
                     if c.tag not in ("filter", "thingDefs", "li") and c.tag in things}
                  | {li.text.strip() for e in d.iter() if e.tag == "thingDefs" for li in e if li.text})


def body_for(catch):
    if catch in ALIAS:
        return ALIAS[catch]
    stem = re.sub(r"^(RM|RUT|RSW)_", "", catch)
    stem = re.sub(r"Catch$", "", stem)
    return stem


def candidates(catch):
    stem = body_for(catch)
    if stem in races:
        return [stem]
    return sorted(r for r in races if re.sub(r"^(RM|RUT|RSW|AA)_", "", r) == stem)


out = {"files_parsed": nfiles, "parse_errors": parse_err, "thingdefs": len(things), "race_thingdefs": len(races),
       "probe": {"RM_Essarn_is_race": "RM_Essarn" in races, "RM_EssarnCatch_is_race": "RM_EssarnCatch" in races,
                 "RM_EssarnCatch_is_thing": "RM_EssarnCatch" in things}, "seas": {}}
for sea in sorted(SEAS):
    if sea not in biomes:
        out["seas"][sea] = {"missing": True}; continue
    b, rel = biomes[sea]
    wa = [(t, v, mr, "inline") for t, v, mr in rows_of(b.find("wildAnimals"))] if b.find("wildAnimals") is not None else []
    wa += [(t, v, mr, fn) for t, v, mr, fn, cls in patch_wa.get(sea, [])]
    ft, rare = [], []
    f = b.find("fishTypes")
    if f is not None:
        for g in f:
            if g.tag == "rareCatchesSetMaker":
                rare.append(g.text.strip())
            else:
                ft += [(g.tag, t, v, "inline") for t, v, mr in rows_of(g)]
    ft += patch_ft.get(sea, [])
    wa_names = {r[0] for r in wa}
    catches = []
    for band, item, w, src in ft:
        c = candidates(item)
        catches.append({"band": band, "item": item, "w": w, "src": src, "item_is_thing": item in things,
                        "item_is_race_BUG": item in races, "body_defs": c,
                        "body_in_this_sea": [x for x in c if x in wa_names]})
    rare_rows = {r: tsm_items(r) for r in rare}
    out["seas"][sea] = {
        "file": rel, "animalDensity": b.findtext("animalDensity"), "maxFishPopulation": b.findtext("maxFishPopulation"),
        "wildAnimals": [{"def": t, "w": v, "MayRequire": mr, "src": s, "in_src": t in things, "is_race": t in races} for t, v, mr, s in wa],
        "catches": catches, "rare": rare_rows,
        "catches_without_body_in_sea": sorted({c["item"] for c in catches if not c["body_in_this_sea"]}),
        "catches_without_any_body_def": sorted({c["item"] for c in catches if not c["body_defs"]})}
json.dump(out, sys.stdout, indent=1)
```
