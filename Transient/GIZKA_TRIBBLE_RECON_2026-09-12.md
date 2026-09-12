# GIZKA_TRIBBLE_ADAPTATION_1 — recon (Parts 1-2 only)

Read-only evidence pass. Nothing activated, nothing edited, no other file written.
Companion doc already on file: `design/RimStarWars/gizka_ship_pest_spec.md` (dated
2026-09-08) — this recon independently re-verifies its Part 1/2 claims and finds
one of them stale (Part 2, art).

## Part 1 — the Tribble module (inactive, examined, never activated)

**Identity** — CONFIRMED (read directly).
- Workshop id: `2400590961`, folder `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2400590961`
- `About/About.xml`: name "Tribble Trouble", author Zylle, `packageId zylle.TribbleTrouble`,
  requires `brrainz.harmony`, supports 1.1-1.6 (separate `1.1/`.."1.6/" folders, each
  with its own `Assemblies/ZTribble.dll` + `Defs/`).
- CONFIRMED absent from the live list: `grep -c "zylle.TribbleTrouble"
  infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` → 0.

**Mechanism inventory** — CONFIRMED (all files read directly):

| piece | file | what it does |
|---|---|---|
| `ZTrib_BaseTribble` / `ZTrib_Tribble` ThingDef | `1.6/Defs/Tribbles.xml` | bodySize 0.2, MarketValue 30, `tradeability None` (can't be sold), `foodType OmnivoreRoughAnimal, DendrovoreAnimal`, `lifeExpectancy 2` |
| Breeding comp | same file, `Class="ZTribble.CompProperties_TribbleSpawner"` | ONE XML-exposed knob: `baseSpawnInterval 0.1~1.4`. The actual breeding logic (asexual spawn-rate math) lives entirely inside `ZTribble.dll` — not visible in XML. DLL only, no `Source/` shipped in any version folder — not decompiled, per instructions. |
| `ZTrib_Tribble` PawnKindDef | `Tribbles.xml` | `combatPower 33`, `canArriveManhunter false`, texPath `ZTrib/Tribble/Tribble` (loose PNG, see below) |
| Arrival incident | `1.6/Defs/Incidents.xml` | `ZTrib_TribbleArrival`, `workerClass ZTribble.IncidentWorker_Tribbles`, `category ThreatBig`, `minPopulation 3`, `baseChance 0.2`, `minRefireDays 20`, `requireColonistsPresent true` — a random weather-tier threat-incident roll, **not** tied to any player action (confirms the spec doc's "reject: arrival as random weather-tier incident" reading) |
| Think tree | `1.6/Defs/ThinkTrees/ThinkTreeDefs.xml` | `ZTrib_Tribble` (flee/dig-out-if-trapped-and-starving/wander) + `ZTrib_Tribble_Constant` (flee, join caravan, lord duty) — vanilla-shaped animal AI, nothing exotic |
| Sounds | `1.6/Defs/SoundDefs.xml` + `Sounds/ZTrib/*` | 4 SoundDefs (Call/Angry/Death/Wounded), each backed by 2-6 loose `.wav` files |
| Tales/Keyed | `Defs/Tales.xml`, `Languages/English/Keyed/Keyed.xml` | present, not detailed further (out of scope: no mechanism content) |
| Art | `Textures/ZTrib/Tribble/Tribble_{east,north,south}.png` | loose PNGs, 3-facing — for the TRIBBLE, not the gizka; irrelevant to Part 2 |
| Assemblies | `{1.2..1.6}/Assemblies/ZTribble.dll` | compiled only; classes referenced by name only (`ZTribble.CompProperties_TribbleSpawner`, `ZTribble.IncidentWorker_Tribbles`) — no Source folder shipped anywhere in the mod, so no class list beyond what XML names |

No Harmony patches beyond the mod's own dependency declaration (no `Patches/`
folder in the mod at all — it's a self-contained comp+incident mod, not a
transpiler/patch mod).

## Part 2 — donor gizka art

**VERDICT: found, and the existing design doc's "absent" claim is now stale.**

`design/RimStarWars/gizka_ship_pest_spec.md` (2026-09-08) states: *"Art:
absent — no gizka texture in src/, the deployed Mods folder, or any workshop
folder."* This recon found it in the workshop, inside a mod that is now
**ACTIVE** in `ModsConfig.FULL.LATEST.xml` (grep confirms
`mlie.starwarsanimalcollection` present in that file).

| item | value | status |
|---|---|---|
| Donor mod | "Star Wars Animal Collection (Continued)", `packageId Mlie.StarWarsAnimalCollection`, WS `3497316713`, folder `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497316713` | CONFIRMED, and CONFIRMED active (in ModsConfig.FULL.LATEST.xml) |
| Gizka mechanism defs | `ThingDef`/`PawnKindDef`/`BodyDef defName Gizka` in `1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml` and `1.6/Defs/Bodies/Bodies_Animal_StarWars.xml` | CONFIRMED (read directly) |
| Gizka art | texPath `swanimals/Gizka/Gizka`, `swanimals/Gizka/GizkaW`, `swanimals/Gizka/Gizka_Dessicated` | CONFIRMED path strings in the ThingDef; art itself **not a loose PNG** — `find … -iname "*gizka*"` in that mod folder returns zero image files |
| Art container | `AssetBundles/Mlie_StarWarsAnimalCollection` (single bundle, no per-platform split) — mod's own About.xml states it was "re-released using only Asset Bundles" for 1.6 | CONFIRMED bundle exists; contents not extracted (no decompile/extraction attempted — read-only task) |
| Already wired into our stack | `RSW_Pawn_Gizka_{Angry,Call,Death,Wounded}` SoundDefs at `src/RimStarWars/SWBestiary/Defs/SoundDefs/SoundDefs_SWBestiary.xml:2536-2626`; `RUT_AridShrubland.xml` biome patch already lists `<Gizka MayRequire="mlie.starwarsanimalcollection">0.4</Gizka>` with comment "small-runway, keep" | CONFIRMED |
| Live decision record | `design/Jawa/worldbuilding/review/round2/decisions_propagated.json` carries `fauna:{arid_shrubland,desert,dune_sea + deep_desert,the_greentide,the_pyrelands}:Gizka` entries, all `"art":"keep"`, `sizeBin small`, propagated from `fauna:the_pyrelands:Gizka` | CONFIRMED — this is the live per-project record (retired `creature_art_register.decisions.json` also has one gizka hit but was NOT consulted as authoritative, per its retirement) |
| Named standalone alternative (unverified) | `design/Jawa/mods/required_mods.md` also names a separate KOTOR-flavored mod "Rimwars – Gizka" WS `2885638908` as an option if Gizka is wanted independent of the big pack | UNCERTAIN — not opened, not checked for activation or art format |

**Net correction to carry into Part 3-6 design:** the gizka creature (defs +
sounds) is not merely "art to locate before generating" — it is an existing,
already-tameable, already-active ThingDef/PawnKindDef with bundled art, already
present in multiple biome fauna rosters as a decided "keep." Whoever designs
the event mechanic should treat this as the base creature to wrap a
comp+incident around (mirroring the Tribble module's shape), not as a creature
to build from scratch, and should confirm the AssetBundle art renders in-game
(bridge/quicktest) before assuming it's usable as-is.

## UNKNOWN / not checked
- Whether the `Mlie_StarWarsAnimalCollection` AssetBundle actually contains a
  renderable Gizka sprite at runtime (bundle contents unopened; this needs an
  in-game/bridge check, not a file scan).
- `guy762.mm.kotorcore` (workshop `3254370945`) IS active in ModsConfig, but
  its absorption (`gen_kotorcore_absorption.py`) is about weapons/armor/
  materials, not creature art — confirmed unrelated to gizka by header read,
  not exhaustively swept for a second gizka reference.
- "Rimwars – Gizka" (WS `2885638908`) content, unverified (see table).
