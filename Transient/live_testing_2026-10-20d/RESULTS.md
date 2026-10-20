# Live testing 2026-10-20d — xeno heads enact + restart + head line-up screenshots (FOUNDRY helper)

Owner (2026-10-20, at bench): *"I REALLY want to see a screenshot of aliens with these head types installed. That could be utterly fascinating."*
Picks: XenoHead_Lasat / Mimbanese / Nelvaanian / Ortolan = **B** (new artpipe renders xeno_head_*_v1, XENOTYPE_CANON_CORRECTION_1).

## 1. Enact — DONE, f19fc83a9
- `art.py enact` dry run would have written the B renders OVER the borrowed textures — but those are shared:
  Cathar/Male_Head is also worn by RSW_RimMandrakeCathar + Zygerrian, Bothan/Male_Bothan by Bothan, kubaz/Male_Kubaz by Kubaz,
  and only the MALE file of each (females would keep the borrowed head). So: rulings ingested, then installed at NEW paths
  `RimMandrakeSW/Heads/<Species>/<Species>_Head_{south,east,north}.png` (art.py install, --reason script:fit_head_canvas.py).
- Renders fill 51-96% of canvas vs ~36% for vanilla heads (the sheet warned 1.5-2.7x too big): fitted by
  `src/RimMandrake/Utils/art/fit_head_canvas.py` (one uniform scale per species, south bbox height 240/512, chin at y=365). Raw bytes stay in the art store.
- New defs: HeadTypeDefs `RSW_{Lasat,Mimbanese,Nelvaanian,Ortolan}_Head` (genderless, requiredGenes) + genes `RSW_<Species>Head`; the four xenotypes swap
  RSW_CatharHead / RSW_Head_Devolved / RSW_BothanHead / RSW_Head_kubaz for them. Heads are full-colour paintings under the skin shader: skin colour will tint them (sheet flagged).
- Dragonsnake swim (owner: "Accept all"): installed at `DragonsnakeCanon/Dragonsnake_{A..D}_Swim_*` (the sheet slot was the BODY texture), def swim paths repointed.
- Grey Sea: RM_BrineElder B/C/D as random pool -> Graphic_Random folder `Things/Building/Natural/RM_BrineElder/` (it borrowed RM_SaltChimney, which other defs use). RM_BrineCrown held (coordinator: undecided) although his file has pool add B,C.

## 2. Which xenotypes use these heads
| head (texture) | gene | xenotypes before |
|---|---|---|
| Cathar/Male_Head | RSW_CatharHead | Cathar, Lasat, Zygerrian |
| Sov_tusken/HeadSandM | RSW_Head_Devolved | Mimbanese |
| Bothan/Male_Bothan | RSW_BothanHead | Bothan, Nelvaanian |
| kubaz/Male_Kubaz | RSW_Head_kubaz | Kubaz, Ortolan |
Binding: XenotypeDef genes -> GeneDef forcedHeadTypes -> HeadTypeDef graphicPath (+requiredGenes). Never edit a non-human head in Character Editor.

## 3. Restart — DONE (load 1)
- Game closed (taskkill, ./game going-down/down --why). origin/main == f19fc83a9 at deploy (nothing newer).
- Deployed: StarWarsRaces, SWBestiary, WeatherSuite, UtinniPatches, AshkarrWeatherSuite (49 files, incl. Auroral Umbra); `--compose biomes` (6: Cauldron DLL + srchash, BrineElder def + 3 PNGs); JawaBench `build.py --gm --apply` deployed (029b94b84b91).
- preflight `--purpose review --all`: NO-GO on pre-existing state (ModsConfig 374 = the acceptance-sweep list, not manifest.FULL 544; ashkarrflora not installed; 0Harmony fingerprint changed; SelfTest .cs compile_include; FlowWorks/Bestiary held files differ). None new from this deploy; launched on the same 374 list as the 10-20b baseline.
- Launched with launch_ready.py --profile full (receipt Transient/live_testing_2026-10-20d/launch_receipt.txt).
- Load 1 READY in 733 s (pid 46960). Harvest vs 10-20b: exceptions 3 (= prev, ours 0), xref ours 0, texture misses ours 0, config errors 13 (ours 0), patch fails 3 (ours 0), **0 new signatures**. WeatherSuite aurora postfixes + Cauldron Harmony 1/0 logged.

## 4. Head line-up — FINDING, second restart
- Site: `RM_TestSite_calm_v1_AREAFIX2` loaded with ignoreModCompatibility (4 donor mods absent; ~17 VEF "New faction" dialogs closed). Saves backed up to `D:\ClaudeWork\saves_backup_2026-10-20d` (364 files) first. Clock jumped to midday (time_set_ticks 15092), weather Clear locked.
- 🔴 **Every one of our species draws under Facial Animation's anime face.** FA's ignore list (`Config/Mod_1635901197_FacialAnimationMod.xml`, `IgnoreEnableAnimationForRaceXenoTypeListAA`) holds `Human-RimMandrake<Species>` for 68 species, but the xenotypes were renamed `RSW_RimMandrake<Species>` (tier rename 2026-08-31), so none match. The new heads are live (`set_pawn_appearance` read back `RSW_Mimbanese_Head`; PNGs deployed) but FA paints over them, and skin colour tints them.
- Fix: backed up the config (`Transient/live_testing_2026-10-20d/Mod_1635901197_FacialAnimationMod.before.xml`), added `Human-RSW_RimMandrake<Species>` for all 68 (old entries kept). `reload_mod_settings` + re-dirty + respawn did NOT change the render: FA reads the list at startup → second restart.
- `shoot_lineup_facings.py`: frame_cell_rect zooms IN past a 21-cell rect (viewRect read-back lies too); use `--zoom`.

- Load 2 READY in 856 s (pid 16456); FA list held (68 RSW_ entries). Menu-time log identical in kind to load 1; the +13 exceptions / Scribe refs in `harvest_load2.txt` all come from loading the test-site save with 4 donor mods absent (abstract Map/World/GameComponent, SurfaceLayer PostLoadInit) — not from new content. Ours: xref 0, texture misses 0.
- **Heads now draw** (FA off our species). Shots (zoom 13, midday, Clear, human pair for scale), in `D:\ClaudeWork\screenshots\2026-10-20\`:
  `heads_lineup_ALL_FACINGS.png` (south/east/north/west stacked close-ups), `heads_lineup_{south,east,north,west}.png` (full frame) + `_closeup.png` crops.
- Seen in the shots: Lasat/Nelvaanian roll gene HAIR that draws over the painted head (one Lasat, both Nelvaanians); Mimbanese head is full-colour red over a grey skin-tinted body; Ortolan east head sits high on the body; Lasat bodies are the huge existing body type.
- Keeper save: `XENO_HEADS_REVIEW_2026-10-20.rws` (14.0 MB, verified). Grid key L→R: Human×2, Lasat×2, Mimbanese×2, Nelvaanian×2, Ortolan×2 at x 62..80, z 70.

## 5. Game left up, bridge released — DONE
- Game UP on the review save, paused, healthy (./game RUNNING, bridge answers). Bridge released.
- Load 2 READY in 856 s (pid 16456); FA list held (68 RSW_ entries). Menu-time log identical in kind to load 1; the +13 exceptions / Scribe refs in `harvest_load2.txt` all come from loading the test-site save with 4 donor mods absent (abstract Map/World/GameComponent, SurfaceLayer PostLoadInit) — not from new content. Ours: xref 0, texture misses 0.
- **Heads now draw** (FA off our species). Shots (zoom 13, midday, Clear, human pair for scale), in `D:\ClaudeWork\screenshots\2026-10-20\`:
  `heads_lineup_ALL_FACINGS.png` (south/east/north/west stacked close-ups), `heads_lineup_{south,east,north,west}.png` (full frame) + `_closeup.png` crops.
- Seen in the shots: Lasat/Nelvaanian roll gene HAIR that draws over the painted head (one Lasat, both Nelvaanians); Mimbanese head is full-colour red over a grey skin-tinted body; Ortolan east head sits high on the body; Lasat bodies are the huge existing body type.
- Keeper save: `XENO_HEADS_REVIEW_2026-10-20.rws` (14.0 MB, verified). Grid key L→R: Human×2, Lasat×2, Mimbanese×2, Nelvaanian×2, Ortolan×2 at x 62..80, z 70.

## 5. Game left up, bridge released — DONE
- Game UP on the review save, paused, healthy (./game RUNNING, bridge answers). Bridge released.
