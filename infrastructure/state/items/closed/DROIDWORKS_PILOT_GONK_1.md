# DROIDWORKS_PILOT_GONK_1 — gonk pilot, superseded-in-part

Filed purpose: "prove the DW race skeleton at n=1 before the generator emits
57." Stale by the time this item was worked — `DROIDWORKS_DEF_GENERATOR_1`
already ran and closed (commit `ee9c095b`), emitting 57/57 races and 80/80
kinds from `extraction.json`, **including** a GNK entry:
`DW_Race_OuterRim_GNKDroid` / `DW_OuterRim_GNKDroid` in
`src/Jawa/Droidworks/Defs/Races_OuterRim.xml` /
`src/Jawa/Droidworks/Defs/PawnKinds_OuterRim.xml`.

## Path taken: edited the existing generator entry in place (not a new race)

Per the item's own fork instructions, read the generator's GNK entry
critically against this item's spec. Two real defects found; both fixed.
No duplicate `DW_Race_GNK` created.

### Fix 1 — `baseHealthScale` was the literal string `"UNCERTAIN"`

`extraction.json`'s `OuterRim_GNKDroid` record carries
`"baseHealthScale": "UNCERTAIN"` with
`"baseHealthScaleSource": "UNCERTAIN - same as other animal-framework
droids"` — genuinely unknown at extraction time. The generator carried that
sentinel through **verbatim as XML text inside a float field**
(`<baseHealthScale>UNCERTAIN</baseHealthScale>`), which is not a valid float
and would break parsing of the whole def field.

Same defect confirmed in **7 other races** in the same file (`grep -n
UNCERTAIN src/Jawa/Droidworks/Defs/Races_OuterRim.xml` → 8 total hits before
this fix). Only GNK's is fixed here — the other 7 are unfixed, flagged as a
follow-up (not this item's scope: DUM, FX7, MSE, SalvageAssist, and 3 more
in that file all carry the identical broken sentinel).

Fix: replaced with `1.0`, matching the exact resolution the generator's own
closing note used for the analogous JDS null-`baseHealthScale` gap (engine
default is the genuine effective value absent better data) — with a comment
in `src/Jawa/Droidworks/Defs/Races_OuterRim.xml` explaining the sentinel bug
and citing the 7 siblings left unfixed.

### Fix 2 — `CompDroidDetonation` was never wired to any def

Confirmed by grep across the whole `Defs/` tree and `Patches/`: zero races
(of all 57) had a `<comps>` block referencing `Droidworks.
CompProperties_DroidDetonation`, despite 18 races carrying `energyDensity >
0` in their `DroidworksExtension` (per `DROIDWORKS_DEF_GENERATOR_1`'s
chassis table). The mechanic is built in C#
(`src/Jawa/Droidworks/Source/Droidworks/CompDroidDetonation.cs`) but was
dead code — attached nowhere.

Added `<li Class="Droidworks.CompProperties_DroidDetonation" />` under a new
`<comps>` block on `DW_Race_OuterRim_GNKDroid`, per the item's own framing
("the gonk detonates by nature" — BENCH). This is the **first** race to wire
the comp; rolling it out to the other 17 energyDensity>0 races is a
follow-up, not this item.

`chassisClass 6` / `powerFallPerDay 0.33` / `energyDensity 3` on
`DroidworksExtension` were already correct in the generator's output — match
the item's spec and BENCH's chassis table exactly. Left untouched.

## HAR needs-suppression finding (assumption 11, `design/Jawa/droidworks_assumptions.md`)

**HAR (`AlienRace.dll`, workshop `839005762`) has no bespoke needs-suppression
field of its own.** Searched the compiled assembly (no `.cs` source ships in
the workshop download) for need-related symbols: only vanilla passthroughs
(`NeedDef`, `Pawn_NeedsTracker`, `TryGetNeed`) and its own food/apparel/
building/gene/recipe *restriction* lists (`blackFoodList`, `whiteFoodList`,
`onlyEatRaceRestrictedFood`, `raceRestriction`, etc. — these gate what a race
may eat/wear/build, not whether it needs to).

**What actually suppresses Food/Rest is plain vanilla `RaceProperties`**,
available inside any `ThingDef_AlienRace`'s `<race>` block because it's
still the same `ThingDef.race` — no AlienRace-specific mechanism needed:
- `<race><needsRest>false</needsRest></race>` suppresses the Rest need.
- `<race><foodType>None</foodType></race>` suppresses the Food need.

Verified against vanilla's own mechanoid defs — confirmed by direct read of
`.../RimWorld/Data/Core/Defs/ThingDefs_Races/Races_Mechanoid.xml`, which sets
exactly these two fields on `Mech_*` races.

**Caveat, not fully answering assumption 11**: `needsRest`/`foodType` do not
touch Joy/Beauty/Comfort/Outdoors — those are gated in vanilla by
`RaceProperties.Intelligence == Humanlike`, a separate switch.
`DW_Race_Base` (`src/Jawa/Droidworks/Defs/Races_Base.xml`) currently
`ParentName="Human"` and does not override `intelligence`, so it inherits
Humanlike — meaning even after adding `needsRest=false`/`foodType=None`, DW
droids would still carry Joy/Beauty/Comfort/Outdoors needs. Full "droids
don't need anything organic" requires touching `intelligence` too, which has
its own knock-on effects (mood, work restrictions, social) not evaluated
here — genuinely a BENCH design call, not resolved by this finding alone.

**Not applied to any def.** This is investigation/documentation only, per
the item's own instruction ("even if the race itself needs rework
afterward"). `needsRest`/`foodType` were **not** added to
`DW_Race_OuterRim_GNKDroid` or `DW_Race_Base` — that decision affects all 57
races via the shared base and belongs to BENCH, not a single-race pilot
item.

## Validation

`skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Droidworks/Defs`
against `Mods`, `workshop/content/294100`, vanilla `Data` (added — the
generator's own closing note flagged this as needed for `DW_Race_Base`'s
`ParentName="Human"` to resolve), and the live capture
`2026-08-30T01-41-15Z` (the `2026-08-29T20-07-29Z` capture named in the item
spec still exists but is no longer the newest — used the newest instead):

**0 errors, 0 warnings across all 10 `Defs/` files** (`OK TOTAL - 10 file(s),
0 error(s), 0 warning(s)`). The only "info"-level notices are the
pre-existing, expected ones for every `Droidworks.*` `Class=` reference (the
validator's `--defs` scan doesn't see the compiled companion assembly, same
as the generator's own baseline run for `DroidworksExtension` on all 57
races) — now also printed once for the new `CompProperties_DroidDetonation`
reference on GNK, same class of expected notice, not a new defect.

Texture paths: `OuterRim/Droid/GNK` confirmed present on disk —
`src/Jawa/Droidworks/Textures/OuterRim/Droid/GNK_{south,north,east}.png`
plus `_southm/_northm/_eastm.png` mask variants, matching the def's
`<body><path>` declaration.

## Explicitly not done here (per item scope)

- The other 7 `baseHealthScale="UNCERTAIN"` races in
  `Races_OuterRim.xml` — flagged, not fixed.
- Rolling `CompDroidDetonation` out to the other 17 `energyDensity > 0`
  races — flagged, not done (this item proves the wiring on one race).
- `needsRest`/`foodType` suppression on `DW_Race_Base` or GNK — investigated
  and documented per the item's ask, not applied (BENCH design call,
  touches all 57 races and the Humanlike-intelligence question).
- No deploy, `ModsConfig.xml` untouched.

## criteria

- [x] Checked whether a GNK race already existed from the generator's run —
      it did (`DW_Race_OuterRim_GNKDroid`) — and edited it in place rather
      than authoring a duplicate.
- [x] `baseHealthScale` sentinel bug found and fixed for GNK, documented,
      7 sibling instances flagged not fixed.
- [x] `Droidworks.DroidworksExtension` confirmed already correct
      (chassisClass 6, powerFallPerDay 0.33, energyDensity 3).
- [x] `CompDroidDetonation` attached to GNK — first race in the mod to wire
      it; documented as pilot for a later rollout.
- [x] HAR needs-suppression investigated and documented precisely (field
      names, mechanism, vanilla-Mechanoid confirmation, the
      Humanlike-intelligence caveat) — not applied to any def.
- [x] `validate_patch.py` run with the newest live capture: 0 errors,
      0 warnings across all 10 Defs files.
- [x] Every texPath referenced by the GNK race confirmed present on disk.
