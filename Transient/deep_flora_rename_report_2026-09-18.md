# DEEP_FLORA_RENAME_1 — execution report, 2026-09-18

Owner approved verbatim "Approve all" on `design/Jawa/worldbuilding/biomes/lantern_deeps_flora_names.md`.
Nothing committed, nothing deployed (game running). All paths below are repo-relative to `D:\Luke\dev\Rimworld`.

## Rename map

| old defName | new defName | new label | texture folder |
|---|---|---|---|
| RUT_Crystalcap | RUT_ThrakkCap | thrakk cap | Plant/ThrakkCap |
| RUT_CrystaltipBrambles | RUT_OsskBramble | ossk bramble | Plant/OsskBramble |
| RUT_DeepArpeau | RUT_VellokReed | vellok reed | Plant/VellokReed |
| RUT_DeepGreyLady | RUT_PrennaLace | prenna lace | Plant/PrennaLace/PrennaLace{Grown,Immature} |
| RUT_DeepNuitae | RUT_NurrikGill | nurrik gill | Plant/NurrikGill |
| RUT_Fungusfern | RUT_QuorrFern | quorr fern | Plant/QuorrFern |
| RUT_Gleamtip | RUT_ZivvitTaper | zivvit taper | Plant/ZivvitTaper |
| RUT_LuminousSpout | RUT_KuvraSpout | kuvra spout | Plant/KuvraSpout |
| RUT_YumBulbs | RUT_BrellikBulb | brellik bulb | Plant/BrellikBulb |
| RUT_DeepDulcisPlant | RUT_TwitchingPuffer | twitching puffer | Plant/TwitchingPuffer/Puffer{Grown,Immature,Harvested} (new) |
| RUT_DeepMycelium | KEEP | mycelium | Plant/Mycelium |
| (RUT_RawDulcis, RotSporeKit's) | RUT_PufferTendrils (new item) | puffer tendrils | Item/Crops/PufferTendrils (new) |

Labels, descriptions and the puffer/tendrils field tables taken verbatim from the names file.

## Defs

- `src/RimUtinni/LanternDeeps/Defs/ThingDefs_Plants/RUT_DeepFlora.xml`: 9 defs renamed (defName, label, description, texPath; PrennaLace's immatureGraphicPath); dulcis def replaced by `RUT_TwitchingPuffer` with the same numbers and `harvestedThingDef RUT_PufferTendrils`; header comment rewritten (no dulcis mention).
- `src/RimUtinni/LanternDeeps/Defs/Biomes/RUT_LanternDeeps.xml`: 10 wildPlants keys renamed; `foragedFood` → `RUT_PufferTendrils`.
- `src/RimUtinni/LanternDeeps/Defs/ThingDefs_Items/RUT_LanternstoneItems.xml`: `RUT_PufferTendrils` added (shape of RotSporeKit's `RUT_RawDulcis`, PlantFoodRawBase, Rottable 16d, RawTasty/Fungus, Ideology-gated Fungus merge tag); dulcis header note replaced.
- `src/RimUtinni/LanternDeeps/About/About.xml`: `mandrake.rut.rotsporekit` modDependency and loadAfter REMOVED. Grep of the whole mod found no other RotSporeKit reference (the only hits were the dulcis dependency note, the biome foragedFood and the plant's harvestedThingDef, all gone).
- Patches (`RUT_LanternstoneFictionRename.xml`, `RUT_LanternDeepEvictCrystalFauna.xml`, GenStep XML): 0 hits on any flora name — nothing to change there. `validation.py`: 0 hits.
- `validate_patch.py` against Data + workshop + Mods roots: 3 files, 0 errors; 3 warnings, all the not-yet-wired puffer texPaths (expected). Every renamed folder resolved.

## Textures

`git mv` (history follows): 8 plant folders + PrennaLace (folder and its two stage subfolders) — 22 renamed PNGs. `git rm` of `Plant/Dulcis/**` (3 PNGs, the Rot's mushroom). No new PNGs written into the mod (wire_art not applied — the owner's review posture).

## C#

- `Source/GenStep_DeepFloraGate.cs`: all 10 literals in `OwnedFloraDefNames` updated (mycelium and `RUT_Lanternstone_Sowable` unchanged).
- `Source/DeepFloraPlanter.cs`: comment names updated. `MapComponent_DeepFloraRegrowth.cs` and every other `.cs`: 0 hits.

## Tooling

- `wire_art.py`: flora dest paths re-derived to the new folders (job ids unchanged: gleamtip_*, fungusfern_*, crystaltipbrambles_*, yumbulbs_*, crystalcap_*, greylady*, arpeau_a/b, luminousspout_*, nuitae_a/b); dulcis rows replaced by the four puffer ids; dulcis ids and `twitchingpuffer_harvested_v1` listed in EXCLUDED_JOB_IDS with reasons; docstring notes the re-derivation.
- `build_art_sheet.py`: same mapping; new `pending` status (counts dict + occurs flag) so a filed-but-unrendered job does not KeyError.
- `ART_JOBS.md`: rows 12, 14–23 rewritten (texPath column and prose); 18/18b/18c are the puffer rows, 12 is the tendrils item.
- `tint_organics.py`: docstring only (YumBulbs → BrellikBulb); behaviour is by hue, unchanged.
- Dry run `python3 src/RimUtinni/LanternDeeps/wire_art.py --all-pass`: `# 47 kept, 1 skipped, 2 texPaths have no job at all` — every plant path served; the one skip is `twitchingpuffer_harvested_v2` (pending); the 2 unserved are the pre-existing wall atlases.

## Puffer

Filed in `infrastructure/artpipe/pending/`: `twitchingpuffer_grown_v1`, `twitchingpuffer_immature_v1`, `twitchingpuffer_harvested_v1`, plus `twitchingpuffer_tendrils_v1` (a FOURTH job — the brief said three, but `RUT_PufferTendrils` has its own texPath and would render magenta without it; the names file specifies four). Field shape copied from `done/dulcisgrown_a_v1.json`; `reference` null; `rimflow_item_id` DEEP_FLORA_RENAME_1; prompts from the names file with the rounded-ball exception spelled out and "render blue, tint shifts it".

The artpipe daemon picked all four up within 3 minutes; all four are in `done/` with facts PASS, 256×256. Contact strip: `D:\Luke\dev\Rimworld\Transient\deep_flora_puffer_strip_2026-09-18.png` (immature, grown, harvested, tendrils). Immature, grown and tendrils read correctly. **harvested_v1 is a content miss** — a smooth wrapped cocoon, no ball, no tentacle stubs — so `twitchingpuffer_harvested_v2` is filed in pending with a tightened prompt and the tooling points at v2 (v1 excluded with the reason).

Owed after the review: `wire_art.py --apply` on the owner's decisions, then **`python3 src/RimUtinni/LanternDeeps/tint_organics.py --apply`** so the puffer set goes violet with the rest of the organics.

## Sheet

`design/Jawa/worldbuilding/biomes/the_lantern_deeps.md`: one amendment line added under the freeze header (exact text from the brief); the donor-inventory sentence on line 42 now reads "zivvit taper, thrakk cap for mushroom logs, prenna lace for lace" (labels only). No other ruling touched.

## Build

`dotnet build … -c Release`: **0 Warning(s), 0 Error(s)**; `Assemblies/RimMandrake.Utinni.LanternDeeps.dll` rebuilt (shows modified). NOT deployed.

## Census after

Scope: `src/RimUtinni/LanternDeeps`, `src/RimUtinni/UtinniPatches`, `the_lantern_deeps.md`, `EXPECTED_FAILURES_next_load.md`; patterns: the ten old defNames, `RUT_RawDulcis`, and the label words (Crystalcap, Crystaltip, Arpeau, GreyLady, "Grey Lady", Nuitae, Fungusfern, Gleamtip, LuminousSpout, YumBulbs, Dulcis), case-insensitive inside the mod.

Survivors, all deliberate:
- `src/RimUtinni/LanternDeeps/wire_art.py` 87–145 and `build_art_sheet.py` 66–90: historical artpipe **job ids** (`gleamtip_a_v1`, `arpeau_a_v1`, `dulcisgrown_a_v1`, …) as table keys/comments — required, the ids are the artpipe's history.
- `src/RimUtinni/LanternDeeps/Defs/ThingDefs_Plants/RUT_DeepFlora.xml:22` and `Defs/ThingDefs_Items/RUT_LanternstoneItems.xml:16`: the word "RotSporeKit" in a comment saying its mushroom does not grow here / the item shape was copied — no packageId reference.
- `design/Jawa/worldbuilding/biomes/the_lantern_deeps.md:8`: "dulcis replaced by the twitching puffer" — the amendment line the brief dictated.
- `infrastructure/state/EXPECTED_FAILURES_next_load.md:39,42–43`: the old defNames listed as the ABSENT check — by design.
- `src/RimUtinni/UtinniPatches/**` (RUT_TheRot.xml, BiomeFlora_Ashkarr.xml, PlantTolerances_Ashkarr.xml, BiomeFloraStatAdjustments_Generated.xml, RotDecayHarvest_LivingProduce.xml, RotGuardianGroves_WildSpawn.xml): every hit is RotSporeKit's own `RUT_Nuitae`/`RUT_Arpeau`/`RUT_GreyLady`/`RUT_RawDulcis` or the donor's `BMT_*` — never a LanternDeeps def. Not rename sites.
- `RUT_*` old defNames inside `src/RimUtinni/LanternDeeps`: **0**.

## Open

- Owner review of the four puffer renders (+ harvested_v2 once rendered) on the art sheet; then `wire_art.py --apply` and `tint_organics.py --apply`.
- Deploy (`deploy_custom_mods.py --mod LanternDeeps`) with the game down; DLL + defs + moved textures all ride together — a partial deploy renders magenta.
- `lantern_deeps_rename_proposal.md` (rejected first proposal) is slated for deletion by the names file's note 11 — outside this brief's write scope, not touched.
- The other seat's unstaged deletes in `infrastructure/artpipe/pending/` were not touched.
