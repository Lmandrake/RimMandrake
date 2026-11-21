# Where our art for vanilla electrical buildings lives

Item `RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART`. Written 2026-11-20 by a BENCH helper of the Conductor, on the
owner's order of the same day during his Gimme Some Slack walk (full text:
`D:\ClaudeWork\rimmandrake\conductor\gss_walk_20261120_his_words.md`, message 2): *"Do a design pass to see whether that
belongs in this mod or in a RimMandrake existing or new mod: design and decide and advise, then present me with
arguments why/where/whynot."*

## Decision

**Split along the line an electrician would draw.** Gimme Some Slack (GSS) keeps the electrical *installation*: the
wires, switches, poles and the light fixtures on them (pole lamps, the standing lamp it already styles, and now the
wall lamp). A **new RimMandrake mod, "RimMandrake: Machine Looks"** (`mandrake.rm.machinelooks`, folder
`src/RimMandrake/MachineLooks/`, namespace `RimMandrake.MachineLooks`, prefix `RM_`), takes the *appliances*: battery,
heater, cooler, benches, research benches, turrets, televisions, generators and solar panels. Both offer the same four
looks (Scrapper, Industrial, Modern, Futuristic) through the shared picker core and the same look icons.

"Restyle this run" does **not** repaint appliances. A machine ends a run (GSS design 2.1, already true for the standing
lamp), so each appliance keeps the look picked for it. Machine Looks has its own "Restyle this machine" button and a
default-look setting; when GSS is loaded, that default **follows GSS's default look** unless the player sets it apart, so
one setting dresses a whole base.

The **strongest argument against** (the blind second reviewer's, below): any boundary inside "electrical things" is a
line the player cannot see. A player who wants an all-Industrial base meets two mods, two settings pages and two
buttons, and the battery, which conducts power exactly like a conduit, sits on the "machine" side. That reviewer would put
the wall lamp in the new mod too and leave only the standing lamp in GSS as a grandfathered exception. Why this pick
still stands: lighting fixtures already hang on GSS's poles (the pole lamp masts have four looks in GSS), so splitting
"lights" across two mods is the line a player *would* notice, while "the electrician installs it" vs "you buy it and plug
it in" is a line most players already carry. If the owner prefers the reviewer's line, only the wall lamp's home moves; no
art changes.

## The inventory (measured)

Source: the frozen official def dump, `OFFICIAL-2026-08-29` (capture `2026-08-29T13-30-02Z`, 584-mod list), queried
through `measure build --only ThingDef` into SQLite, never a scan. A def is counted when one of its comps is
`CompProperties_Power` or `CompProperties_Battery` and its package is `ludeon.*` (Core plus the five DLC); blueprints,
frames and minified things are left out. `drawSize` comes from the newest live capture (`2026-11-20T19-51-00Z`), because
the official capture does not write Vector2 fields; for vanilla defs it is Ludeon's XML value (Battery `(2,3)` checked
against `Data/Core/Defs/ThingDefs_Buildings/Buildings_Power.xml`). Picture sizes come from the extracted vanilla art
(`D:\Luke\dev\RimMandrake\observed\inventory\bundle_textures`), south facing, else north. Script and full rows:
`power_census.py`, `power_census.json` (this folder).

**106 defs [measured]**, 97 of them buildable. Only **7 of 106** reach our 128 px per cell; almost all vanilla power art
is 64 px per cell. 4 rows are UNMEASURED (no extracted picture under their texPath: linked conduit atlases, the
hydroponics basin, the atmospheric heater, the ship reactor).

| group | defs (buildable) | each: def, vanilla picture px, drawSize, px per cell |
|---|---|---|
| lighting | 5 (5) | FloodLight 256x256 @2.5x2.5 = 102.4 · StandingLamp 64x64 @1x1 = 64 · SunLamp 64x64 @1x1 = 64 · WallLamp 64x64 @1x1 = 64 · LightBall (Ideology) 64x64 @1x1 = 64 |
| climate | 3 (3) | Cooler 64x64 @1x1 = 64 · Heater 64x64 @1x1 = 64 · AtmosphericHeater (Anomaly) UNMEASURED |
| production | 13 (11) | see `power_census.json`: the Core electric stove, smithy, smelter, tailor bench, machining table (224x96 @3.5x1.5 = 64), fabrication bench (448x256 @7x4 = 64), biofuel refinery, crematorium (192x128 @3x2 = 64); Anomaly bioferrite shaper, serum lab; Biotech subcore encoder, mech gestators (the gestators are 128) |
| research | 2 (2) | HiTechResearchBench 448x256 @7x4 = 64 · MultiAnalyzer 128x128 @2.47 = 51.8 |
| turret | 5 (5) | autocannon, uranium slug, rocketswarm 128x128 @1.5 = 85.3 · mini-turret, foam turret 192x192 @3 = 64 (bases; each turret also draws a separate gun top) |
| entertainment | 3 (3) | FlatscreenTelevision 128x64 @2x1 = 64 · MegascreenTelevision 256x64 @3x1 = 85.3 · TubeTelevision 64x64 @1x1 = 64 |
| generation | 17 (12) | Core chemfuel and wood-fired 128x128 @2 = 64, solar 256x256 @4 = 64, wind turbine 256x128 @5x2 = 51.2, watermill 320x384 @5x6 = 64, geothermal 512x512 @6 = 85.3; DLC toxifier, bioferrite, electroharvester, gravship engine and reactor, gravcore cell, and non-buildable power cells |
| storage | 1 (1) | Battery 128x256 @2x3 = 64 |
| network | 9 (9) | PowerConduit, WaterproofConduit, HiddenConduit (linked atlases, UNMEASURED) · PowerSwitch 64x64 = 64 · five ship parts |
| other | 48 (41) | Biotech gene and mech machines (15), Anomaly devices (6), Ideology (5), Odyssey (4), comms console, deep drill, scanners, nutrient paste dispenser, moisture pump, autodoor and more |

The full per-def line for every group, including every DLC def, is in `power_census_table.md` (generated from the JSON).

## What already exists, and what collides

- **GSS already styles three kinds of vanilla thing** through the engine's own style field (a `ThingStyleDef` per look,
  `CompStyleable` patched onto `PowerConduit`/`PowerSwitch`; `StandingLamp` has it from vanilla): conduit runs, the power
  switch and the standing lamp. Its overhead poles, pole lamps, tap clamps and wall brackets have per-look art too.
- **The picker core is shared source**, `src/RimMandrake/_Shared/StylePicker/StylePickerCore.cs`, linked into GSS and
  FlowWorks (hoses and pipes). A third consumer is the design it was built for.
- **The style field is contested [measured on the live dump].** Ideology's own styles (Hindu, Morbid, Totemic, Spikecore,
  Rustic, Techist) and the Alpha Memes mod (Cubic, Flesh, Horaxian, Kemetic, Mesoamerican, Scavenger, SteampunkRevival)
  and Vanilla Memes Expanded (Serketist) already restyle the standing lamp, wall lamp, sun lamp, flood light, cooler,
  wood-fired and chemfuel generators and the solar generator through the same field. Whatever the home, our picker must
  not silently overwrite an ideoligion's style, and an ideoligion style must not silently overwrite a picked look.
- **No other active mod retextures these buildings [measured]:** on the owner's 315-mod list only GSS changed a power
  def's texPath (conduits, switch). CommonSense adds comps to some benches, PipeSystem to the chemfuel generator,
  ItemControl to turrets; none of these touches graphics.
- **Turrets draw their gun top separately**; the style system swaps only the base. A styled turret needs C# for its top.
- **The standing lamp's four GSS looks are 128x128 on a 1-cell lamp = 128 px per cell [measured]**, at the standard.
  The low-resolution lamp a player sees is the *unstyled* lamp, which draws vanilla's 64 px art: any lamp built before a
  look was picked, or one an ideoligion styled.

## The options

### A. Everything in Gimme Some Slack (its next version)

- **Player gets:** one mod that dresses all power things in one look; one settings page; "Restyle this run" could
  reach appliances.
- **Conflict risk:** every collision above lands on GSS, a mod whose core job (cords that sag, plug and break) has
  nothing to do with a television's casing. A bad style interaction would block GSS's cable fixes.
- **Looks:** the run repaint could include appliances, but GSS's own rule says machines end runs; repainting them would
  break that rule for the lamp too.
- **Settings:** a GSS switch per appliance group; defaults equal shipped behaviour (all off until the art passes).
- **Tier and names:** RimMandrake tier, existing `mandrake.rm.gimmesomeslack`.
- **Effort:** the same art as any option (about 250 pictures for the Core set, below), plus GSS's acceptance bars and
  tests roughly double; every GSS walk then reviews a base's worth of machines.
- **GSS 0.1.0:** untouched (a Divergent addition goes to 0.2.0), but GSS 0.2.0 becomes two products under one number.

### B. A new mod for every vanilla powered building; GSS keeps only what it has

- **Player gets:** "GSS for wiring, Machine Looks for buildings". GSS's standing lamp stays as a grandfathered exception.
- **Conflict risk:** contained in a mod that can be switched off or removed without losing cables.
- **Looks:** each appliance keeps its own look; a default-look setting; no run repaint.
- **Settings:** a switch per group (lighting, climate, production, research, turrets, entertainment, generation,
  storage); defaults equal shipped behaviour; the game is vanilla with every switch off.
- **Tier and names:** `mandrake.rm.machinelooks`, `RimMandrake.MachineLooks`, `RM_`.
- **Effort:** a new mod's skeleton (About, settings, the picker as a third consumer, `CompStyleable` patches, style defs
  per def per look), then art and checks group by group.
- **GSS 0.1.0:** untouched; GSS needs nothing new.
- **Weak point:** lighting is split. The pole lamps and the standing lamp are in GSS, the wall lamp, sun lamp and flood
  light would be in Machine Looks.

### C. Split by installation vs appliance (the pick)

As B, except GSS also takes the **wall lamp** (and later the sun lamp and flood light if he wants them styled), so all
light fixtures sit with the poles and lamp masts that already carry looks. Machine Looks takes the battery and every
appliance. GSS's share is a Divergent addition for its next version (0.2.0); 0.1.0's bars do not move.

### D. Widen an existing generic mod

The only generic appearance mod is **Rust Chrome** (`mandrake.rm.rustchrome`), a UI skin that works by texture
override. Override replaces one picture for everyone: it cannot offer four looks per building, and it would replace the
vanilla picture under every ideoligion style too. **Rejected:** it cannot deliver the owner's per-build looks.
`MandrakePatches` holds compatibility fixes and is the wrong place for an art collection.

## The blind second pass

GPT (through `gpt_consult.py`, 2026-11-20) was given the facts and the four options, picked blind, then critiqued this
pick. **Its blind pick was B**, with the standing lamp grandfathered in GSS. It found C defensible ("its strongest
defence is continuity") but would move the battery and wall lamp to the new mod, because "electrical topology is a poor
boundary for ownership of artwork". That argument moved the **battery** out of GSS in this pick (the first draft had
it in GSS because it conducts power). It did not move the wall lamp, for the lighting reason in the Decision. It added
three points this design adopts:

1. **Run traversal and repaint are separate rules.** A battery conducting power does not make it a run member for
   "Restyle this run". Machine Looks never changes vanilla power behaviour.
2. **Turrets need an early prototype** of the top graphic before their art is commissioned; a styled base alone does
   not deliver the look.
3. **Removing a mod mid-save leaves style defNames the save cannot resolve.** Keep every `ThingStyleDef` defName stable,
   and give each mod a "clear this mod's looks" action that leaves other providers' styles alone; test it with a
   save/load before 1.0.0.

## The wider set: what it is and what it takes

**The Core set his words name**, buildable: heater, cooler, eight production benches, the hi-tech research bench and
multi-analyzer, five turrets, three televisions, six generators (chemfuel, wood-fired, solar, wind, geothermal,
watermill), sun lamp and flood light: **28 defs, about 63 pictures per look (every Graphic_Multi building has three
facings; each turret counts one more for its gun top), so about 252 pictures for four looks [measured from
`power_census.json`; turret tops estimated]**. The DLC add 10 more buildable defs (about 72 pictures).

What it takes, in order:

1. Create Machine Looks through the Maturation Pipeline (Design Version 0.1.0), with the battery as its first def: the
   battery's art from this item is ready for it.
2. The code skeleton once: settings, the picker as a third consumer, a `CompStyleable` patch per def that lacks it,
   one `ThingStyleDef` per def per look (`<Def>_<Look>`, as GSS does), the ideoligion-style rule.
3. Art per group, at 128 px per cell (`drawSize x 128`), one look family at a time, each judged before install.
4. The turret top prototype before any turret art.

GSS's share (the wall lamp's `ThingStyleDef`s and picker registration, the pole button icons, the look icons in the
style menu) is ordinary GSS next-version work; the art is already in place from this item.

## Part 2, the first commissions (this item)

See `commissions.md` in this folder for what was rendered, judged and installed, and where.

## For Mandrake

- **Where:** the wires, switches, poles and the lights on them stay in **Gimme Some Slack**. The machines (battery,
  heater, cooler, benches, research benches, turrets, televisions, generators, solar panels) go in a **new mod,
  "Machine Looks"**. Both offer the same four looks with the same icons, and the new mod copies Gimme Some Slack's
  default look when both are loaded, so you pick a look once.
- **Why:** the four looks already work on Gimme Some Slack's pieces, and the light fixtures hang on its poles. Machines
  are a much bigger collection (about 250 new pictures for the Core set alone) that has nothing to do with cords. Keeping
  them apart means a problem with a machine's look never holds up a cable fix, each mod passes its own walk, and a
  player who wants the cords but not the machine art just leaves one mod off.
- **Why not:** you get two mods and two settings pages for one idea, and the line between them ("the electrician
  installs it" vs "you plug it in") is ours, not the game's. The independent reviewer would have put the wall lamp with
  the machines too; I kept it with the other lights.
- **Why not all in Gimme Some Slack:** it doubles that mod's tests and walk for something that is not about wiring, and
  every style collision with Ideology and other mods would land on it.
- **Why not an old mod:** our only appearance mod, Rust Chrome, swaps one picture for everyone; it cannot give you four
  looks to choose from.
- **A thing to know (terms):** a *look* is one of Scrapper, Industrial, Modern, Futuristic. The game keeps one *style*
  slot per building; Ideology's styles (Morbid, Totemic and others) and the Alpha Memes mod already use that same slot
  for lamps, coolers and generators, so either mod must not silently overwrite the other's choice. *Restyle this run*
  repaints a connected stretch of wire; it will not repaint machines, which keep the look you picked for each one.
- **What it costs:** about 250 pictures for the Core machines you named, plus the new mod's settings and code, plus a
  small C# piece for turret guns. Nothing here changes Gimme Some Slack 0.1.0, which passed today.
