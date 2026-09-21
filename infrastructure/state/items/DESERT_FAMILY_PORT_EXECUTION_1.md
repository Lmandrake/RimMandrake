# DESERT_FAMILY_PORT_EXECUTION_1 — port the whole desert family to our own defs and art

## the ruling

Owner, 2026-09-20, verbatim: *"Yes. All of the desert sheet should be keep but
replace with our own version of creature and art. Port. All of them. Now."*

Every one of the desert sheet's **109 rows** is `replace`. Nothing is cut. The
decisions file is frozen and records that the ruling was blanket and uniform —
his instruction, not a default.

This satisfies `DONOR_DEFS_PORT_TO_OURS_1`'s "keep/cut pass first" precondition
**for the desert family only**. The other ~190 species still need their own pass.

## the work, RE-MEASURED 2026-09-20 — the defs are 78% DONE, the ART is not

🔴 **The original version of this section said "~105 species to author". That was
wrong and would have sent a wave of agents to re-author 85 creatures that already
exist.** Corrected here against the live def dump
(`defs.sqlite`, mods=618/a48bc71544df1a7e, captured 2026-09-20T20:14:27Z) and the
SWBestiary authoring source, row by row across all 109 decision rows.

### defs — MEASURED 85 of 109 already ported and live

| state | rows | what it means |
|---|---:|---|
| **LIVE as `RSW_`** | **68** | canon-named rows; `RSW_<name>` ThingDef present in the dump |
| **Alpha Animals, ported under drafted names** | **13** | `AA_Cactipine`→`RSW_Spinerat`, `AA_SandSquid`→`RSW_Sandmaw`, `AA_Terramorph`→`RSW_Ferroclaw`, … all 13 verified live. ⚠️ A `RSW_<donorName>` prefix test **cannot find these** — they were deliberately renamed per `NONCANON_BEAST_RENAME_1`. The mapping is in the `<!-- Alpha Animals AA_X -> RSW_Y -->` comments in `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml` |
| **already ours** | **4** | 3 SWBestiary (`RSW_ImperialToad`, `RSW_Jellypot`, `RSW_MossBeetle`) + `JOE_Landopus`, which MEASURED as already living in RimUtinni Patches |
| **DONE** | **85** | |
| unblocked, still to author | **11** | see below |
| **needs the owner before authoring** | **12** | 7 Droid Depot + 5 vanilla/Biotech, see below |
| out of scope | **1** | `AB_GiantStikehr` — cut from the Extreme Desert as misplaced the same day. ⛔ Do not re-add |

### 🔴 art — MEASURED 3 of 84, and this is the actual remaining wave

Parsed `<texPath>` out of every ported row's `ThingDef` **and `PawnKindDef`** in the
SWBestiary source (animal art hangs off `PawnKindDef.lifeStages`, not the ThingDef —
a ThingDef-only scan reports "no texPath" for 79 of 84 and is the wrong instrument):

- **3** rows carry our own art (`RSW_Plant_Chakroot_Wild`, `RSW_Plant_HubbaGourd_Wild`, `RSW_Plant_Bloddle`)
- **81** still point at donor texture paths — `swanimals/Bantha/BanthaW_j`, `Things/Pawn/Animal/AA_Cactipine/AA_Cactipine`, `swplants/Nysillin`, …

⇒ The owner ruled *"replace with our own version of creature **and art**"*. The **def**
half is 78% done; the **art** half is ~4% done. **81 renders is what this item actually
owes**, and the def port is nearly finished.

⚠️ **UNMEASURED from the def dump:** the dump does not carry `texPath` for these records
(79 of 84 came back empty), so the art figure above is measured from the **authoring
source**, not the loaded game. It is evidence about what we wrote, which is the right
question here — but do not quote it as a statement about the running game.

🔑 **Before filing any art job, search for art already generated AND already ruled on** —
`infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl`, and any
`Transient/*.decisions.json` review sheet. Standing rule (`CLAUDE.md`); it has already
caught three plants one step from a wasted regen.

### the 11 unblocked rows still to author

`AA_BoulderMit` (Alpha Animals) · `Terrorworm` (Horrors) · `VFEI2_Fuelmite` (VFE
Insectoids 2) · `AB_Aaklac`, `AB_DessertTree`, `AB_HardyGrass` (Alpha Biomes) ·
`Plant_Brambles`, `RG_Plant_AridGrass`, `RG_Plant_CreepStern`, `RG_Plant_CrimsonCushion`,
`RG_Plant_Dervish` (ReGrowth 2)

### the 12 rows that need him first

- **7 Droid Depot droids** (`OuterRim_DUMDroid`, `DestroyerDroid`, `FX7Droid`, `GNKDroid`,
  `MSEDroid`, `MuckrakerDroid`, `SalvageAssistDroid`) — `neronix17.outerrim.droiddepot` is
  **NOT in the active mod list**, so they cannot be read from a live game. Port from the
  donor's files on disk, or do they not come back at all?
- **5 vanilla/Biotech rows** (`Rat`, `Plant_Bush`, `Plant_HealrootWild`, `Plant_ShrubLow`
  from Core; `Plant_Ripthorn` from Biotech) — replacing vanilla is a bigger departure than
  porting a donor.

## 🔑 the precedent — copy it, do not invent one

`BMT_FAUNA_ABSORPTION_1` already did exactly this operation for three Biomes!
Team mods: **68 defNames ported to `RSW_`**, landed at
`src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/` (Bodies, SoundDefs, Support,
ThingDefs_Items, ThingDefs_Races). Read that folder's header comment before
touching anything — it is the operating manual and it records what went wrong.

What it establishes:

- **Reference closure is the job.** Port the species *and* every def pulled in by
  reference — bodies, eggs, leather, sounds, hediffs, damage types — "so nothing
  dangles". A ported creature with a dangling BodyDef is a broken creature.
- **Drop donor-framework comps.** Any `modExtension`/comp whose C# lives in a
  retiring or inactive assembly comes OUT; the creature keeps its stats, body and
  behaviour-free form. Do not reimplement donor AI in this pass.
- **Repath texPaths.** The donor's texPath does not follow the def. A texture
  binds by `texPath`, not defName.

🔴 **ONE DELIBERATE DEPARTURE FROM THAT PRECEDENT.** `BMT_FAUNA_ABSORPTION_1`
copied the donor's textures verbatim. **This ruling does not** — he said *"our own
version of creature and art"*. So every ported species needs a NEW render, filed
through `fill_queue.py` only. Donor art may stand in only as a temporary
placeholder, and only where it is loudly commented as such.

## naming

- **Canon keeps its name.** Bantha, Massiff, Eopie, Ronto, Shyrack, Krayt dragon,
  Womp rat, Mynock, Gizka, Varactyl, Nuna, Lothcat and the rest are the point of
  the setting. Grade against `design/RimStarWars/canon_references/` (137 entries)
  via the `rimworld-canon-references` skill.
- **Non-canon gets a pseudo-Star-Wars name** — `NONCANON_BEAST_RENAME_1`.
  ⚠️ That item's own design is *"agent drafts, owner reacts"*. **Assumption this
  item proceeds under:** names are DRAFTED now so the port is not blocked, and
  surfaced to him in a batch for reaction. A drafted name is not a ruled name —
  mark them so, and never let a drafted name reach a canon creature.

## sequencing

1. **Defs first** (offline, unblocked) — author the defs with reference closure.
2. **Art jobs** as each batch's names settle — the art prompt needs the ruled
   name and description, so naming gates art, not defs.
3. **Land art** as the daemon clears it; review by eye before wiring, the way the
   Rot wave did — 4 of 61 renders there were bad and only an eye caught them.
4. **Rewire the biome tables** last: donor entry out, our defName in, and the
   `MayRequire` **re-pointed at the mod that now owns the def** — never dropped.
   🔴 "It is ours now" is not "it is in the same mod". The biome defs live in
   UtinniPatches (`mandrake.rut.patches`); the ported species live in SWBestiary
   (`mandrake.rsw.swbestiary`). A bare cross-mod ref in `wildAnimals` is the
   known-crash shape `WYYYSCHOKK_FERALISK_MERGE_1` removed `AA_Dunealisk` for.
   MEASURED 2026-09-20: 65 of 67 cross-mod entries in the other UtinniPatches
   biome defs are guarded, and `RSW_Jellypot` in this very file kept its guard —
   dropping the guard on the 68 ported rows would have made them the exception.

## Watch out

- ⚠️ **Droid Depot is NOT in the active mod list** (`BIOME_ROSTER_DEAD_SPECIES_REFS_1`).
  Its 7 droids cannot be read from a live game. Porting them means authoring from
  the donor's files on disk, or deciding they do not come back at all — that is a
  question for him, not an assumption for this item.
- ⚠️ **5 Vanilla Core + 1 Biotech row.** Replacing vanilla is consistent with the
  desert cards' standing ban on *"instantly-nameable Earth organisms"* (plain
  `Rat` is in this set). But it is a bigger departure than porting a donor —
  confirm with him before authoring those 6.
- 🔴 The def dump has **no `statBases`** — calibrate from donor mod XML, never the dump.
- 🔴 Fauna size is the ADULT life stage `lifeStages/li[3]`, never `[0]`.
- ⚠️ `AB_GiantStikehr` was cut from the Extreme Desert this same day as misplaced;
  it is NOT part of this port. Do not re-add it.
- ⚠️ The world is repainted at the end (`WORLD_REMAKE_FINAL_STEP_1`) — do not
  build migration machinery for the current save.

## verify

Every desert-family biome table names our defs only; each donor mod can be
removed from `ModsConfig.xml` with the three biomes still generating; every
ported species has its own art; confirmed from a post-load def dump, never from
the patch files.

## criteria

The desert family is ours. Removing Star Wars Animal Collection, Alpha Animals,
Alpha Biomes, ReGrowth or Droid Depot changes nothing a player sees in the desert.
