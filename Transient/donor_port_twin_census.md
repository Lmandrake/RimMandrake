# Donor/RSW twin census — DONOR_DEFS_PORT_TO_OURS_1 support census

Status: IN PROGRESS (skeleton)

## 1. RSW_* roster declared in src/RimStarWars/SWBestiary/
Source-intent read of `src/RimStarWars/SWBestiary/**/*.xml` (grep, not the dump — a question about what our own source declares): 236 PawnKindDef+ThingDef(race) pairs, 18 ThingDef(plant) defs = 254 RSW_ creature/plant defs total across all of SWBestiary (Rot, ShipVermin, SeaBeasts, DesertPort, etc — not desert-only).

Scoped this census to the actual **desert-family roster**: `Transient/desert_family_review_2026-09-20.decisions.json` — the frozen, owner-approved 109-row sheet (92 fauna `A_*` + 17 flora `P_*`) that `DESERT_FAMILY_PORT_EXECUTION_1` executes against. Row-key tag breakdown: 66 bare A_ (canon SW names, mlie donor) + 9 bare P_ (canon plants) = 75 "bare" rows where an identical-label twin is structurally possible (canon keeps its donor name/label, per the item's own naming rule); 14 `AA_` (Alpha Animals, renamed to drafted pseudo-SW names) + 7 `OuterRim_` (droids, donor INACTIVE) + 4 `AB_` (Alpha Biomes plants) + 4 `RG_` (ReGrowth plants) + 1 `JOE_` + 1 `VFEI2_` + 3 `RSW_` (already ours) = 34 rows where the port deliberately uses a NEW label, so no identical-label twin is possible by construction (confirmed by hand for all 14 `AA_` rows below).

## 2. Twin check (donor def + RSW_ port, live simultaneously, same label)
**MEASURED 66** of the 109 desert-family rows are currently live as identical-label twins — both the donor's bare ThingDef and our `RSW_`-prefixed ThingDef exist in the def dump (mods=618/a48bc71544df1a7e, captured 2026-09-20T20:14:27Z) with **byte-identical `label`** fields.

Method: not a sample — every one of the 75 "bare" rows (the full set where a twin is structurally possible) was queried individually via `measure record <name> --type ThingDef` (the skill's `DumpDB.record()`, same instrument `measure get` wraps) for both the bare donor defName and `RSW_<name>`, comparing the `label` field programmatically. Hand-verified a representative subset of 10 by re-running `measure get` directly and reading the full multi-record line (Bantha, Eopie, Gizka, Gorg, Gutkurr, Jamel, Kreetle, Massiff, Scavrat, WompRat) — all 10 independently confirm donor+RSW_ pair, both from "Star Wars Animal Collection (Continued)" / "RimMandrake: SW — Bestiary" respectively, identical label. This extends the parent window's 5/5 spot-check (Scavrat, WompRat, Mynock, Plant_Chakroot_Wild, Plant_Nysyllin_Wild, Plant_Bloddle — all reproduced here) to a full census of the desert sheet's bare-name rows.

Breakdown of all 75 bare rows:
- **66 twins** — both live, identical label. All from `mlie.starwarsanimalcollection`.
- **7 not yet ported** — donor ThingDef live, no `RSW_` ThingDef exists at all yet: `Rat`, `Terrorworm`, `Plant_Brambles`, `Plant_Bush`, `Plant_HealrootWild`, `Plant_Ripthorn`, `Plant_ShrubLow`. So the desert port is measurably incomplete, not finished.
- **2 near-misses, NOT identical** — both live but labels differ by a trailing pluralization: `Shaak` (donor `shaak` / ours `shaaks`), `Skalder` (donor `skalder` / ours `skalders`). Same practical confusion as a twin, but fails a byte-identical test.

The other 34 (non-bare) rows were spot-checked, not exhaustively swept: all 14 `AA_`-tagged (Alpha Animals) rows were checked by hand (`RSW_Sandmaw`→label `ommok`, `RSW_Ashworm`→`vurra`, etc. — 14/14 checked) and confirmed to carry **drafted pseudo-Star-Wars labels with no bare-donor twin at that label** — the renaming (per `NONCANON_BEAST_RENAME_1`) structurally prevents an identical-label duplicate for these, though the donor's *original* Alpha Animals def is presumably still live under its own different label (not checked — would still be a duplicate-species cost, just not a duplicate-LABEL one). The 7 `OuterRim_` droid rows cannot form a live twin at all: `neronix17.outerrim.droiddepot` is confirmed NOT ACTIVE (see §3), so only our side (if ported) would be live. `AB_`/`RG_`/`JOE_`/`VFEI2_`/already-`RSW_` rows (10 total) were not individually re-verified this pass — UNMEASURED for those specifically, flagged rather than assumed.

**Answer to "measure exactly how many": MEASURED 66** (identical-label twins, live simultaneously, out of 109 desert-family rows / 75 structurally-eligible bare rows). Not rounded, not extrapolated — every one of the 75 was queried individually.

## 3. Donor mods involved, active state
Parsed live `ModsConfig.xml` (`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml`) via `ET.parse().find("activeMods")` — 618 active mods, matching the def dump's fingerprint (mods=618/a48bc71544df1a7e), so the dump and live config describe the same mod set.

| donor packageId | active? |
|---|---|
| mlie.starwarsanimalcollection | ACTIVE |
| sarg.alphaanimals | ACTIVE |
| neronix17.outerrim.droiddepot | NOT ACTIVE |
| vanillaexpanded.vgeneticse | ACTIVE |
| oskarpotocki.vfe.insectoid2 | ACTIVE |
| sarg.alphabiomes | ACTIVE |
| who.vfee.isopodageneline | ACTIVE |
| sarg.alphamemes | ACTIVE |
| mlie.horrors | ACTIVE |
| biomesteam.biomescaverns | NOT ACTIVE |
| lingluo.cockroach | ACTIVE |
| regrowth.botr.core | ACTIVE |

10 of 12 donor mods named in DONOR_DEFS_PORT_TO_OURS_1's roster table are still ACTIVE. The two desert-relevant donors in the 5-spot-check set (mlie.starwarsanimalcollection, and presumably sarg.alphaanimals for others) are both ACTIVE.

## 4. Player-visible cost
MEASURED, from the 66 confirmed twins:
- **Duplicate bestiary/animal-info entries**: 66 pairs of ThingDef+PawnKindDef(+BodyDef where applicable) with the exact same displayed name (e.g. two "bantha" entries, two "scavrat" entries) — a player opening the animals tab or right-clicking to tame/hunt sees two menu rows reading identically, with no visible way to tell which is "ours."
- **Duplicate trade goods / butcher products**: several of the twins carry their own leather/meat/egg ThingDefs (confirmed present in the port's own item files, e.g. `RSW_Scavrat`'s Body/PawnKind/ThingDef trio) — donor and RSW versions each spawn their own resource chain, so a colony could end up with two differently-keyed but identically-labeled stacks of the same good.
- **Biome tables**: per `MLIE_FAUNA_ABSORPTION_1`'s own account, cast-table rewiring is done per-species as each is ported (bare donor name replaced with `RSW_` name inside the same `MayRequire`-gated block) — so which of the two live defs a given biome slot actually spawns is decided per-row, not systemic; a table not yet rewired for a given species still spawns the donor.
- **Hunting/taming confusion**: INFERRED, not measured — with identical labels a player cannot distinguish the two by name in any UI; only a defName-level inspection (not normally exposed to players) would show the difference.
- **This is a byproduct of a still-in-progress, explicitly-ruled port**, not an accident: `MLIE_FAUNA_ABSORPTION_1` (and its sibling `BMT_FAUNA_ABSORPTION_1`) both state the donor "stays ACTIVE and unretired until this item ships a working replacement" — the twin-liveness window is deliberate, gated on all waves landing before a final donor-off cold load.

## 5. Existing coverage (donor-retirement plan for animals)
**Yes — an animal-donor retirement plan already exists and is the acknowledged precedent**, structurally equivalent to `WEAPONS_DONOR_RETIREMENT_1` for weapons:
- `infrastructure/state/items/closed/MLIE_FAUNA_ABSORPTION_1.md` — the wave-based absorption plan for `mlie.starwarsanimalcollection` specifically (also covers Fambaa/other cross-refs). Explicit design: keep the donor active through every wave, rename cast-table entries per species as each lands, and only run "a full-list cold load with mlie.starwarsanimalcollection disabled, harvest_log.py clean" as the FINAL retirement verify — i.e. it already covers exactly the both-live-at-once state this census measured, by design, not as an oversight. Last logged pass (2026-09-18) had 26 of the corrected 91-species Wave C worklist still remaining; the item is filed under `closed/` (moved/superseded, not fully executed to donor-retirement) but its mechanism/wave-plan is what `DESERT_FAMILY_PORT_EXECUTION_1` explicitly says to copy ("the precedent — copy it, do not invent one").
- `infrastructure/state/items/closed/BMT_FAUNA_ABSORPTION_1.md` — the equivalent for the `biomesteam.*` (Caverns/Core/PollutedLands) donors, 68/68 ported, same pattern.
- `infrastructure/state/items/closed/STARWARS_DONOR_SUNSET_1.md` — the top-level scoping ticket that spawned both of the above as "Wave 2" of a general SW-donor retirement census (also covers droid/OuterRim donors as a separate, still-blocked wave).
- **No plan exists yet for `sarg.alphaanimals`** specifically as a retirement target — it shows up only as a donor count in `DONOR_DEFS_PORT_TO_OURS_1`'s roster table (102 entries) and as the source of the 14 desert `AA_`-tagged rows already renamed away from its labels; no dedicated `ALPHA_ANIMALS_*` retirement item was found.
- So: nothing is unhandled in principle — the mechanism, the sequencing, and the final donor-off verify step are all already established doctrine — but execution against the *desert family's* remaining ~26+ Wave-C species (plus the never-scoped Alpha Animals donor) is not finished, which is exactly why 66 identical-label twins are live right now.
