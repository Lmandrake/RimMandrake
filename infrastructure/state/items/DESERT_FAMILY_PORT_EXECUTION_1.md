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
`Transient/*.decisions.json` review sheet. Standing rule (`CLAUDE.md`).

### 🔴 the 81 are NOT 81 jobs to file — the daemon is already running them

CENSUSED 2026-09-20, full table in `Transient/desert_art_census.md`:

| state | rows | what to do |
|---|---:|---|
| **IN FLIGHT** — job already queued or rendered under *this item* | **77** | ⛔ **do not queue.** `registry.jsonl` holds 251 `target` entries with `source: DESERT_FAMILY_PORT_EXECUTION_1`, first registered **2026-09-20 09:41 PDT**. 24 already have PASS-validated renders sitting unreviewed in `_artsrc/`/`done/`; 52 are queued and not yet rendered; 1 (Kybuck) is 2 pass / 1 fail |
| already has our own art | 4 | `RSW_Plant_Chakroot_Wild`, `RSW_Plant_HubbaGourd_Wild`, `RSW_Plant_Bloddle`, and `RSW_Mynock` (wired by `SHIP_VERMIN_MOD_1`) |
| **owner already ruled — CONFLICT** | 1 | `RSW_MossBeetle`, see below |
| **safe to queue** | **3** | `RSW_ImperialToad`, `RSW_Jellypot`, `JOE_Landopus` |

🔴 **So the owed work is 24 renders to REVIEW BY EYE, not 81 to generate.** Filing
`fill_queue.py` for any of the 77 duplicates work already in flight. The next art action
on this item is a review pass over what has already landed — the Rot wave found 4 of 61
renders bad, and only an eye caught them.

⚠️ **`RSW_Ferroclaw` (`A_AA_Terramorph`) has TWO art jobs**: an earlier `aa_terramorph`
from `ART_REGEN_WAVE5_QUEUE_1` (south/east already PASS) and today's
`desertportb_ferroclaw`. Reconcile them; do not treat it as two needs.

### 🔴 scope conflict the owner must settle — `RSW_MossBeetle`

`Transient/deeps_flora_fauna_review_2026-09-18.decisions.json` (owner-approved
**2026-09-19**) rules `RSW_MossBeetle` **CUT**. This item's blanket *"replace"* ruling
came **2026-09-20**, one day later, and sweeps it back in. Two owner rulings one day
apart disagree about the same creature. ⛔ Do not generate art for it and ⛔ do not
silently drop it — it is his call which ruling governs.

### ✅ the def half is DONE except for the 12 rows that need him

FINAL, 2026-09-21. The "11 unblocked rows" this section used to list was itself wrong:
**9 of the 11 were already ported** under drafted names. Only two genuinely needed
authoring, and both landed at `1ab7b6f09`:

| donor | ours | state |
|---|---|---|
| `AA_BoulderMit` | `RSW_Stoneback` ("korrum") | **newly authored** |
| `Plant_Brambles` | `RSW_Thornscrub` ("krenna bramble") | **newly authored** |
| `Terrorworm` | `RSW_Ashworm` ("vurra") | already live |
| `VFEI2_Fuelmite` | `RSW_Cindermite` ("zhakka") | already live |
| `AB_Aaklac` | `RSW_VellaraBloom` | already live |
| `AB_DessertTree` | `RSW_SweetbarkTree` | already live |
| `AB_HardyGrass` | `RSW_Dunegrass` | already live |
| `RG_Plant_AridGrass` | `RSW_Scrubgrass` | already live |
| `RG_Plant_CreepStern` | `RSW_Starvine` | already live |
| `RG_Plant_CrimsonCushion` | `RSW_EmberCarpet` | already live |
| `RG_Plant_Dervish` | `RSW_Whirlbloom` | already live |

⚠️ **Every one of those names is DRAFTED, not ruled** (`NONCANON_BEAST_RENAME_1`'s design
is *"agent drafts, owner reacts"*). They need to reach him as a batch.

✅ Authoring `RSW_Stoneback` also fixed a real dangling reference: `RSW_Ferroclaw`'s
`<useMeatFrom>RSW_Stoneback</useMeatFrom>` pointed at a def that did not exist.

⇒ **96 of 109 rows are ported. 12 are blocked on the owner. 1 is out of scope.**
The def half of this item is finished; what remains is his 12 answers, the art review,
and step 4 (rewiring the biome tables).

### 🔴 the instrument lesson — stop re-measuring this wrong

**A `RSW_<donorName>` prefix test CANNOT find a ported row, because the port renames it.**
This produced a wrong count three times in one sitting: first "~105 to author" (counted
all 109 as unported), then "11 to author" (found the 13 Alpha Animals renames but missed
the Alpha Biomes / ReGrowth / Horrors / VFEI2 renames, which use the same mechanism).

✅ **The mapping is authoritative and it is in the source**, as
`<!-- <donor> -> RSW_<ours>. ... -->` header comments in
`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml` and
`RSW_DesertPortMisc_Plants.xml`. Read those comments before counting anything on this
item. ⛔ Do not count by prefix.

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

## the art review sheet — built 2026-09-20, waiting on the owner's eye

`D:\Luke\dev\Rimworld\Transient\desert_art_verdict_2026-09-20.html`
decisions → `D:\Luke\dev\Rimworld\Transient\desert_art_verdict_2026-09-20.decisions.json`

Serve it:
```
python3 ~/.claude/skills/review-sheets/assets/serve_sheet.py \
  --sheet Transient/desert_art_verdict_2026-09-20.html \
  --decisions Transient/desert_art_verdict_2026-09-20.decisions.json
```

- **25 rows** — 24 desert-port creatures whose three facings all PASS, plus a 25th for
  `RSW_Ferroclaw` showing its **earlier** `aa_terramorph` art (south+east PASS, north
  failed), because today's own job is still queued.
- **Excluded, with nothing to look at:** 179 still-queued facings across the wave's
  remaining ~52 creatures, and Kybuck's north facing (`generated`, not yet validated).
- **Donor art recovered for all 25**, so every row is judged as a *replacement*, not an
  image in isolation.
- **Canon `## Must show` checklist shown for 9 of 25** (Anooba, Bantha, Corinathoth,
  Eopie, Gizka, Iriaz, Kreetle, Mudhorn, Nuna). The other 16 have no
  `canon_references/` entry — flagged on the row, **not invented**.
- Gate: `check_sheet.py` 0 FAIL / 0 WARN / 34 ok; both script blocks pass `node --check`.
  ⚠️ **Not click-tested in a live browser** — no GUI was available to the builder.

🔑 Re-run `Transient/desert_art_verdict_build_2026-09-20.py` then
`..._assemble_2026-09-20.py`, in that order, as more of the queue lands.

⚠️ Neither `make_verdict_sheet.py` nor `build_flora_legibility_sheet.py` was reusable —
both hand-roll a localStorage-only page predating the current
`sheet_template.html`/`check_sheet.py` contract.
