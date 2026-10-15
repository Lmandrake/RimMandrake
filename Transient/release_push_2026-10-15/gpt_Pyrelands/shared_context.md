# Pyrelands — shared context for every GPT consult (2026-10-15)

## What Pyrelands is
A RimWorld 1.6 fire biome (`RM_Pyrelands`, mod `src/RimMandrake/Pyrelands`, packageId mandrake.rimmandrake.pyrelands,
assembly FireEcologyHook) plus a Star Wars-tier companion (`src/RimUtinni/PyrelandsMechanics`: fire raids, flame
harvest, scorch-fruit harvesting, the fire rite). Content: deep-ash / scorchable terrains, a moving "burn line" fire
front, fire-born plants (embergrass, quickgrass, scorchfruit) that regrow after burns, an ash field that makes freshly
burned ground fertile (washed away early by black rain), fulgurite after dry lightning, a lightning breaker, sand
shovel / terrain dig, burrowing grazers that dive underground when fire approaches, furnace-beasts (heat-charged
giants that warm pawns/rooms, migrate as a world-map herd), fire-hawks that carry burning twigs ahead of a blaze,
Ullai / ashwallow / emberscythe and ported fauna, weathers (ash fall, black rain, cinderfall).

## Owner rulings that bound the design (not bugs)
- **One kind of heat, planet-wide** (owner 2026-09-29/30): *"It can't be a new "kind" of heat."* Sun exposure and
  biome heat feed VANILLA temperature -> vanilla Heatstroke, never a new heat hediff. Each extreme-heat biome declares a
  heat KIND (overhead sun / low sun / ambient); shade gear works per kind. A custom heat hediff would be a defect.
- **No animal or pawn ever vanishes without a readable sign.** A burrower that dives, a herd that leaves the map,
  a despawn — each must leave something a player can read (mote, letter, message, track, inspect string).
- **`Plant` only ticks `TickLong()`** (every 2000 ticks). A comp on a plant must override `CompTickLong()`;
  CompTick/CompTickRare on a plant never run. Anything plant-side that relies on finer ticks is a bug.
- **There is NO worldgen feature, in any version.** Players receive a savegame with one fixed hand-made world. A
  Pyrelands BiomeDef on 0 world tiles is expected (the planet is painted once, at the end). Do not report "biome
  never generated on the world" as a bug. Map generation (GenSteps on a Pyrelands tile) IS in scope.
- **Every DLC is assumed present** (Royalty, Ideology, Biotech, Anomaly, Odyssey). No "player lacks DLC" findings.
  `MayRequire` is for optional MODS only. **`MayRequire` on a top-level patch `<Operation>` is IGNORED** — must be
  guarded with PatchOperationFindMod/Conditional.
- **Every mod ships superb Mod Settings**: on/off per major feature, defaults = shipped behaviour, all-off degrades
  gracefully. Settings may be changed mid-game; that must be safe.
- **If it flies in the fiction it flies in the game** (MaxFlightTime stat, flip-book animation). Fire-hawk flight is
  NEVER live-tested without the owner present; propose state reads of `Pawn_FlightTracker`, not live visual checks.
- An animal belongs to one biome unless there is an in-game reason; the Pyrelands cast is fixed by an owner-ruled sheet.
- Names: `RM_`/`RSW_`/`RUT_` tiers. A patch that matches nothing logs nothing.

## How we debug RimWorld here (summary — full text in debug_process.md, inlined)
- Every mod has a functional script (`validation.py`, `northstar_site.py`, `preflight_pyrelands.py`) and is debugged
  through it via a bridge (RimBridge + JawaBench companion: static calls, spawn, tick advance, inspect).
- A cold load of the full 550-mod list is ~15-25 min; a 22-mod minimal tier ~90 s; a quicktest map ~90 s.
  Live checks reload a fixture save (`NS_Pyrelands_site_1_*`) — so **reload to an earlier tick with the same thing IDs
  happens many times per session**; a static table keyed by thing/pawn ID has bitten us twice (burrow nudge,
  scorchfruit roll).
- Offline checks: C# SelfTest/Fuzz projects (pure kernels: RM_BurnKernel, RM_FireEcoKernel, RM_FurnaceKernel,
  RM_BreakerKernel), `lint_pyrelands_defs.py`, `validate_patch.py`, RimSage decompiled vanilla source.
- A round/zero/alarming count is a query bug until a sanity probe proves the instrument can see.
- The live site sits at ~56 C, so vanilla heatstroke downs colonists in long advances (test environment fact).

## What we want from you
You are a senior RimWorld 1.6 C#/XML modder doing a pre-release hidden-behaviour hunt. Find things that will go
strange in real play that our scripted proofs would not catch.
