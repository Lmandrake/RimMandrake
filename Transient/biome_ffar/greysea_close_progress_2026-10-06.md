# Grey Sea sheet close — progress 2026-10-06

## 1. Decisions read
46 rows: 40 letter picks, RM_Reefback/RSW_Reefback A, RM_Hessal redo, RM_Sorruth + RM_SorruthCatch hold "cut don't need" (kill). reviewStatus stamped ruled with his typed words.
## 2. Ingest + install
Ingest DONE: 51 rulings (incl. kept variants), 19 purges, 0 refused, 1 rejected-bytes event (Hessal). Installs DONE: 69 PNGs via `art install --ruling` into src/RimMandrake/TerminalBiomes/Textures (14 creatures x3 facings incl. Orruhmu over A; 11 catch items single east-facing -> Things/Item/RM_GreySea/<def>.png; 16 plants -> Things/Plant/RM_GreySea/<def>/<def>_A.png). Reefback A already live. XML wiring DONE (see 6).
## 3. Kills (Sorruth)
DONE. Removed `<RM_Sorruth>0.4</RM_Sorruth>` from RM_GreySea wildAnimals and `<RM_SorruthCatch>0.5</RM_SorruthCatch>` from its fishTypes saltwater_Uncommon (`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml`). No other biome, patch, RUT_ twin, rare-catch table or C# names either def; the seabed floor copies RM_GreySea's cast at startup, so it drops there too. Defs left in place, cast nowhere. Masonmat description's "The sorruth graze it" clause deleted (now false). Sorruth sheet purges executed by ingest.
## 4. Reefback swap
RM_GreySea already casts RM_Reefback inline (0.005) since 2026-09-25; RSW_Reefback is not cast there (census: "not cast in this biome"). TerminalBiomes ships its own byte-identical Reefback PNGs. Only the frozen RUT_GreySea twin still lists RSW_Reefback.
## 5. Hessal regen
DONE: `greysea_hessal_redo_v2_{east,south,north}` filed to artpipe pending, owner_note verbatim. Source: `Transient/biome_ffar/greysea_close_jobs_2026-10-06.json`.
## 6. Wiring / texPath check
DONE. 13 creatures Graphic_Single->Graphic_Multi on all lifestages (Hessal left Single, redo pending). 11 catch items texPath -> Things/Item/RM_GreySea/<def> (3 sessile catches lost their tint <color> on the shared generic item). 16 plants texPath -> Things/Plant/RM_GreySea/<def> (Graphic_Random folder). Resolver check: 72 graphics, 0 unresolved. placeholder_detect file: 73/73 real (69 installed + 4 Reefback). Old flat single RM_<X>.png placeholders of the 13 creatures retired via ledger on his words. art guard worktree: 0 unledgered.
⚠️ Another agent ran `git pull --rebase --autostash` in this clone at 23:06 and dropped my 13 retire events from BENCH.jsonl; re-recorded them.
## 7. Commits / deploy
- `20fd7cf7c` pushed (installs, wiring, kill, ledger, Hessal job file). Another agent holds uncommitted FlowWorks/GimmeSomeSlack edits in this clone, so the push was built with merge-tree + commit-tree on origin/main and the local branch moved with `reset --keep` (their edits untouched).
- NOT deployed: TerminalBiomes now deploys only as the composed `--compose biomes` mod, and that plan carries ~150 other changes (45 modified incl. 7 DLLs, 102 new) from other biome work, while RimWorld is running. Not mine to push into the live Mods folder mid-session.
- Selftests (run_selftests, timed out at 208/210): 4 FAIL. `selftest_placeholder_detect` failed because its sanity probe read the very placeholder PNGs this close retired; repointed to their archived bytes in the art store (same 6 shas), now 0 failures. The other three (rimflow selftest_built, FlowWorks northstar, FlowWorks liquid_looks) touch nothing here.
- Corrik: B is a real painted creature (pale domed crystalline-shelled body, real by placeholder_detect). The A it replaced was a flat black ellipse placeholder, which is probably what his note means.
