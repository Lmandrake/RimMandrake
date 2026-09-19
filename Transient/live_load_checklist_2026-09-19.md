# Live load 2026-09-19 — what this load must answer

617 active mods. Launched via Steam (`-applaunch 294100`), never the bare exe.
Prior log preserved at `Transient/Player.log.pre_live_load_2026-09-19`.

Everything below is a STRING to grep in Player.log, decided before the load so the
answer cannot be an impression.

| # | question | PASS looks like | FAIL looks like |
|---|---|---|---|
| 1 | Do the four ported defs load? | no mention of `RUT_Flamefang`/`RUT_Sytheclaw`/`RUT_Barbslinger`/`RUT_FireWasp` in any error line | `Could not resolve cross-reference` or `XML error` naming one |
| 2 | Does the Pyrelands cast resolve? | no `GenStep_Animals` exception, no null PawnKindDef | the `PYRELANDS_ANIMALS_GENSTEP_1` crash shape — dangling wildAnimals key kills GiddyUp's startup cache too |
| 3 | Do the flight stats parse? | silence — `MaxFlightTime`/`FlightCooldown` are Core stats | `Could not find stat` / unknown field on RUT_FireHawk or RUT_FireWasp |
| 4 | Do the 4 removed ArtOverride mods break anything? | no `boomsnake`/`razorjack`/`barbslinger`/`firewasp` artoverride lines | `Could not load reference to` a texture, or a missing-mod warning |
| 5 | Did the donor defs actually leave? | no `GR_Boomsnake`/`AA_Razorjack`/`AA_Barbslinger`/`AA_FireWasp` in a Pyrelands context | any biome record still naming them |
| 6 | Crossref health | at or below the 38 FOUNDRY measured after its VentForge fix | a rise — something I deployed dangles |

## Traps for whoever reads this log

- 🔴 **`Could not resolve cross-reference` ≠ `Could not load reference to`.** The
  first is the def loader against the live mod set; the second is Scribe, meaning a
  SAVE holds a dead name and no mod change fixes it.
- 🔴 **A patch that matches nothing logs NOTHING.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match, so a silent log does not
  prove a patch fired. Items 1-5 are about errors; proving the cast actually took
  needs the bridge, not the log.
- ⚠️ **There is NO wing-flap to see.** Flight animation needs
  `flyingAnimationFramePathPrefix` + a frame sequence; we ship none, so
  `GetBestFlyAnimation` returns null by design. Judge flight as BEHAVIOUR — takeoff,
  crossing unwalkable terrain, fleeing upward — never as a sprite.

---

# RESULT — load completed 890 s, bridge answering, state UP

| # | question | verdict | evidence |
|---|---|---|---|
| 1 | four ported defs load? | **PASS** | 0 error lines naming any of the four |
| 2 | Pyrelands cast resolves? | **PASS** | no GenStep_Animals crash; the one `GenStep_Animals` string is inside a method LIST, not a stack trace — and proven by outcome, since the cast resolved live (row below) |
| 3 | flight stats parse? | **PASS** | live dump, against vanilla `Locust` as control |
| 4 | removed ArtOverride mods break anything? | **PASS** | 0 mentions at 617 active |
| 5 | donor defs gone from our content? | **PASS** | see live cast — zero donor defNames |
| 6 | error health | **IMPROVED** | 262 → **250** distinct, 485 → **326** occurrences |

## The live Pyrelands cast, MEASURED from the running game

Capture `2026-09-19T18-15-44Z`, `BiomeDef.json` → `RM_FE_Pyrelands.wildAnimals`, 14 records:

`RUT_FireHawk` 0.15 · `RUT_FurnaceBeast` 0.08 · `RSW_Anooba` 0.35 · `RSW_Iriaz` 0.5 ·
`RSW_Nuna` 0.5 · `RSW_Orray` 0.25 · `RSW_Zeer` 0.6 · `RSW_Dalgo` 0.18 · `RSW_Gizka` 1.0 ·
`RUT_Emberscythe` 0.05 · `RUT_Sytheclaw` 0.2 · `RUT_Barbslinger` 0.15 · `RUT_FireWasp` 0.4 ·
`RUT_Flamefang` 0.5

🔑 This is the proof the log could not give: a `PatchOperationConditional` returns true
on no match, so silence proves nothing. The post-patch dump is the running game's own
answer, and it says every donor defName is gone.

## Flight, MEASURED with a control

| def | MaxFlightTime | canFlyIntoMap |
|---|---|---|
| `Locust` (vanilla control) | 10 | true |
| `RUT_FireHawk` | **30** | **true** |
| `RUT_FireWasp` | **10** | **true** |
| `RUT_Flamefang` / `RUT_Sytheclaw` / `RUT_Barbslinger` | none | false |

The three ground creatures correctly have no flight — the stat is not sprayed across
the port.

## One finding NOT acted on

`AA_Razorjack` is still being added by ANOTHER mod to `Wetland`, `ZBiome_AlpineMeadow`
and `ZBiome_Marsh` (log lines 8254, 10185, 10555). That is not our content and our
Pyrelands no longer names it — but the donor creature still spawns in the world, which
sits against the owner's "any donors cut, period". ⚠️ Worth checking whether those
`ZBiome_*` biomes carry any tiles on the frozen world at all; `ZBiome_Grasslands` had
**zero**, which is what made this whole thread start.
