# Owner card answers 2026-10-05 (decision taken by question card; clicked, not typed)

## 1. LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1 — "Delete them" — DONE
- Removed from `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/` (ThingDef + PawnKindDef): RSW_BloodropMoth, RSW_FacetMothLarvae,
  RSW_Megapleura, RSW_MossBeetleLarvae, RSW_Gembug. Their private closure: 10 egg ThingDefs (all five, fert + unfert),
  4 RSW_Biomes_Pillbug_* SoundDefs (+ the 4 mp3s), orphan hediff RSW_GembugDefense.
- Kept (shared with other SWBestiary defs, so not ours to remove): RSW_ChitinStuff, RSW_MothWing, the larval/chitin bases.
- Correction (coordinator): adults RSW_FacetMoth / RSW_MossBeetle keep their egg-laying; the 4 egg defs are kept and now hatch RM_FacetMothLarvae / RM_MossBeetleLarvae. SWBestiary About.xml gains a dependency on mandrake.rm.lanterndeeps. No growth chain larva -> adult exists in the defs.
- References repointed/removed: RUT_Miasma roster row RSW_Gembug (frozen twin; a dead def would have errored), the RSW_Gembug temperature
  pin in AnimalTolerances_Ashkarr.xml, design roster the_lantern_deeps.json (-> RM_), 5 rows of armoury_bestiary_desc_remainder.csv.
- Generator `port_fauna.py` retired (git rm); the five generated `RM_LanternDeeps_Fauna_*.xml` headers now say hand-owned.
- No RM_ def inherits from any deleted def (grep of src/ for the 19 names: only comments and the dead sheet builder remain).
- Textures: 18 PNGs retired through the art ledger (`artledger.retire`, reason `script:LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1`).
  6 refused as OWNER-KEPT (Gembug/Blue Jewelbug x3, Megapleura x3): retiring needs his typed words; they stay as orphan files
  with no def. Same bytes live at the RM_ paths.
- Left alone: `build_species_sheet.py` (one-shot builder of the already-ruled sheet; would not re-run), comments in RM_Miasma/About,
  generated `creature_register_rows.json` (dated snapshot).
- validate_patch: SWBestiary/LanternDeeps/Utinni files, no error mentions a removed def (102 pre-existing missing-texPath errors on
  Gizka/Vornskyr/Hawkbat etc. are unrelated). run_selftests: 190/191 (selftest_tool_metadata failing before this work).

## 2. "Treat all as ours" — DONE
Seven rows recorded in `design/RimStarWars/canon_references/NO_SOURCE.json` under new key `owner_ours`, each
"owner, by question card 2026-10-05: treat as ours": RM_Peeper, RM_Saava, RM_FireHawk, RM_FireWasp, RM_Kirruk, RSW_Screecher, Plant_Grass.
`art_sheet.py` `_no_source()` now reads `owner_ours` (RSW_ rows get "not canon-linked"; RM_/plain rows already get no canon tag).
RSW_Screecher also carries the note in its existing `not_canon_linked` text. No renames.

## 3. ART_VERSION_WRANGLING_1 hook — "Block as they happen" — DONE
`.claude/hooks/block_unledgered_texture.py` (already written) registered in `.claude/settings.json` PreToolUse/Bash group.
It bites only on `git commit` / `./publish` / `git push` that take texture PNGs the ledger did not make, so art install, artpipe collect
and sheet tools (which write through `install_bytes`) are untouched. Own selftest ALL PASS; direct runs with `ls` and `git status`
input exit 0 with no output. Newly registered hooks fire only in NEW sessions. The git pre-push guard is separate and already live.
