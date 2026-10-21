# FLIER_FRAMES_FILL_FIVE_GHOST_FLOCKS - research result (FOUNDRY, 2026-10-20, offline)

Question: five flier defs declare flip-book frames absent from `src/`. Are they broken in game? Evidence below; nothing was installed, deployed or flight-tested.

| def | owner mod | declared prefix / frames | PNGs exist elsewhere? | reachable in the 325-mod list? | class |
|---|---|---|---|---|---|
| RM_Kirruk | WeepingStones (live dump: `mandrake.rm.biomes`) | vanilla `Things/Pawn/Animal/Chicken/Chicken_Flying_`, 8 | Yes: vanilla `resources.assets` (def comment says shipped; not re-extracted here). Not a ghost. | yes, in BiomeDef `RM_WeepingStones` | NOT-A-DEFECT (HAS-ART-ELSEWHERE: vanilla) |
| RSW_Brezak | SWBestiary | `swanimals/Brezak/Brezak_Flying_`, 4 | donor bundle (see below), 12 PNGs (4 frames x east/north/south) | yes: vanilla TemperateForest/TropicalRainforest 0.04 (race.wildBiomes, in the live dump's BiomeDef spawn lists) | REACHABLE-BUT-MISSING, art available |
| RSW_Drexl | SWBestiary | `swanimals/Drexl/Drexl_Flying_`, 4 | donor bundle, 12 PNGs | yes: 4 vanilla forest/swamp biomes at 0.01 | REACHABLE-BUT-MISSING, art available |
| RSW_Thranta | SWBestiary | `swanimals/Thranta/Thranta_Flying_`, 4 | donor bundle, 12 PNGs | yes: swamps 0.8, ColdBog 0.6 and 4 more | REACHABLE-BUT-MISSING (most visible: common) |
| RSW_Tibidee | SWBestiary | `swanimals/Tibidee/Tibidee_Flying_`, 4 | donor bundle, 12 PNGs | yes: `RM_TheForge` 0.5 (WildAnimals_TheForge.xml) + 4 cold vanilla biomes at 0.01 | REACHABLE-BUT-MISSING (Forge animal) |

## Where the PNGs are
- Donor bundle `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3497316713\AssetBundles\Mlie_StarWarsAnimalCollection` (UnityPy scan: `assets/data/mlie.starwarsanimalcollection/textures/swanimals/<k>/<k>_flying_<1-4>_<east|north|south>.png`, 12 per def).
- Already extracted: `D:\ClaudeWork\rimmandrake\build\mlie_extract\swanimals\<k>\` (12 files per def, lowercase names). Scan script and output: `D:\ClaudeWork\rimmandrake\scratch\ghostflocks\scan.py`, `scan_out.txt`.
- NOT in: `src/` (or git history of `*_Flying*` for these), the deployed `Mods\SWBestiary\Textures\swanimals\<k>\` (body, `_Dessicated` only), the art ledger / artpipe store (`artpipe_state.py find`: 0 bound for Brezak/Drexl/Thranta; Tibidee's only bound job `gapall_Tibidee_v1` is body art). The donor mod `mlie.starwarsanimalcollection` is NOT in ModsConfig, so its bundle never serves these paths: the missing frames are real in the 325-mod list.

## What the game draws
UNMEASURED live (no bridge allowed). `Player.log` (Oct 20 18:49, SWBestiary loaded) has 0 lines naming the four prefixes and 0 `swanimals` texture errors, which says only that no flight draw happened in that session. Expectation, not measurement: the flip-book textures are looked up when the animal first flies; a miss gives the red "Could not load Texture2D" error and a null/bad texture for the flight frame, so these four animals either show a bad graphic or error-spam when they take off. Priority: Thranta, Tibidee (common/Forge), then Brezak, Drexl.

## Proposed install route (owner-gated: art is cosmetic, needs his permission; ports may reuse extracted donor art until regenerated, owner 2026-10-14)
For each of 48 files: restore case (`Brezak_Flying_1_east.png`), `python3 src/RimMandrake/Utils/art/art.py install --file <png in clone> --reason "donor flip-book frames for ported flier" SWBestiary swanimals/<K>/<K>_Flying_<n>_<facing>.png` (dry-run first; the store takes the PNG from inside the clone, so copy to a clone path first). Hawkbat/Convor frames were installed the same way.
Caveat: donor frames are separate repaints like the other ported sets, so expect them to also fail the body-drift audit (`flier_frame_registration_audit_2026-10-20.md`); not measured here. Installing is still better than ghost frames.
Alternative if the owner prefers no art: remove the four `flyingAnimation*` blocks (animals then do not animate flight).

Nothing here is UNREACHABLE; no def should be retired.
