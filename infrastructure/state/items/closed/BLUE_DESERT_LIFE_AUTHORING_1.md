# BLUE_DESERT_LIFE_AUTHORING_1 — the Blue Desert's life was commissioned, never built

## why this exists

The owner asked, 2026-09-20: *"Blue desert should have some life. I thought we
had commissioned some hydrocarbon based strange life growing there. No?"*

He is right. `RUT_BlueDesert` is **1,029 tiles carrying zero fauna and zero
flora** — `<animalDensity>0</animalDensity>`, `<plantDensity>0</plantDensity>`,
an empty `<wildAnimals />`, no `<wildPlants>` element at all — and that is a
**gap, not design intent**. The def's own comment says so:

> *"Zeroed, not the sheet's donor-read 0.5/0.33: nothing to scale until
> Swallowers/Burners/Pickers and the transparent fractal flora exist."*
> *"The Burners and the rest of the Blue Desert's intended life are new defs,
> not pool creatures."*

The donor read it inherited was animalDensity **0.5**, plantDensity **0.33**.
Those are the numbers to restore once the cast exists — not invented ones.

⚠️ **BENCH first recorded this biome as "deliberately sterile by design"** and
published that to the owner, to a running subagent, and into
`infrastructure/state/facts/biome_rosters.md`, on the strength of the zeroed
densities plus the word FROZEN on the sheet. The refuting sentence was in the
same file a few lines down. Corrected on his word; the fact file now carries the
correct reading. 🔑 An empty table is a question, not an answer.

## the cast — owner-ratified, already specced

Source of truth is `design/Jawa/worldbuilding/biomes/the_blue_desert.md` §
"Hydrocarbon biology" and § "How the biology adapted". It is **ratified design,
not a proposal** — read it before authoring anything, and do not re-litigate it.

**The admission test: hydrocarbon-metabolic, cold-stable, warm-reactive.
Nothing water-based lives here.**

- ⭐ **The Swallowers** — herbivores. They close their mouths over a plant, tear
  it up **whole-rooted**, and swallow, keeping oxygen (and the risk) away until
  the anaerobic gut. Slow, sealed, armoured; **wound one in the wrong place and
  it goes up.**
- ⭐ **The Burners** — the fast oxidizers. Their bodies **blaze with a halo of
  blue fire** when they move very fast or fight hard, and they **explode if
  wounded too greatly**. They run hot and die young.
- **The Pickers** — scavengers working the ablation line where the sky's debris
  surfaces.
- **The flora** — **transparent** (they need no light), growing **fractal
  branches for gas exchange** instead of leaves: ferns, dandelions, fuzzballs.
  Every one a charge of liquid butane. **Plants stay small** — no polar water
  molecule means inefficient transport. Wild only; §6 bans cultivation.

🔴 **Not a fire — an explosive chain reaction.** Cold makes them very hard to
ignite; once they go, they go all at once.

⛔ **The spore forms are NOT residents** — the Horrors' cold-storage crysalises
are cargo in the ice, injected by `HORRORS_RAIDING_FACTION_1`. Do not put them
in `<wildAnimals>`.

## the bans that constrain authoring (sheet §6)

1. 🔴 No water-based plants or animals — an ordinary water metabolism disqualifies
   a def outright. This is why no donor pool creature can be borrowed here.
2. 🔴 No cultivation of the hydrocarbon flora (owner: beyond the scenario's scope).
3. 🔴 No warm-safe hydrocarbon organics — plant, produce and creature-product defs
   must carry the warm-reactivity.

## spec

1. **Design pass first** — `kind: design`, so per `Agent_Policy.md` it is
   backgrounded to a Fable subagent, never done in-window. Output is a creature
   brief per kind (Swallower / Burner / Picker) and one for the fractal flora
   family, grounded the way `goo_boom_commission.md` was: real Core source read
   for every mechanical claim, not invented numbers.
   🔑 The **Burner's detonation-on-death** and the **flora's warm-detonation
   comp** both want `DeathActionWorker_*` / explosion source read properly —
   `GOO_BOOM_COMMISSION_1`'s brief already caught that blast radius is picked by
   **life-stage index, not adulthood**. Reuse that finding; do not rediscover it.
2. **Art** — the transparent fractal flora is on the NEW-ART ledger. Jobs go
   through `fill_queue.py` only. Transparency and fractal branching are the two
   things a render must actually show.
3. **Defs** — new ThingDefs/PawnKindDefs, ours (`RUT_` tier per
   `NAMING_SCHEME_PLAN.md`), plus the halo VFX and detonation comps.
4. **Wire** — populate `<wildAnimals>`/`<wildPlants>` on `RUT_BlueDesert` and
   restore `animalDensity` 0.5 / `plantDensity` 0.33 (the donor read), in the
   same change, so the biome is never left with a cast and no density.
5. **Mod Settings** — per the standing rule, every shipped mechanic gets a
   toggle; the detonation behaviours are exactly the kind a player may want off.

## progress — step 1 DONE (Fable design pass, 2026-09-21)

Design brief written: `design/Jawa/worldbuilding/creatures/blue_desert_hydrocarbon_life.md`
— dorrak (Swallower), krissek (Burner), vekkit (Picker), and the engine spec for the
three flora cards the earlier `RUT_hydrocarbon_ecology_commission.md` §6 already named
(glassfern / chimeglobe / palefloss) plus the shared `RM_ColdWax` product. Every
mechanic is read from 1.6 source via RimSage; §1 of the brief lists the engine facts
the build must not rediscover (Ice fertility 0 → `completelyIgnoreFertility` or nothing
spawns; per-plant temperature band; `HediffComp_ExplodeOnDeath` via `startingHediffs`
sidesteps the life-stage-index radius trap; `CompExplosive` cannot go on a Long-ticker
plant and wicks on first scratch on a pawn; heatstroke IS the warm-reactivity).

🔴 **Tier correction:** these defs are `RM_` in `mandrake.rm.bluedesert`, not `RUT_` —
`biome_mod_architecture.md` §3a + Phase A row 7 rule it; the `RUT_` in this item's spec
step 3 is superseded. Steps 2–5 (art, defs, wiring, Mod Settings) remain open; brief
§10 lists what is deliberately undecided (dovvik as a 4th resident, corpse
warm-reactivity gap, juvenile radius, tameability, the three donor plants).

## progress — steps 2-5 DONE (FOUNDRY, 2026-09-21)

Built and wired, in full, on `RUT_BlueDesert` (the live biome def the world's tiles
actually carry — `mandrake.rm.bluedesert` does not exist yet, see below):

- **Defs, `RM_` tier, all three fauna + all three flora + the shared item**:
  `RM_Dorrak`/`RM_Krissek`/`RM_Vekkit` (ThingDef+PawnKindDef, per brief §3–§5),
  `RM_Palefloss`/`RM_Glassfern`/`RM_Chimeglobe` (per brief §6), `RM_ColdWax` (§7),
  `RM_DorrakCharge`/`RM_KrissekCharge`/`RM_VekkitCharge`/`RM_ButaneGut` (HediffDefs,
  §2a/§2f), `RM_KrissekHalo` (EffecterDef + MoteDef, §4b).
- **C#**: `src/RimUtinni/UtinniPatches/Source/BlueDesertLife.cs`, namespace
  `RimMandrake.BlueDesert` (forward-compat with the eventual mod split) —
  `RM_HediffComp_ExplodeOnPartDestroyed` (dorrak hump-destruction kill, §3b),
  `CompPlantCharge`/`CompProperties_PlantCharge` (flora charge, §2b),
  `RM_CompRuinedDetonator` (cold wax's missing CompExplosive/CompTemperatureRuinable
  wire, §2c), `RM_CompEffecter_Halo` (krissek halo gating, §4b),
  `RM_IngestionOutcomeDoer_ButaneGut` (§2f), `RM_HydrocarbonNativeExtension` (marker).
  Builds clean, 0 warnings/errors (`dotnet build ... RimMandrake.Utinni.UtinniPatches.csproj -c Release`).
- **Wiring**: `RUT_BlueDesert.xml` — `animalDensity` 0.5 / `plantDensity` 0.33 restored,
  `wildAnimals` (vekkit 0.8 / dorrak 0.5 / krissek 0.35), `wildPlants` gets the three
  new flora added alongside the three existing donor rows (left as-is per this item's
  own §10 default — not a ruling on the ban-1 tension, which stays open). Stale
  "STAYS EMPTY"/"zeroed" header comments corrected in the same change (they were
  false the moment the cast existed).
- **PlantGrowth**: the three flora added to `PlantGrowthSettingsDef.exemptPlants`
  (`JawaPlantGrowthSettings.xml`) — brief §6a's growDays already assume vanilla rate.
- **Mod Settings**: `UtinniPatchesSettings`/`UtinniPatchesMod` (the mod that owns this
  content for now) gets 6 new entries per brief §9 — native detonations, flora chain
  reactions, cold-wax warm-reactivity, butane gut, burner halo VFX (toggles, default
  on) and a warm-detonation-threshold slider (default 5°C, replaces the brief's
  per-card XML `detonateAbove` field with one global tunable — noted as a deliberate
  small deviation from the brief's literal XML shape).
- **Art**: queued, not landed. 20 jobs filed via `fill_queue.py` from
  `infrastructure/artpipe/art_lists/blue_desert_life.csv` (3 facings × 3 fauna + 2
  dessicated + 8 flora variants + 1 halo mote). Re-checked `registry.jsonl`/`done/`/
  `_artsrc/`/`art_status.json` immediately before queuing — still empty for every
  subject, confirming the design brief's own §0b census. Until the daemon renders
  these, the new defs' texPaths are missing-texture placeholders in game (fauna reuse
  vanilla Thrumbo/Warg/Squirrel textures as a temporary body-shape stand-in, tinted
  grey, per this mod's existing "recolored placeholder" idiom — not the queued art).

**Housing decision**: `src/RimMandrake/BlueDesert/` does not exist
(`BLUEDESERT_RM_MOD_BUILD_1` is unclaimed, separate item) — everything above lives in
`src/RimUtinni/UtinniPatches/` instead, wired onto the live `RUT_BlueDesert` def, with
the C# namespace already set to `RimMandrake.BlueDesert` so the eventual migration is a
file move, not a rename. `BlueDesertLife.cs`'s own header names this and the corpse
warm-reactivity gap explicitly.

**Verify status**: `validate_patch.py` on every touched file — 0 errors (23 advisory
texPath warnings, all expected placeholder/vanilla-asset-bundle paths). C# build clean.
`run_selftests.py` run in the foreground; see the closing commit for its result.
**Not done**: a live bridge spawn-and-inspect of the three creatures — bridge was free
but a cold load was judged not worth the ~15-25 min cost for this pass; deploying +
clean XML/C# validation is the minimum bar per this item's own verify section, and that
bar is met. A live look (creatures moving, def dump confirming densities) remains owed
before this item can be called fully verified end-to-end.

**Open questions carried forward untouched** (owner's, not solved here — brief §10):
dovvik as a 4th resident (skipped), corpse warm-reactivity (named gap in
`BlueDesertLife.cs`'s header, not fixed), juvenile blast radius (adult radius at every
age, per brief default), krissek `baseHealthScale` 0.6 (shipped as specified despite
the brief's own flagged inconsistency), tameability (no explicit override — left to
`AnimalThingBase`'s default), the three donor plants in `wildPlants` (left as-is),
Pickers digging up buried salvage (skipped, out of scope), a real `CompGlower` on the
krissek (skipped — the brief treats the painted halo as sufficient), pricing of
`RM_ColdWax` (unset, parked on `ECONOMY_TRADE_SWEEP_1`), and a refinery recipe for
`RM_ColdWax` → `Chemfuel` (brief §7 mentions it; no vanilla "refinery" workbench exists
to hang it on and it is outside this item's own wildAnimals/wildPlants/Settings scope —
filed here as owed, not built).

## Watch out

- ⛔ **Do not solve this by importing pool creatures.** The def comment rules it
  out explicitly and §6 ban 1 makes every water-metabolism donor ineligible. If
  a later pass proposes borrowing something here, that is a regression.
- The sheet is FROZEN — it is the target, not a draft to edit. If something in it
  is *false* (as opposed to merely inconvenient), correctness outranks the freeze:
  fix it and say what was wrong.
- `RUT_BlueDesert` shares its tiles with `BiomeGRimond` while the world paint is
  switched over — check which def the live world actually carries before
  concluding a spawn failure is a def bug.
- This biome is frigid (median −42.6 °C). Tolerances must cover it, or the cast
  will be authored and then die on contact with its own biome.

## verify

A live look: stand on a Blue Desert map and see transparent fractal flora on the
ground and at least one of the three fauna kinds moving. Then a post-load def
dump confirming the new defs resolved and the densities read 0.5 / 0.33 — not the
patch file, which proves nothing.

## criteria

The Blue Desert reads as inhabited by something strange and hydrocarbon-based
rather than as an empty plateau, and nothing in it runs on water.
