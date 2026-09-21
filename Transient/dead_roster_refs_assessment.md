# Dead roster refs — decision-ready assessment

Assessment only. No def, roster or biome table was changed by this pass.
Source items: `BIOME_ROSTER_DEAD_SPECIES_REFS_1`, `ROT_ROSTER_DEAD_DONOR_NAMES_1`.
Both items had already had significant work land on them (same day, by other
agents/BENCH) between when they were filed and when this assessment ran —
several rows below report **RESOLVED**, not a live defect.

## Active mod list used

`infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`
(621 ids), parsed via `ET.parse(p).find("activeMods")` — the same reference
both source items measured against.

⚠️ **The LIVE `ModsConfig.xml`** (`/mnt/c/.../Config/ModsConfig.xml`, mtime
2026-09-20 18:35) currently holds only **19 mods** — a minimal bridge-test
list, not the campaign list (RimWorld is running under another window's
bridge hold right now). It is not usable as "the active list" for this
assessment; using it would have manufactured 600 false "dead" rows. The
621-id snapshot is the correct instrument, consistent with both items' own
methodology, but it is dated 2026-09-19 and is stale by one day relative to
at least one mod built today (see AshkarrFlora note below) — flagged
UNMEASURED where that staleness matters.

---

## PART 1 — BIOME_ROSTER_DEAD_SPECIES_REFS_1 (23 original dead entries)

**Current status: 0 of the 23 remain dead.** Both sub-problems were resolved
by other work landing on the same item earlier today (commits `5a0b0f5c0`,
then `66649b5a0`; GiantLeaf resolved by whatever landed `RUT_GiantLeaf`).
Re-measured directly against the live def files (regex-parsed
`<wildAnimals>`/`<wildPlants>` blocks, MayRequire attr checked against the
621-id list) rather than trusting the item's own prose:

| biome def | dead entry | donor mod | donor active? | commonality (rank) | do we own an equivalent? | recommendation |
|---|---|---|---|---|---|---|
| `RUT_ExtremeDesert`/`RUT_Desert`/`RUT_AridShrubland` | 21 × droid rows (`neronix17.outerrim.droiddepot`) | `neronix17.outerrim.droiddepot` | inactive | was 0.6/0.4/0.1×4/0.08×2/0.05×2/0.02 across the 3 tables | **YES** — `RSW_DW_OuterRim_*Droid` (Droidworks, `mandrake.rsw.droidworks`, ACTIVE) | **RESOLVED, then SUPERSEDED** — repointed to Droidworks at `5a0b0f5c0` (2026-09-20 09:37), then all 15 Fall-Line-origin rows (incl. these 7×3) were pulled OUT of ambient `wildAnimals` entirely at `66649b5a0` (2026-09-20 15:10) on an owner ruling: droids/vermin here are ARRIVALS (wreckage content), not ambient biome fauna. Now tracked as new work item `FALL_LINE_ARRIVAL_MECHANISM_1`, filed to BENCH — not a "dead ref" any more, a design mechanism not yet built. |
| `RUT_Greentide` | `BMT_GiantLeaf` | `biomesteam.biomescaverns` | inactive | was 1.0, rank 4/11 | **YES** — `RUT_GiantLeaf` (RimUtinni itself) | **RESOLVED** — now wired as `RUT_GiantLeaf`, no `MayRequire` (owned outright, not donor-guarded). Confirmed rank 4/11 in the live table, weight unchanged. |
| `RUT_FeverWood` | `BMT_GiantLeaf` | `biomesteam.biomescaverns` | inactive | was 0.8, rank 3/7 | **YES** — `RUT_GiantLeaf` | **RESOLVED** — same, confirmed rank 3/7. |

### Per-biome effective dead weight — Part 1

- **`RUT_ExtremeDesert` / `RUT_Desert` / `RUT_AridShrubland` wildAnimals: 0% dead now** (was ~15 entries' worth of ambient droid/vermin weight — the item's own "effective fauna is 16, not 23" framing no longer applies; those 7 rows per biome are gone from ambient tables entirely, correctly, pending the Fall-Line arrival mechanism).
- **`RUT_Greentide` wildPlants: 0% dead** (was 1.0/9.6 ≈ 10.4% of table weight dead; now live, unguarded).
- **`RUT_FeverWood` wildPlants: 0% dead** (was 0.8/~5.4 ≈ 14.8%; now live, unguarded).

### Newly found while re-measuring (not on the original 23, not a donor-retirement case)

Two **different** dead entries turned up in the same live-parse sweep, both guarded by our **own** brand-new mod, not a retired donor:

| biome | entry | MayRequire | commonality (rank) |
|---|---|---|---|
| `RUT_Desert` wildPlants | `RUT_Staggerseed` | `mandrake.rut.ashkarrflora` | 0.1, rank 8/9 |
| `RUT_AridShrubland` wildPlants | `RUT_Fuzz` | `mandrake.rut.ashkarrflora` | **0.9, rank 1/10 — the heaviest row in the table** |

`mandrake.rut.ashkarrflora` (`RimUtinni: Ash'karr Flora`, `src/RimUtinni/AshkarrFlora/`)
is a real, built mod — its `RUT_Staggerseed` def was committed **today at
17:21** (`f5f8b4abf DESERT_STAGGERSEED_BUILD_1`), **after** the 621-id
snapshot was captured (2026-09-19 03:58). It **is** present in the live
19-mod minimal test list. **UNMEASURED: whether it is in the current full
campaign list** — no full snapshot post-dates its creation, and the live
`ModsConfig.xml` right now is the unrelated 19-mod minimal list. This is not
a port/drop/reactivate decision like the rest of this doc — it reads as "our
own new mod not yet flipped on," not a donor retirement. Worth a five-second
check next time the full list is live: if it's missing, `RUT_Fuzz` is
currently the single heaviest dead row found anywhere in this sweep.

---

## PART 2 — ROT_ROSTER_DEAD_DONOR_NAMES_1

The roster JSON (`design/Jawa/worldbuilding/biomes/rosters/the_rot.json`) has
also moved since the item was filed — it now admits **23** fauna (not 28),
of which **10** are wired in `RUT_TheRot.xml`'s `<wildAnimals>` (unchanged
from the item's own count). `biomesteam.biomescaverns` re-confirmed **NOT**
in the 621-id active list (0 hits).

Roster weight accounting (commonality-sum, not row-count — a "gap" in rows
overstates or understates depending which rows are heavy):

- Roster admits **8.25** total commonality-weight across 23 rows.
- **2.95** (36%) is actually wired and spawns.
- **5.30** (64%) is admitted-but-absent from the live table. Of that gap:
  - **4.20** (79% of the gap, 51% of the whole roster) is species **we
    already own** under an `RSW_` name and simply never wired — the cheap
    win, zero new art or defs needed.
  - **0.60** (11% of the gap) is two rows that are **already correctly
    resolved elsewhere** but left stale in the roster JSON (see table).
  - **0.50** (9% of the gap) is one genuine open build-or-drop call
    (`MA_Sporemole`).

| dead entry | donor mod | donor active? | commonality (rank in 23-row roster) | do we own an equivalent? | recommendation |
|---|---|---|---|---|---|
| `BMT_GlowBat` | `biomesteam.biomescaverns` | inactive | 0.4 (rank 11/23) | not found in `BMT_FAUNA_ABSORPTION_1`'s port (`RSW_BiomesTeamPort_Races.xml` has no GlowBat entry; no GlowBat sound/texture folder under `BMT_Caverns/`) | **DROP the roster row.** The owner already ruled this CUT: `design/Jawa/worldbuilding/review/round2/decisions_propagated.json` → `fauna:the_rot:BMT_GlowBat` = `"decision": "out"`, note *"CUT — all flying bats (owner; this is the 'violescent/bioluminescent bat') (sitting ruling 2026-09-10)"*. The roster JSON simply never picked up that ruling. No new work, just delete the row. |
| `BMT_BovineBeetle` | `biomesteam.biomescaverns` | inactive | 0.2 (rank 20/23) | **YES** — `RSW_BovineBeetle` ("grabber", MEASURED, active via `mandrake.rsw.swbestiary`) | **DROP the roster row.** Already deliberately moved to `RUT_LanternDeeps.xml` (`RSW_BovineBeetle` wired there at 0.1, confirmed live) per `ROT_FLORA_FAUNA_VERDICTS_1` TASK 2, done 2026-09-19. The def-level fix already happened; only the roster JSON is stale. |
| `BMT_ColonyPustuleHornetQueen` | `biomesteam.biomescaverns` | inactive | 0.2 (rank 21/23) | **YES** — `RSW_ColonyPustuleHornetQueen` (MEASURED via source, `RSW_BiomesTeamPort_Races.xml`) | **PORT-already-done → WIRE.** Rename row to `RSW_ColonyPustuleHornetQueen`, add to `RUT_TheRot.xml` `<wildAnimals>`, no `MayRequire` needed (ours). |
| `BMT_PustuleHornetQueen` | `biomesteam.biomescaverns` | inactive | 0.3 (rank 14/23) | **YES** — `RSW_PustuleHornetQueen` | **WIRE** (same as above). |
| `BMT_PustuleHornetSpawned` | `biomesteam.biomescaverns` | inactive | 0.2 (rank 22/23) | **YES** — `RSW_PustuleHornetSpawned` | **WIRE.** |
| `BMT_ColonyPustuleHornet` | `biomesteam.biomescaverns` | inactive | 0.5 (rank 4/23) | **YES** — `RSW_ColonyPustuleHornet` | **WIRE** — heaviest of the pustule-hornet family. |
| `BMT_PustuleHornet` | `biomesteam.biomescaverns` | inactive | 0.5 (rank 5/23) | **YES** — `RSW_PustuleHornet` | **WIRE.** |
| `BMT_SmogMoth` | `biomesteam.biomescaverns` | inactive | 0.5 (rank 6/23) | **YES** — `RSW_SmogMoth` (has its own flying-animation frame prefix already in the port) | **WIRE.** |
| `BMT_Thrumbungus` | `biomesteam.biomescaverns` | inactive | 0.5 (rank 7/23) | **YES** — `RSW_Thrumbungus` | **WIRE.** |
| `BMT_Yooka` | `biomesteam.biomescaverns` | inactive | 0.5 (rank 8/23) | **YES** — `RSW_Yooka` | **WIRE.** |
| `ShiroTrap` (non-donor-prefixed) | n/a — already ours | n/a | 0.5 (rank 1/23, tied heaviest) | **YES** — `RSW_ShiroTrap` (MEASURED: BodyDef/PawnKindDef/ThingDef "shiro-trap", RimMandrake: SW — Bestiary, ACTIVE) | **WIRE** as `RSW_ShiroTrap`. Not a donor-dead ref at all — the roster's bare name just needs its `RSW_` prefix and a row in `<wildAnimals>`. Already wired in `RUT_Greentide.xml`, so this would be a second biome carrying it — confirm that's intended (cross-biome sharing) before wiring, not a blocker. |
| `AA_AnimaColossus` | `sarg.alphaanimals` | **ACTIVE** | 0.5 (rank 3/23, tied heaviest) | uses donor name directly (PawnKindDef + ThingDef "anima colossus", MEASURED) | **WIRE directly** — donor mod is active, defName is correct as-is, this was simply never added to `<wildAnimals>`. Zero build work. |
| `MA_Sporemole` | `veterano.mythicages.megafaunabestiary` (Mythic Ages: Megafauna Bestiary) | **inactive** (0 hits in 621-id list) | 0.5 (rank 9/23, tied heaviest) | **NO** — no `RSW_`/`RUT_` port found anywhere in `src/` | **OPEN CALL — PORT or DROP.** This is the one row in the Rot list that is genuine new work either way: `veterano.mythicages.megafaunabestiary` was never absorbed the way Biomes! Caverns was. `homeless:MA_Sporemole` in `decisions_propagated.json` records `"decision": "move"` to The Rot (2026-09-10), so the intent is real, but nothing has built it. Reactivating the donor mod is the third fate and is explicitly against standing practice (owner: retired donors don't come back) — so this is PORT-or-DROP, not reactivate. |

### Per-biome effective dead weight — Part 2

**`RUT_TheRot`: 64% of the roster's admitted weight is currently absent from
the live table**, but that number overstates the actual work owed — 79% of
the missing weight (51% of the whole roster) is species we already own under
an `RSW_` name and never wired (pure reconciliation, no new content), 11% of
the gap is two rows that are already correctly resolved elsewhere and just
need deleting from the stale JSON, and only 9% of the gap (`MA_Sporemole`,
commonality 0.5) is an actual open build-or-drop decision.

### The other 4 biomes the item flagged as "check for the same staleness"

The item's own "Watch out" section names `RUT_Miasma`, `RUT_TheForge`,
`RUT_FeverWood`, `RUT_Greentide` as rosters authored before the caverns
retirement. Re-measured: **their live `<wildAnimals>`/`<wildPlants>` tables
carry ZERO wired dead `MayRequire` refs** (confirmed in Part 1's sweep — this
is not the same defect class as the original 23). But their **roster JSONs**
still admit unreconciled `BMT_` names that were never wired at all:
`the_miasma.json` (10 `BMT_` names, incl. a second `BMT_GlowBat` — same
already-ruled cut applies), `the_forge.json` (27 `BMT_` names — the largest
by far), `the_fever_wood.json` (9), `the_greentide.json` (3). None of these
are "dead refs that never spawn" in the sense of the two items assessed here
— they are unreconciled design-roster rows with no live counterpart at all,
same shape as most of the Rot's gap above. **Out of scope for this pass**
(neither item asks for a per-row ruling on 49 more names); flagging so the
next roster-reconciliation pass doesn't have to rediscover it, and because
`RUT_TheForge`'s 27 is large enough that it's probably worth its own item
rather than folding into this one.

---

## UNMEASURED

- Whether `mandrake.rut.ashkarrflora` is in the **current, live** full
  campaign mod list (only a 19-mod minimal test list is live right now; the
  most recent full snapshot pre-dates the mod's own commit by ~14 hours).
- Whether `RSW_ShiroTrap` being wired into both `RUT_Greentide` and
  `RUT_TheRot` is an intended cross-biome share or an oversight — not
  determinable from source alone, flagged as a design call.
- The exact commonality/rank picture for the 4 "also flagged" biomes'
  unreconciled `BMT_` roster rows (Miasma/Forge/FeverWood/Greentide) — not
  computed, out of this pass's scope (see above).

## Total dead entries confirmed (this pass's core scope)

- Part 1 (`BIOME_ROSTER_DEAD_SPECIES_REFS_1`'s original 23): **0 remain
  dead** — all resolved by other work today.
- Part 1, newly found: **2** dead entries (`RUT_Staggerseed`, `RUT_Fuzz`),
  different root cause (own new mod pending activation, not donor
  retirement).
- Part 2 (`ROT_ROSTER_DEAD_DONOR_NAMES_1`'s 14 `BMT_` + 3 non-donor rows):
  **12 confirmed dead-or-stale rows** ruled here (9 `BMT_` port-and-wire, 2
  already-resolved-but-stale, 1 genuine open port/drop call), plus **2**
  non-donor rows (`ShiroTrap`, `AA_AnimaColossus`) that are wire-only, not
  donor-dead at all.
