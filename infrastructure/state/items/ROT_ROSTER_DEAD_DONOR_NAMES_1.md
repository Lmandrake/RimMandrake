# ROT_ROSTER_DEAD_DONOR_NAMES_1 — the Rot roster names a retired donor's species

## what is actually true — MEASURED by BENCH 2026-09-20

`design/Jawa/worldbuilding/biomes/rosters/the_rot.json` lists **28** admitted
fauna. `RUT_TheRot.xml`'s `<wildAnimals>` wires **10**. A reconciliation agent
reported that as *"18 ruled fauna unwired — the live def is short."*

🔴 **That reading is wrong, and acting on it would have been a regression.**
Of the 20 roster names not in the table:

| | |
|---|---:|
| `BMT_*` — **Biomes! Caverns** donor defs | **17** |
| non-donor (`ShiroTrap`, `AA_AnimaColossus`, `MA_Sporemole`) | 3 |

And **`biomesteam.biomescaverns` is NOT in the active mod list** — 0 hits across
the 621 active ids in `infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`
(parsed, not scanned). That mod was deliberately retired; `CAVERNS_PARITY_BUILD_1`
closed on exactly that, having made the Lantern Deeps donor-free of it.

⇒ **Those 17 names can never spawn.** The def is not short — **the roster is
stale.** Wiring them in would re-introduce a dependency on a mod we just spent a
build removing.

Three of the 20 are already accounted for and are NOT gaps:

- `BMT_FungalWeevil` → ported, ships as **`RSW_FungalWeevil`**, wired (line 131).
- `BMT_FungalMantis` → ported, ships as **`RSW_FungalMantis`**, wired (line 138).
- `BMT_BovineBeetle` → **deliberately cut** from the Rot; it became the Lantern
  Deeps' Grabber (`ROT_FLORA_FAUNA_VERDICTS_1` TASK 2).

🔑 Those two ports are the *pattern for the remedy*: a wanted donor species gets
re-authored as our own `RSW_`/`RUT_` def, not wired under its dead donor name.

## spec

For each of the **14 remaining `BMT_` names** (the 17 minus the two ported and
the one cut), rule one of:

- **PORT** — re-author as our own def, the way FungalWeevil and FungalMantis
  were. This is donor-retirement work and is the reason the species was wanted.
- **DROP** — remove the row from the roster JSON. Git is the provenance.

Then reconcile: the roster and `<wildAnimals>` must agree, with no `BMT_` name
left in either.

**Separately, settle the 3 non-donor names** — `ShiroTrap`, `AA_AnimaColossus`,
`MA_Sporemole`. None resolves in `src/`, so each is a donor def; Alpha Animals
(`sarg.alphaanimals`) IS active, so `AA_AnimaColossus` may be legitimately
wirable and simply missing. Check each against the active list before ruling.

⛔ **Do not bulk-wire anything to close the 28-vs-10 gap.** The gap is the
correct shape of a retirement that got half-done; closing it by number is how the
donor comes back.

## Watch out

- ⚠️ This is the same trap as `patched-collisions` and the desert donor census:
  **a name-based count reads as a coverage gap when it is really a rename or a
  retirement.** Compare against the active mod list before calling anything
  missing.
- ⚠️ The roster was authored 2026-09-09 (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`),
  BEFORE the caverns retirement. Check other biomes' rosters for the same
  staleness — `RUT_Miasma`, `RUT_TheForge`, `RUT_FeverWood` and `RUT_Greentide`
  all still carry `biomesteam.biomescaverns` entries per
  `infrastructure/state/facts/biome_rosters.md`.
- 🔴 Do not "fix" this by re-adding Biomes! Caverns to the mod list.

## verify

Zero `BMT_` names remain in `rosters/the_rot.json` and in `RUT_TheRot.xml`; every
species the roster still admits resolves against the active mod list; a post-load
def dump confirms the wired kinds actually spawn.

## criteria

The Rot's roster names only species that can exist in the shipped game.

## resolution — FOUNDRY, closed 2026-09-21

Most of the work was done and pushed in an earlier sitting under this same
item (`6af64f818`, "Reconcile the Rot and the Forge rosters"), which
re-measured the roster from scratch (23 fauna, not the briefed 28 — 5 rows
had already been cut same-day by `c2428fb6f`) and resolved 13 of the 14
open `BMT_`/non-donor names:

| dead/bare name | ruling | reasoning |
|---|---|---|
| `ShiroTrap` | PORT (already done) | `RSW_ShiroTrap` already existed (`MLIE_FAUNA_ABSORPTION_1` Wave C); wired |
| `BMT_ColonyPustuleHornetQueen` | PORT (already done) | `RSW_ColonyPustuleHornetQueen` already existed; wired |
| `BMT_PustuleHornetQueen` | PORT (already done) | `RSW_PustuleHornetQueen` already existed; wired |
| `BMT_PustuleHornetSpawned` | PORT (already done) | `RSW_PustuleHornetSpawned` already existed; wired |
| `BMT_ColonyPustuleHornet` | PORT (already done) | `RSW_ColonyPustuleHornet` already existed; wired |
| `BMT_PustuleHornet` | PORT (already done) | `RSW_PustuleHornet` already existed; wired |
| `BMT_SmogMoth` | PORT (already done) | `RSW_SmogMoth` already existed; wired |
| `BMT_Thrumbungus` | PORT (already done) | `RSW_Thrumbungus` already existed; wired |
| `BMT_Yooka` | PORT (already done) | `RSW_Yooka` already existed; wired |
| `AA_AnimaColossus` | wire as-is | already an active `sarg.alphaanimals` donor def, never needed porting, just never wired |
| `BMT_GlowBat` | DROP (confirmed) | owner ruling 2026-09-10 sitting, "CUT — all flying bats" (`decisions_propagated.json`) |
| `BMT_BovineBeetle` | DROP (confirmed) | already moved to the Lantern Deeps as `RSW_BovineBeetle` (`ROT_FLORA_FAUNA_VERDICTS_1` TASK 2); roster row was stale |

That left exactly **one** genuine open call, which this closing pass made:

| name | ruling | reasoning |
|---|---|---|
| `MA_Sporemole` | **DROP** | Donor `veterano.mythicages.megafaunabestiary` (Mythic Ages: Megafauna Bestiary) is not in the active mod list and no `RSW_`/`RUT_` port exists. Web search on the donor mod found only a generic mechanic (a burrow-defending manhunter, part of a hunt/tame/butcher resource-cycle bestiary) with nothing distinct from fauna the Rot already has, and it is natively a Boreal/Cold/Temperate-biome animal (`animal_census.csv`), not a fungal-rot-swamp species. Every in-repo record of it is a bulk-census "keep" tag with no authored flavor or design-sheet backing — unlike `RSW_FungalWeevil`/`RSW_FungalMantis`, which had explicit `the_rot.md` §7b sheet language calling for them by name. Porting would mean inventing a whole new creature from a name and a body-size number, which this hygiene item's own instructions rule out (`DROP is the cheaper, safer, default call... when its mechanic can't be determined`). Removed from `fauna`, recorded in `evictions`. |

Also fixed on sight (correctness outranks seat ownership, no ticket needed):
`RUT_TheRot.xml`'s own header comment still claimed *"wildAnimals is
UNCHANGED (still donor `BMT_`/`AA_` defNames, MayRequire'd)"* — true when
written (`FUNGALFOREST_RAID_MERGE_1`), false since `6af64f818` rewired that
section. Corrected in place, one line.

**Verified at close**: `the_rot.json`'s `fauna` array has 20 entries, zero
`BMT_` names, zero `pending-owner-decision` actions; `RUT_TheRot.xml`'s
`<wildAnimals>` has zero `BMT_` tags (7 remaining substring hits in the file
are all historical prose in comments, not live defNames); every one of the
20 fauna defs resolves against an active packageId in
`ModsConfig_full_plus_longhunger_2026-09-19.xml` (parsed with
`xml.etree.ElementTree`, not grepped): `sarg.alphaanimals`,
`mandrake.rsw.swbestiary`, `mlie.starwarsanimalcollection` all active;
`biomesteam.biomescaverns` and `veterano.mythicages.megafaunabestiary`
both confirmed absent. `RUT_TheRot.xml` re-validated clean with
`validate_patch.py` against the live 621-mod snapshot (`--defs` Data/Mods/
Workshop on the Steam install): 0 errors, 0 warnings (4 pre-existing,
unrelated WARNs about missing art-override mod folders).

**"Watch out" biomes, checked not fixed**: `RUT_TheForge` was already
reconciled by the separate, now-closed `FORGE_ROSTER_UNRECONCILED_BMT_1`
(`6af64f818`). The other three — `the_miasma.json` (3 live `BMT_` fauna
rows: `BMT_CrestedDragon`, `BMT_AaroxisDendoria`, `BMT_PodWorm`),
`the_fever_wood.json` (3: `BMT_GlowSlug`, `BMT_JewelBeetle`, `BMT_AcidSlug`)
and `the_greentide.json` (1: `BMT_Diggerpede`) — were confirmed to carry the
identical live defect (parsed, not grepped; zero of the 7 wired under their
`BMT_` name in the corresponding XML either). Not fixed here — out of this
item's declared scope. Follow-on item filed:
`MIASMA_FEVERWOOD_GREENTIDE_BMT_1`.

Full commit-level detail on the bulk of the work (the 12 rows above) is in
`Transient/roster_reconciliation_2026-09-21.md`.
