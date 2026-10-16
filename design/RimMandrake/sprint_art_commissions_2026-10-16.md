# Sprint art commissions, 2026-10-16 (FOUNDRY helper)

Owner, `--owner-said`: *"try to commission all art you can so it doesn't bottleneck us (within this sprint of course)"* and
*"Anything still from ratchet experiment too"*. Scope: Phase 0 (donor retirement, gate Mon 2026-10-19), plus the ratchet pilot's
Pyrelands, GimmeSomeSlack and FlowWorks. Nothing here is installed. Every job is queued in artpipe (daemon pid 1881904, 5 workers,
idle when I started); renders land in `D:\Luke\dev\_artpipe\done\` and go on a review sheet before any `art.py install`.

Job files (the provenance; rows carry target_def, install_to, prompt, priority):
- `D:\Luke\dev\RimMandrake\design\RimMandrake\sprint_art_commissions_wave1_2026-10-16.json` (priority 30-32, 15 jobs)
- `D:\Luke\dev\RimMandrake\design\RimMandrake\sprint_art_commissions_wave2_2026-10-16.json` (priority 46-50, 50 jobs)

(Paths are the repo's; `/home/mandrake/rm/foundry/design/RimMandrake/` is the working clone until pushed.)
Throttle: 65 jobs against 5 workers at about 7 minutes each is roughly 1.5 to 2 hours wall; the lower priority numbers claim first, so
wave 1 drains before wave 2. North/south facings are derived from each row's east master (ARTPIPE_FACING_COHERENCE_1), so they start
after the east lands.

## How the gap was found (read this before trusting a "Phase 0 art is done" line)

The art ledger, not the md5 check, is the instrument. For every live slot under `src/`, fold its live sha and look for a `donor`
variant carrying `donor_pkg`. Result on 2026-10-16: **207 live `SWBestiary` slots are still byte-identical to Star Wars Animal
Collection art** (file sha256 re-read from disk equals the ledger sha for all 207; all 207 are referenced by a def). SWAC's art lives in
a bundle, so the md5-against-loose-PNGs comparison in the kickoff's gate 0.5.5 clause 3 cannot see them. Breakdown: 100 body, 61
dessicated, 18 mask, 9 swimming, 19 other. Script: scratchpad `donorlive.py` (ledger `Index.live` joined to `Index.variants`); rerun it
before calling clause 3 met. Alpha Animals and Alpha Biomes are not installed on this machine, so the same check cannot run for them here.

| group of the 207 | slots | state |
|---|---:|---|
| body, swimming and mask slots whose species already has artpipe renders (commission 1, 2, v2, enact) | 90 | renders exist, waiting on his picks at O1; not re-queued |
| dessicated corpse pictures | 61 | **NOT commissioned: needs his ruling (see below)** |
| item icons, ability icons, trophies, eggs, meat, raw foods | 44 | **commissioned, wave 2** |
| Kaadu female swimming (3), Snoruuk adult stationary (3) | 6 | **commissioned, wave 2** |
| Snoruuk juvenile stationary (3), Snoruuk dessicated (2), Gullipud_i corpse (1) | 6 | not yet (sequenced or held, below) |

## Commissioned

### Wave 1: shared overlays, Braskeen, plants and fish whose texPath is a donor or missing path

| job id (facings) | subject | why | source item |
|---|---|---|---|
| `packoverlay_biped_v1` (E, S, N) | loaded-pack overlay B, upright biped (Kybuck, Kaadu, Blurrg, Tauntaun, Brezak, Thranta) | 3 facings x 6 races; overlay A (`packoverlay_quadruped_v1`) landed and reads well | `PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS` |
| `packoverlay_sixlegged_v1` (E, S, N) | overlay C, six-legged shelled insect (HarvesterBeetle, Moravatha, FoundryBeetle, RoyalRhino, LavaFlea, Megatardi) | same | same |
| `packoverlay_lowlong_v1` (E, S, N) | overlay D, low long body (Gelagrub, Sacapillar) | same | same |
| `braskeen_onE_v4` | Braskeen variation, five sprawling arms, one shut on a husk | `braskeen_onE_v1`/`v2` failed reskin-validate (subject 8% and 30% smaller than E, squashed, shifted). Refiled with E as `canon_reference` (anatomy guidance, no reskin-validate) and a 94%-of-canvas span in the prompt. v3 stays installed | `BRASKEEN_REDRAW_VARIATIONS_ON_E` |
| `braskeen_onE_v5` | Braskeen variation, young crowded whorl | same | same |
| `p0art_glasskelle_v2` | Scald vent coral | `scald_glasskelle_v1` failed (worker exit 1, no image); def still on donor `SnakePlant/SnakePlantA` | `SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE` |
| `p0art_rimebeard_v1` | Grey Sea rimebeard | no render ever; def on donor `SnakePlantA` | same |
| `p0art_stillbloom_greysea_v1` | Grey Sea stillbloom | no render for this def (the `RM_Stillbloom` folder art in TerminalBiomes belongs to `RM_ChillStillbloom`); def on donor `PincushionPlantB` | same |
| `p0art_lungerfry_v1` | RM_LungerFry fish item (RUT_LungerFry is the frozen twin, shares it at the paint) | on donor `EcheveriaA` | same |

### Wave 2: SWAC donor bytes still live (all `target_def` RSW_, install_to under `src/RimStarWars/SWBestiary/Textures/`)

| jobs | subject | source item |
|---|---|---|
| `p0art_chrysalideheart_v1`, `_greenmilk_`, `_nexutongue_`, `_rikknitovum_`, `_tachgland_` (5, 256 px) | animal products | `DONOR_DEFS_PORT_TO_OURS_1` |
| `p0art_eggdimple_a/b`, `_eggrough_a/b`, `_eggshark_a/b`, `_eggfungi_a/b` (8, 256 px) | thranta, rancor and jungle rancor, drexl eggs, snoruuk spore; Graphic_Random pairs | same |
| `p0art_glitterstim_a/b_v1` (2) | glitterstim drug pair | same |
| `p0art_meat_rancor_a/b/c_v1`, `p0art_meat_rycrit_a/b/c_v1` (6) | raw meat, three variants each | same |
| `p0art_behemothskull_`, `gundarkskull`, `mankatooth`, `mastmottusk`, `rancorskull`, `rancortooth`, `taozinnodule`, `tukataspike`, `skaldertusk`, `warwyrmskull` (10) | hunting trophies | same |
| `p0art_tookeroot`, `bloddle`, `chakroot`, `hubbagourd`, `nysyllin` (5) | raw plant-food icons (the wild plants have renders; these item icons do not) | same |
| `p0art_abil_acidspray`, `chaosskip`, `invisibility`, `animalspit`, `toxicspew`, `forcepush` (6, 128 px) and `p0art_proj_spitproj`, `forceblast` (2) | trainable-ability icons and two projectiles | same |
| `p0art_kaadu_f_swimming_v1` (E, S, N, 512 px, `derive_from donorport_kaadu_f_v1_east`) | female kaadu swimming | same |
| `p0art_snoruuk_stationary_v1` (E, S, N, `derive_from enact_6811876e_snoruuk_v1_east`, his pick B) | adult snoruuk rooted pose | same |

Canon check: none of these is a creature body with a canon library entry except the two derived ones, which inherit the canon
images of their parent entries through `derive_from`/`canon_reference` (the job file shows them attached). Items and icons carry no
`canon` link (no Must-show list applies to a bone or an egg). Nothing is Star Wars IP beyond names already in the defs.

Biome-sprint kit art (ruled by card 2026-10-16, *"Let me guess the designs"*): commissioned with guessed designs, see
`design/RimMandrake/kit_art_designs_2026-10-16.md`.

## Deliberately NOT commissioned

| what | reason |
|---|---|
| **61 dessicated corpse pictures** of ported SWAC species (plus `Snoruuk_Dessicated`, `Snoruuk_j_Dessicated`, `Gullipud_i` corpse) | His 2026-10-08 ruling on `DESICCATED_LOOKALIKE_FAMILIES_1`: *"Look alike families but this ticket should be blocked by finalizing the per biome art."* Per-species dessicated art is the opposite of that. They are donor bytes, so gate clause 3 (*"every ported def's art has an owner-accepted art-ledger event"*) fails until he rules. **NEEDS HIS RULING** |
| 90 body, swimming and mask slots that still hold donor bytes | renders already exist (donorart_*, donorport_*, enact_*, `_v2`); they wait on his picks at O1. Not re-queued |
| FrogDog north, Grazer male north, Torton female south | the v1 and v2 renders each failed the canon gate twice (hands "four digits", head "narrow"; the rear view cannot show some Must-show lines). Renders exist in `_artsrc`. Put them on the sheet flagged, or `artpipe_state.py owner-accepted`; another re-roll will fail the same lines |
| 18 colour-mask files (`*_eastm/northm/southm`: ChrysalideRancor, NexuW, Nexu_j, RancorW, Rycrit, Squall) | a mask is paired with its body; if his pick for those bodies is a new render, the def's shader must drop the mask (a def change) or the mask is derived afterwards. Decide at enact, not now |
| Snoruuk juvenile stationary (3) | derive from the adult stationary render; queue after `p0art_snoruuk_stationary_v1` lands |
| Scald understorey 7 + KettlewickSalt, Pulsebead, Noothelm, Cauldron flecks 2 + dew 5, CrawlSmear, Dakkra_rest | renders exist (`scflora_*`, `scald_pulsebead_v1`, `twilightsea_noothelm_redo_v1`, `gap_RM_AssayFlecks_*`, `gap_RM_Dewfall_*`, `gap_RM_CrawlSmear`, `gap_RM_Dakkra_rest_v1`); they need a sheet and his pick, then `art.py install` |
| Dustveil and BedBug eggs | renders done and installed, **but only at the Fertilized path**. `RM_BedBugEggUnfertilized` (`Cauldron/Defs/ThingDefs_Races/RM_BedBug.xml:191`) and the Dustveil unfertilized egg (`TheRot/Defs/Fauna/RM_Dustveil.xml:232`) still name `Things/Item/Resource/RM_BedBugEgg` / `RM_DustveilEgg`, which do not exist. `texture_gap_lint.py` fails on exactly these two. A def repoint, not art |
| SandLion v2, Hydenock, Jogan, Tooke trap, Sarlacc, Zhissa, Vekka, AngelMoth options, Skorra | rendered, and most are installed on his word; Skorra waits on a sheet row |
| Alpha Biomes (16 plant and disease names) | his card at O1 (*"Retire Alpha Biomes now too?"*) is unanswered |
| Gender, juvenile and swimming art for species not yet reached | `EXTRA_ART_PER_BIOME_COMMISSION_1`: per biome, after group sizes are settled |
| 49 shipped placeholders on `placeholder_allowlist.json` (FeverWood, LuminousPigment, TheSump, Webwork, Bacta, RUT_Greenwood) | not Phase 0, not ratchet; owned by those biomes' sittings. Three Murrelith entries are stale (`placeholder_lint.py` fails on them) |
| Ratchet pilot: Pyrelands | owner approved the whole review save 2026-10-16 (*"I'm approving this whole sheet"*); art coverage is 49 of 51 texPaths ours, the other two (`Filth/Ash`, `ShellFirefoam`) are vanilla by design. Nothing owed |
| Ratchet pilot: FlowWorks | tanks (16 looks), containers (12 plus masks), pit ladder (lowered and raised), pipe looks are installed and approved. 86 of 91 texPaths ours; the five left are vanilla Spatter, ChunkStone, VatBubble and Fire, so replacing them is a cosmetic change he must permit. `FLOWWORKS_NORTHSTAR_SHIP_1`'s "97 of 100 borrowed" line is stale (2026-10-07) |
| Ratchet pilot: GimmeSomeSlack | 24 of 24 texPaths ours; the rest is code-drawn |
| `SWALE_CANAL_ART_REFERENCE_1` | needs a live screenshot of a built canal; not offline |
| Owner-kept donor art (18 species) | his ruling stands |

## Needs his ruling (two lines)

1. **Dessicated corpses of the ported SWAC species** (61, donor bytes): draw them per species now (about 61 jobs, 1.5 h of daemon), or
   accept the donor pictures as owner-kept for Phase 0 and let the look-alike-family ticket redraw them after the biome art settles?
2. **Retire Alpha Biomes too?** (Unchanged from the kickoff; it decides whether its 16 names get art jobs.)

Check progress: `ls D:\Luke\dev\_artpipe\pending` and `...\active`; per job `python3 src/RimMandrake/Utils/artpipe/artpipe_state.py find <id> --names-only`.

## Update 2026-10-16 (later): dessicated corpses queued, Alpha Biomes retired

Owner, `--owner-said`: *"Go ahead and queue all pending art"*. By card: dessicated corpses drawn per species now; Alpha Biomes retires. 63 jobs `dessic_*` queued (priority 51; file `dessicated_corpses_commission_2026-10-16.json`, builder `dessicated_corpses_commission_build.py`; item `DESSICATED_CORPSES_REDRAW_ONE_BY_ONE`). The species' own body art rides as `canon_reference`, never `reference`; no `canon` entry is set because a living animal's Must-show list would mis-grade a skeleton. Alpha Biomes: `alpha_biomes_retirement_2026-10-16.md`; zero art jobs queued because all 14 plants already have ours.
