# DONOR_DEFS_PORT_TO_OURS_1 — everything becomes ours

## the ruling

Owner, 2026-09-20, verbatim: *"Everything should be moved t our own thing defs."*

Said while approving the desert graphics, immediately after seeing that the
desert family's 109-species roster is **3 ours to 99 donor**. It is the general
form of what `CAVERNS_PARITY_BUILD_1` already did for one donor in one biome.

## the scale, MEASURED 2026-09-20

Every owned `RUT_*` BiomeDef's `<wildPlants>`/`<wildAnimals>`, parsed by each
entry's `MayRequire` packageId. Full table and method:
`infrastructure/state/facts/biome_rosters.md`.

| entries | donor |
|---:|---|
| **160** | `mlie.starwarsanimalcollection` |
| **102** | `sarg.alphaanimals` |
| 21 | `neronix17.outerrim.droiddepot` |
| 8 | `vanillaexpanded.vgeneticse` |
| 7 | `oskarpotocki.vfe.insectoid2` |
| 6 | `sarg.alphabiomes` |
| 4 | `who.vfee.isopodageneline` |
| 3 | `sarg.alphamemes` |
| 2 each | `mlie.horrors`, `biomesteam.biomescaverns` |
| 1 each | `lingluo.cockroach`, `regrowth.botr.core` |

🔑 **Two mods carry 262 of ~330 borrowed roster entries.** Any plan that is not
mostly about those two is aimed at the tail. `RUT_TheRot` is the only biome where
we already own more than we borrow (21 vs 8) — it is the benchmark for what
"done" looks like.

## the pattern to copy — it already exists twice

- **`RSW_FungalWeevil`** and **`RSW_FungalMantis`** — ported out of
  `BMT_FungalWeevil`/`BMT_FungalMantis`, wired into `RUT_TheRot.xml` under our
  own defNames (lines 131, 138). This is the shape: re-author as ours, wire the
  new name, drop the donor name from the roster.
- **`CAVERNS_PARITY_BUILD_1`** — the whole-biome version, for `Biomes! Caverns`.
  It closed having made the Lantern Deeps generate from owned defs only, verified
  with the donor ABSENT from the mod list. Read it before planning this.

## naming

Per `design/NAMING_SCHEME_PLAN.md`, three tiers: **RimMandrake** (any RimWorld
game) / **RimStarWars** (any Star Wars scenario) / **RimUtinni** (this campaign),
prefixes `RM_`/`RSW_`/`RUT_`. A ported creature is almost always `RSW_`. ⚠️ The
rename gate is long closed — `NAMING_SCHEME_EXECUTION_1` ended 2026-08-31 — so a
rename here is owed work, never something to defer to it.

🔑 **Porting and renaming are separate jobs.** A ported def keeps whatever name
it had unless `NONCANON_BEAST_RENAME_1` says otherwise; do not silently
re-christen things while porting, or neither ruling can be checked.

## spec

⛔ **Do not start porting 300 defs.** This needs a plan and an owner sitting on
the order first. What is owed before any porting:

1. **A census of what porting actually means per donor.** A creature is a
   ThingDef + PawnKindDef + art + sometimes comps and a BodyDef. Some donors are
   a straight copy with a rename; some carry C# that would have to be reimplemented
   or dropped. Grade each donor's entries by that cost.
2. **A keep/cut pass first.** Porting a species we would have cut is pure waste —
   and the desert sheet shows the roster was never keep/cut ruled at all. Cutting
   is cheaper than porting, so the cut list comes first.
3. **Order by the table above**, not by biome.
4. **A per-donor retirement test**, the `CAVERNS_PARITY_BUILD_1` shape: the donor
   ABSENT from `ModsConfig.xml` and the biome still generating.

## Watch out

- 🔴 **Never infer a def's owner from its defName prefix.** `mlie.starwarsanimalcollection`
  ships BARE defNames (`Bantha`, `Kreetle`, `Scavrat`, `Shyrack`, `Gorg`,
  `Gutkurr`, `Jamel`, `Rat`), so a prefix rule buckets the single largest donor as
  vanilla Core. A census did exactly that this session. Read `MayRequire`.
- ⚠️ **19 desert-family entries carry NO `MayRequire` guard at all** (`AB_HardyGrass`,
  `AB_Aaklac`, `AB_DessertTree`, four `RG_Plant_*`, and others). Those break on
  the donor's removal with no graceful degrade — they are the first things this
  ruling fixes, not the last.
- ⚠️ A roster can name a species from a donor **already retired** — the Rot names
  17 `BMT_` defs from a mod absent from the 621-mod list
  (`ROT_ROSTER_DEAD_DONOR_NAMES_1`). Those need dropping, not porting.
- ⛔ Vanilla Core and DLC defs (`Ludeon.*`) are NOT donors. Leave them.
- 🔴 A texture binds by `texPath`, not defName — a ported def with the donor's
  old texPath renders the donor's art or nothing.

## verify

Per donor: it is absent from `ModsConfig.xml` and every biome that used it still
generates, with its roster intact under our own defNames. Confirmed from a
post-load def dump, never from the patch files.

## criteria

The shipped game's biome rosters name our defs. Removing any third-party content
mod changes nothing a player can see.

## FOUNDRY, 2026-09-24: folding in a stray 2026-09-20 census that never landed here

Commit `78b63a97` (2026-09-20, Opus) wrote `Transient/donor_port_twin_census.md`
citing this item in its message but never touched this file — found this pass
while checking why the queue flagged this item's prose as possibly stale. The
work is real and worth keeping; folding it in rather than leaving it to rot in
`Transient/`.

**Scope**: this is a twin-duplication census of the desert family's 109-row roster
only (`DESERT_FAMILY_PORT_EXECUTION_1`'s frozen sheet), not the full-roster
donor-cost census this item's own spec step 1 asks for — it answers "how bad is
the current live-duplication problem," not "what does porting each donor's
entries actually cost." Both are still owed.

**MEASURED** (against the 618-mod dump, 2026-09-20T20:14:27Z, fingerprint-matched
to the live `ModsConfig.xml` at capture time): of the desert sheet's 75
structurally-twin-eligible rows (bare donor-style names), **66 are live
identical-label twins** — both the donor ThingDef and our `RSW_` port exist,
same label, simultaneously. 7 rows are genuinely unported yet (`Rat`,
`Terrorworm`, `Plant_Brambles`, `Plant_Bush`, `Plant_HealrootWild`,
`Plant_Ripthorn`, `Plant_ShrubLow`). 2 are near-miss twins failing only on
pluralization (`Shaak`/`shaaks`, `Skalder`/`skalders`). All from
`mlie.starwarsanimalcollection`.

**Not a defect** — confirmed against `MLIE_FAUNA_ABSORPTION_1` (closed, moved to
`items/closed/`), whose own design keeps the donor active through every wave
and only retires it after a full donor-off cold load. That item's last logged
pass (2026-09-18) had 26 of 91 Wave-C species still remaining — so the 66 live
twins are exactly that in-progress state, not new damage.

**The one real gap this surfaced**: `sarg.alphaanimals` (102 roster entries,
the SECOND-largest donor named in this item's own table) has **no retirement
plan at all** — no `ALPHA_ANIMALS_*` item exists anywhere in `items/` or
`items/closed/`. `MLIE_FAUNA_ABSORPTION_1` and `BMT_FAUNA_ABSORPTION_1` cover
the other two large donors; Alpha Animals' 102 entries have never been scoped
as a wave. That is real unfiled work, not yet filed as its own item here —
whoever plans the porting order (spec step 1/3) should treat it as a third
wave alongside the other two, not a tail item.

Files: `Transient/donor_port_twin_census.md` (the full method + per-donor
active-state table, kept as-is; this section is the summary, not a
duplicate).

Still `proposed` — the census does not authorize porting; spec step 1's
full per-donor cost grading and step 2's keep/cut pass are both still
unstarted, and `⛔ Do not start porting 300 defs` stands.
