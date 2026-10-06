# Pyrelands sheet close: progress, 2026-10-05

The owner typed "Finished pyrelands". Sheet: `Transient/biome_ffar/pyrelands_sheet_2026-10-05.decisions.json` (RM_Pyrelands).

## ADVICE (answering "Please advise and assist")

- **The walking hawk is fixed now.** You picked M, the wings-folded walking bird. It is now the fire-hawk's ground art
  in all three directions. The old wings-out picture is gone, and so are the old pictures you marked for purge.
- **The hawk already flies with a 5-frame wing-beat in game.** That set is columns H–L on the sheet. Columns B–F
  are a second, unused 5-frame set. The sheet showed each frame as if it were a separate body choice, which is why
  you couldn't find a "flying" option. That was a sheet-layout problem, not missing art.
- **Queued now: 48 new flight frames** (8 frames × 3 directions × 2 creatures), made from the pictures you picked so
  they are the same animal. The fire-hawk's frames start from M. The fire-wasp's frames start from A, which stays its
  ground art. Each frame is drawn from the one before it, going from wings tucked to fully spread and back.
- **What you'll be asked:** once the frames finish, one small sheet with both flyers. It will show the
  ground art, then a flight strip of frames 1–8 for each direction, and you pick or redo per creature. This
  sheet does not exist yet. The sheet tool can't build a brand-new sheet or show frame strips (see "Review
  sheet" below), and that is filed.
- **When the hawk looks right in game:** walking, at the next game restart (no deploy has run yet). Flying with
  the new frames: after you pick them and they are installed and wired. Until then it flies with the current 5-frame set.

## Plain installs: DONE
Ingest: stamped ruled. `art.py ingest` recorded 2 rulings (FireHawk M, Orray F; the other touched rows only
purged) and 45 purges. The two live FireHawk pictures were purged after M replaced them. **1 purge refused:**
Gizka `3599473822d4` is still live at `src/RimStarWars/GizkaArtOverride/Textures/swanimals/Gizka/GizkaW_south.png`,
the female south. It needs a replacement installed first. Left for his next Gizka pass.
- RM_Barbslinger A, RM_FE_Plant_Quickgrass A, RM_FurnaceBeast A, RSW_Gizka A: already live, nothing to copy.
- RSW_Orray F: installed into `src/RimStarWars/OrrayArtOverride/Textures/swanimals/Orray/Orray_{east,north,south}.png` (ruling b7de786ff0711b090a5f).
- RSW_Dalgo B: B was the shadowed DalgoArtOverride copy, and the game showed SWBestiary's. B is now installed into
  `src/RimStarWars/SWBestiary/Textures/swanimals/Dalgo/Dalgo_*.png`, so both mods ship B.
- RM_FireHawk M: installed into `src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_{east,north,south}.png` (ruling 28fbf60fa474a916dd98).
- placeholder_detect.py `file` on all 23 live PNGs of these 8 rows: 23 `real`.
- Not deployed (no deploy run; the game reads the Mods folder).

## Flyer inventory
- **RM_FireHawk** (`src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsFauna.xml`): MaxFlightTime 30,
  FlightCooldown 5, flightStartChanceOnJobStart 0.15, flightSpeedFactor 2.5, canFlyIntoMap and canLeaveMapFlying,
  body vanilla `Bird`, no renderTree. The PawnKindDef has a 5-frame flip-book wired: prefix `.../FireHawk/FireHawk_Flying_`,
  frameCount 5, ticksPerFrame 2, drawSize 1.35, multiplier false. Its 15 PNGs are on disk (artpipe `rut_firehawk_flying_{1..5}`,
  sheet columns H–L). A second set, `rut_firehawk_flying_v2_{1..5}` (B–F), is unused. Grounded sets: A (old live,
  wings out), G grounded_v3 (purged), M wingsplit body (now live), N single south.
- **Wing-split art:** `FireHawk_Wing_*` / `FireHawk_Body_*` were already deleted from the mod on 2026-09-19. Only the
  artpipe source remains (`_artpipe/_artsrc/firehawk_wingsplit_v1_*/{body,wings}.png`). M is that *body* half, which is
  now the walking art. The wings half is unused and stays out.
- **Spastic BodyDef/PawnRenderTree:** already removed on 2026-09-19 (`RUT_FireHawkRenderTree.xml` deleted, body reverted
  to `Bird`). See `infrastructure/state/items/FIREHAWK_FLIGHT_BEHAVIOR_1.md`.
- **RM_FireWasp** (`src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsPortedFauna.xml`): MaxFlightTime 10,
  FlightCooldown 5, flightStartChanceOnJobStart 0.1, flightSpeedFactor 2.5, canFlyIntoMap, body BeetleLike, adult
  drawSize 2. **No flip-book.** Grounded A is live in all 3 directions (`pyrelands_firewasp_v3`).
  Note: the same texPath is also used by RM_GreatboleGrub and RM_Skerrel.

## Grounded art: DONE
FireHawk M has all three directions, so nothing needed deriving. FireWasp A is already live.

## Flying flip-book jobs: QUEUED (48)
File: `Transient/biome_ffar/pyrelands_flyer_flipbook_jobs_2026-10-05.json`. Ids are `pyrelands_{firehawk,firewasp}_flight8_<N>_<facing>`.
Item FLYER_FLIPBOOK_ART_1, owner_note is his verbatim note, and no facing-set words appear in any prompt.
- **artpipe cannot express a frame sequence.** `derive_from` must name a *finished artpipe job*, and neither pick has a
  done job (the wingsplit render has no done manifest; the firewasp_v3 PNGs are not in `_artsrc`). So:
  frame 1 east attaches the installed grounded pick as `canon_reference`, and its prompt says it is the accepted
  individual (the Mynock precedent). Frame 1 south and north use `derive_from` frame 1 east. Frame N of each
  direction uses `derive_from` frame N-1 of the same direction, so each frame is derived from the previous one.
  Risk: the chain can drift; compare frame 8 against frame 1.
- The jobs carry no `install_to`. Their `target_texpath` is the ledger's flying slot (`..._Flying_`), which is only for
  subject binding. Planned install is to a NEW prefix, so the live 5-frame hawk set stays untouched until he picks:
  `Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Fly_<N>_<dir>.png` and `.../FireWasp/FireWasp_Fly_<N>_<dir>.png`.
- XML to add once the frames are picked and installed. It goes as a sibling of `<lifeStages>`, and on the hawk
  it replaces the existing 5-frame block:
```xml
<!-- RM_FireHawk PawnKindDef -->
<flyingAnimationFramePathPrefix>Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Fly_</flyingAnimationFramePathPrefix>
<flyingAnimationFrameCount>8</flyingAnimationFrameCount>
<flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
<flyingAnimationDrawSize>1.35</flyingAnimationDrawSize>
<flyingAnimationDrawSizeIsMultiplier>false</flyingAnimationDrawSizeIsMultiplier>
<flyingAnimationInheritColors>true</flyingAnimationInheritColors>
<!-- RM_FireWasp PawnKindDef -->
<flyingAnimationFramePathPrefix>Things/Pawn/Animal/Pyrelands/FireWasp/FireWasp_Fly_</flyingAnimationFramePathPrefix>
<flyingAnimationFrameCount>8</flyingAnimationFrameCount>
<flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
<flyingAnimationDrawSize>2</flyingAnimationDrawSize>
<flyingAnimationDrawSizeIsMultiplier>false</flyingAnimationDrawSizeIsMultiplier>
<flyingAnimationInheritColors>true</flyingAnimationInheritColors>
```
After wiring, verify with a `Pawn_FlightTracker` state read, never an unattended live flight hunt.

## Wiring removal plan: NOTHING LEFT TO REMOVE
The Spastic render tree, the custom BodyDef and the wing PNGs were removed on 2026-09-19 (FIREHAWK_FLIGHT_BEHAVIOR_1). The hawk is
`Bird` with a plain texPath. The only leftover is the wingsplit *wings* PNG in the artpipe source dir, which nothing references.

## Review sheet: BLOCKED BY THE TOOL (tools not edited, as briefed)
- The `art_sheet.py --res` mode builds a sheet, but `scaled_review_gate.py` fails it on req 1/2/4/5: it is not a
  biome sheet, so it has no census, ground colour or scale panel. That sheet was deleted.
- The `art_sheet.py --biome RM_Pyrelands --census <flyers-only census>` mode passed everything except **req 9/chk:
  "a decisions file exists to review"**. `generate_biome` runs the gate *before* it writes the decisions file, so a
  sheet at a NEW path can never pass on its first build. Not worked around (no hand-made stub). That sheet was also deleted.
- **Missing from the tool:** (1) the first-build bootstrap above; (2) labelled sections within a row ("GROUNDED /
  walking" vs "FLYING flip-book"); (3) a frame-strip layout for frames 1–8 per direction. Today a flip-book slot shows
  every frame as its own pick column, which is exactly what confused him on this sheet.
  (4) The ledger slot `RM_FireHawk/flying` has 0 variants: the installed `FireHawk_Flying_*` frames were never imported, so even a
  working sheet would show nothing in that row.

## Flyer census / item: DONE
64 own creatures have MaxFlightTime > 0, and **36 have no flip-book**. Filed `FLYER_FLIPBOOK_ART_1` (BENCH, spec
`infrastructure/state/items/FLYER_FLIPBOOK_ART_1.md`).
