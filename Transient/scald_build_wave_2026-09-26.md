# The Scald — offline build wave, 2026-09-26 (FOUNDRY background agent)

Status: COMPLETE for this pass. Six commits, all pushed. Everything OFFLINE — the game was
down and another wave held the bridge, so nothing was deployed and nothing was live-tested.

## 0. Starting state (read, not re-derived)
Authorities read in full: the frozen sheet `the_scald.md`, `scald_steam_and_hazards_spec.md`
(build order §8 is the spine of this pass), `scald_kit_spec.md` S1-S6, the roster JSON, and
all five filed items. Step 1 of the hazards spec (native immunity, `RM_OrganicScaldNative`)
was already built at `2f223f825`. The Scald's floor roster and `fishTypes` both work.

## 1. SCALD_MECHANICS_1 — PARTIAL (kit-adjacent progress, item stays `doing`)
Not worked head-on; four of its six mechanics moved anyway as a side effect of the other
items. S1 sky is now a real hazard rather than presentation; S2's condenser finally has the
art redo; S4's vent is `Graphic_Random` over two shapes; S6's wrecks went from one
silhouette to three. Its own remaining bar is unchanged and is a **live** bar — a quicktest
map showing forced steam with clear spells, a condenser producing on a vent and refusing
off one, a pawn swimming the margin without pathing through boil cells, wrecks salvageable
at burn cost, sails anchored to vents. None of that is reachable offline.

## 2. SCALD_WATER_AGITATION_FLECKS_1 — BUILT (`c2f437523`)
Acceptance bar was the owner's walk verdict: the boiling should have WAY MORE ripples.

**Root cause was structural, not a timid constant.** `RM_MapComponent_WaterAgitation`
fired ONE ripple per interval MAP-WIDE (~0.014 spawns/tick at its fastest). A camera
sees ~3% of a map and `FleckDef WaterRipple` lives ~4.1 s (fadeOutTime 4, solidTime 0,
alpha 0.2 — MEASURED from the def), so the expected count of ripples VISIBLE AT ANY
MOMENT was about one tenth of one. Re-tuning the old constants could never have fixed it.

- Rewritten to sample cells from `Find.CameraDriver.CurrentViewRect`: density is
  proportional to how much of the VIEW is agitated water, cost is bounded by the sample
  count regardless of map size (<= 0.5 fleck spawns/tick at 1x). Per-cell byte grid
  replaces the cell-list pools. Skips when this is not the current map.
- New Mod Settings slider `waterAgitationDensity` (0-4x, default 1x).
- Second lever, zero C#: terrain `fleckData`/`throwFleckChance` (AirPuff, angled up) on
  all six boil terrains (0.75 deep / 0.45 shallow) and the margin (0.08). This is the
  engine's own `SteadyEnvironmentEffects` route and is probably the bigger visual win.
- Burn numbers corrected to what they DO: `HediffGiver_Terrain` applies
  `Max(burnDamage, 3)`, so the authored 1/2 were both silently 3. Now 3 shallow / 4 deep,
  the latter being the 2026-09-25 deep-water ruling stated honestly.

OWED: deploy + a live look. The game was down for this pass.

## 3. SCALD_STEAM_WEATHER_DESIGN_1 — BUILT, steps 3-7 (`bd8c50caf`, `dd528abf4`)
Step 1 (native water immunity) was already built at `2f223f825`. This pass did 2 through 7
except the parts with a real missing dependency.

**Step 2** — terrain flecks + honest burn numbers: landed with item 2 above.

**Step 4, the exposure clock** — `RM_ScaldProtection` StatDef, `RUT_ScaldExposure` hediff
(four stages, lethal at the top, sized to the owner's card ruling: unprotected, dead in
under two days), and `RUT_ScaldSteamCarrier`, a SECOND permanent condition rather than a
field on the existing lock. Why: the lock's class has no `carrierHediff` and the class that
does has no periodic lapse, and extending either would change shared behaviour every other
kit depends on. They cannot fight — the carrier sets no `forcedWeather`, and
`ForcedWeather()` returns exactly `ext.forcedWeather` (read in full).
`GameCondition_EnvironmentalWeather` now honours `RM_MechanicGateExtension` the same way
`RM_GameCondition_WeatherPulse` already did, which is what makes the new S7 toggle real; a
def with no gate extension is never gated, so Miasma/Rot/Sump are untouched.

**Step 5, the gear ladder the owner typed** — `RM_Apparel_ScaldWrap` (Neolithic, no
research, 0.45), `RM_Apparel_BoilSuit` (Industrial, new `RM_ScaldWorking`, 0.85 +
`RM_ArmorRating_Scald` 0.60), and a patch putting 0.35/0.30 on the Odyssey vacsuit and
helmet. Ban 3 holds by construction: the comp clamps the summed stat to 1 and
`minDriveFactor` floors the clock at 8%, so boil-suit + helmet still runs.

**Step 3, the steam devil** — it scalded the Scald's own natives exactly as hard as a
colonist. `DamageCell` hit every Thing in the cell with no species check and the extension
carried no immune list at all. Added `immuneThingDefs`/`immunePawnKinds`/`affects` and a
Pawn-only `HazardTargeting.Affects` skip; empty lists reproduce the old behaviour exactly.

**Step 6, the overlay** — copy vanilla's fog material, swap its textures, tint it with
`ForcedOverlayColor`. Graceful: with the textures absent nothing is swapped and the class is
exactly today's look, so the art can land later with no code change. Two jobs filed.
🔴 **The spec's own draft snippet for this would NOT have compiled**:
`MaterialAllocator.Create(Material)` is `internal static` to Assembly-CSharp and is not
callable from a mod assembly. `new Material(src)` is what it does anyway.

**Step 7, the vent flash** — `RUT_WeatherEvent_VentFlash`, cribbed from vanilla's lightning
flash but with no shadow vector (a raking shadow reads as lightning, which the Scald never
has) and a lower, warmer ceiling. `eventMakers` at a ~4-hour mean, tunable in XML. New S1b
toggle, riding S1.

🔑 **THREE SEPARATE IMMUNITIES now exist and a Scald creature needs ALL THREE** — water via
`RM_OrganicScaldNative` on the race, steam via the exposure hediff's `immuneThingDefs`,
vortex via the steam devil's own list. Every new def says so in its header, and all ten
current Scald residents are in all three lists.

**Not done**: step 9 (a bespoke boil's-breath SoundDef — real audio content, nothing
blocking). And `RM_Apparel_RindCoat`, deliberately: `RM_RoyalRind`, the greatbole fruit item
and the butcher recipe do not exist anywhere in `src/` (re-checked 2026-09-26). They are
owed by `greatbole_harvest_spec.md` §9 items 4-5, and the coat goes in with them in one XML
pass. Shipping a recipe with no material to make it from would be worse than waiting.

## 4. SCALD_ART_UPGRADE_WAVE_1 — BUILT (`506c4ca63`)
**The whole wave's art was already finished and sitting unused.** 41 `scald2_*` renders in
`infrastructure/artpipe/_artsrc/` since 2026-09-25, every catch def still pointing at a
vanilla `ToxicMeat`/`Echeveria` placeholder. Zero new jobs queued for anything that had art.

- 9 catch items -> owned `Graphic_StackCount` folders, small/medium/large pile.
- 3 wreck defs -> three `Graphic_Random` variants each (was one); `shadowData` re-calibrated
  on the MEAN alpha bbox of the new 512px art, since one box serves three silhouettes.
  Hull (1.31,0.5,1.10) · Tank (1.35,0.5,1.06) · Frame (1.35,0.5,1.14).
- `RUT_ScaldVent` -> `Graphic_Random` over two rock-mouth shapes.
- `RUT_SteamCatch` -> the redo: no blue tint, vent visibly capped.

One real gap: `scald2_shullacatch_a` finished with **no PNG on disk** (empty `_artsrc` dir),
so `RM_ShullaCatch` ships 2 variants not 3. Refiled as `scald3_shullacatch_a` (pending,
priority 40) with install instructions in its `style_notes`.

Deliberately NOT rewired: `RM_Deepfire` (ex-`RM_RainbowPigment`). Its three
`scald2_rainbowpigment_*` renders are unruled and its own item waits on the owner's pick.

## 5. SEA_FISHABLES_ALIVE_IN_DEPTHS_1 (Scald portion) — BUILT (`293a05174`)
All nine `RM_TheScald` `fishTypes` entries now have a living counterpart in
`wildAnimals`. Seven new species in `RM_ScaldFloorFauna.xml`: eesh, doss, muddal,
thuum, karrash, ekkel, bladderboil — each written from its OWN catch item's existing
description, not invented. Six catch defs renamed to `RM_*Catch` to free the bare
species name; all call sites updated, zero duplicate defNames (verified by parse).
`RM_Bladderboil` ships RM_-tier, not the `RUT_Bladderboil` its own commission names
(that doc predates the tier split and Q11a; the name is the owner's own coinage, not
franchise IP). 21 real-art jobs filed; placeholders ship meanwhile.

## 6. Design gaps found — written down, NOT resolved

1. 🔴 **`eesh` and `shulla` are written as the same creature.** Both are the hot-white
   shoal sliver darting between the vent plumes, feeding the herds' dung-fall; both ship as
   a catch item and, now, as a living resident. That is two species, two catch rows and two
   roster rows for one idea. A content call for the owner — merge, or differentiate one of
   them. Nothing in this pass pre-empts it: both were authored faithfully to their own text.
2. **`RM_Apparel_RindCoat` is blocked on the Greentide.** See item 3 above. Not a gap in the
   Scald's design, a real cross-item dependency.
3. **`RUT_BladderboilBladder`** (the hydrocarbon commission's §14c butchery product) is
   unbuilt, and is now unblocked because the pawn exists.
4. **`RM_Deepfire`'s art is waiting on the owner, not on work.** Three finished
   `scald2_rainbowpigment_*` jar renders sit unruled in `_artsrc/`; that def's own file says
   the owner has not picked one. Not rewired here on purpose.
5. **`scald2_shullacatch_a` produced no PNG** — the one genuinely missing render in the art
   wave. Refiled as `scald3_shullacatch_a`.
6. **A seat-resolution oddity, flagged not fixed**: `rimflow note` from this window wrote to
   `infrastructure/state/ledger/events/BENCH.jsonl`, not `FOUNDRY.jsonl`, although this pass
   ran as FOUNDRY-style work on FOUNDRY-owned items. The notes are correct and committed;
   only the shard they landed in is surprising.

## 7. Commits (all pushed)

| sha | what |
|---|---|
| `506c4ca63` | Scald art wave 2 wired in — stack variants, wreck/vent variety, steam-catch redo |
| `c2f437523` | ripples where the camera is; steam off the water; honest burn numbers |
| `293a05174` | seven living residents for the seven catch-only species; six catch defs renamed |
| `bd8c50caf` | the exposure clock, the gear ladder, the steam-devil species gate |
| `dd528abf4` | custom steam overlay route + the map-wide vent flash |
| `09a7cb3fb` | ledger notes |

## 8. What is owed, in order
1. **Deploy and look.** `deploy_custom_mods.py --mod TerminalBiomes --apply` and `--mod
   EnvironmentalHazards --apply` (the DLL half only writes while the game is closed), then a
   quicktest on `RM_TheScald`. Nothing in this pass has been seen running.
2. **The owner's eye on the boil.** The ripple/steam change exists to answer his walk
   verdict; only he can say whether it now reads as boiling. The density slider is there so
   the answer can be "more" without another build.
3. The 23 artpipe jobs filed here (21 creature facings + 2 overlay tiles + 1 shulla refile)
   land in `_artsrc/` on the daemon's own schedule and need installing and wiring.
4. `SCALD_MECHANICS_1`'s live bar — the only thing left on that item, and it needs a map.
