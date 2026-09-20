# SHEET_ORPHAN_CONSUMPTION_1 — flora `art:improve` channel, final resolution

Scope: the 37 rows the item's own 2026-09-20 audit called "genuinely OWED" (96
of the original 148 were already ALREADY DONE, 3 already queued, 37 owed — with
the 17 non-BMT rows cleared to file immediately and the 20 `BMT_Plant_*` rows
held on `BMT_FLORA_ABSORPTION_1`). That hold item closed today, and a concurrent
session in this same window finished repointing/porting the 14 dead `BMT_`
plant defNames it covered. This pass re-derived the 37 owed rows against that
new ground truth, per the owner's standing rule: *"please make sure nobody has
already done so before you."*

**Result: 0 of the 37 rows are genuinely owed. No art jobs were filed.**

## The 17 `BMT_Plant_*` rows (recount: actually 17, not 20 — see below)

The item text says "17 non-BMT / 20 `BMT_Plant_*`"; a literal extraction of its
own "### The 37 owed" list gives the opposite split — **17 `BMT_Plant_*` rows,
20 non-BMT rows** (confirmed by script, not by eye — the manual-count trap this
project warns about repeatedly). Both totals still sum to 37; only the two
sub-counts were swapped in the item's prose. Acted on the real (parsed) split.

### 5 ALREADY DONE — real ThingDef + real, non-trivial art on disk
`BMT_Plant_TreeTwistingThornwood` → `RUT_TwistingThornwood`,
`BMT_Plant_TwistingThorngrass` → `RUT_TwistingThorngrass`,
`BMT_Plant_TwistingThornweed` → `RUT_TwistingThornweed`,
`BMT_Plant_TreeMartyr` → `RUT_TreeMartyr`,
`BMT_Plant_ScorchedStars` → `RUT_ScorchedStars`.
All 5 defined in `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_PollutedFlora.xml`,
each with 2-3 real growth-stage PNGs (6-55 KB each, not placeholders) already
under `src/RimUtinni/UtinniPatches/Textures/Things/Plant/*/`.

### 12 CUT — no ThingDef, no roster presence, explicit ruling on record
`BMT_Plant_TreeTanglerootMangrove`, `BMT_Plant_SewerReed`, `BMT_Plant_Snaketails`
(the 3 Miasma cuts named in this pass's brief — confirmed absent from every
`src/` XML and present only in `the_miasma.json`'s `flora_purged` provenance
array) **plus** `BMT_Plant_GutterPlantain`, `BMT_Plant_ToxicIvy`,
`BMT_Plant_TwistedDandelion`, `BMT_Plant_WildRashroot`, `BMT_Plant_Doomsprout`,
`BMT_Plant_TumorbulbHyacinth`, `BMT_Plant_PoxSorghum`, `BMT_Plant_EclipsusFlower`,
`BMT_Plant_EclipsusLeaves` (the 9 the brief flagged as "status unknown, may be a
missing-port gap"). All 9 turned out to be resolved already, not a gap:
`wasteland.json`'s `flora_purged` array carries an identical explicit reason for
each — *"POLLUTED_LANDS_FLORA_PORT_1: biomesteam.biomespollutedlands retired
2026-09-18 (mutation system RULED DROP, caverns_replacement_scoping.md §4/§5);
Wasteland's toxic-ground identity already carries via its vanilla/AB_ poison
flora ... so this donor filler plant is cut rather than ported."* None of the
12 has a ThingDef anywhere in `src/`, confirmed by grep across
`src/RimUtinni`, `src/RimStarWars`, `src/RimMandrake`. No art owed against a
cut subject — filing any would be exactly the waste the owner ruled against for
the 4 purged flora at the top of this item (*"I don't want new versions of
these silly plants"*), and this is the same disposition, just recorded under a
different ruling name.

## The 20 non-BMT rows

### 18 ALREADY DONE — exact source-row match in `infrastructure/artpipe/done/`
Matched by reading each candidate job's own `style_notes`/`prompt` field for
an exact `"Source row: flora:<biome>:<defName>"` citation (stronger than a
slug-stem guess) — all landed via the closed item `ART_REGEN_FLORA_WAVE1_QUEUE_1`
or an earlier wave, `status: "ok"`, `timed_out: false`, and a real PNG present
in `_artsrc/`:

| defName | done job id |
|---|---|
| `AB_AlienTree_Polluted` | `alientreepolluted_v1` |
| `AB_TentacularPlant` | `tentacular_v1` |
| `AB_ToxiGrass` | `abtoxigrass_v1` |
| `Plant_Bubblespore_Wild` | `bubblespore_v1` |
| `Plant_FelucianGlowspore_Wild` | `felucianglowspore_v1` |
| `Plant_HealrootWild` | `healroot_v1` |
| `Plant_HydenockTree_Wild` | `hydenocktree_v1` |
| `Plant_JoganTree_Wild` | `jogantree_v1` |
| `Plant_MujaFruit_Wild` | `mujafruit_v1` |
| `Plant_TookeTrap_Wild` | `tooketrap_v1` |
| `Plant_TreePolux` | `polux_v1` |
| `RG_Plant_AridGrass` | `aridgrass_v1` |
| `RG_Plant_CreepStern` | `creepstern_v1` |
| `RG_Plant_CrimsonCushion` | `crimsoncushion_v1` |
| `RG_Plant_Dervish` | `dervish_v1` |
| `RG_Plant_TallToxiGrass` | `talltoxigrass_v1` |
| `RG_Plant_ToxiGrass` | `rgtoxigrass_v1` |
| `RG_Plant_TropicalChokevine` | `tropicalchokevine_v1` |

### 2 EXCLUDED (superseded, not owed) — `Plant_YellowGrass`, `Plant_YellowTallGrass`
Absent from every biome roster json (grepped all of
`design/Jawa/worldbuilding/biomes/rosters/`) — confirmed dead content, not a
gap. `ART_REGEN_FLORA_WAVE1_QUEUE_1`'s own closed record already found this and
explicitly excluded both rows for the same reason before filing its 14 jobs.
This pass's "37 owed" figure had not re-applied that exclusion; it should have.
Both are vanilla RimWorld `ThingDef`s (`Plant_YellowGrass`/`Plant_YellowTallGrass`)
that `src/RimUtinni/UtinniPatches/Patches/PlantNames_Ashkarr.xml` only relabels
("ochreskal"/"tall ochreskal") — not modded content we own art for, and not
placed in any of our rosters.

## Net result

**Already done: 23 · Excluded/cut (no live subject): 14 · Genuinely owed: 0 ·
Jobs filed: 0.**

(23 = 5 BMT-ported-with-art + 18 non-BMT matched; 14 = 12 BMT cut + 2 vanilla
excluded rows.)

No writes to `infrastructure/artpipe/pending/`, no roster edits, no def edits.
This channel of `SHEET_ORPHAN_CONSUMPTION_1` (flora `art:improve`) is now fully
accounted for with zero art debt outstanding. The item itself is left open —
other channels (118-row ledger, sizeBin OWED rows, flora move/purge execution)
are untouched by this pass and are not this seat's call to close.
