# WORLDGEN_RUN.md — the one-shot run that closes v1 rows 2 and 7

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


_Assembled by PROJECT, 2026-08-14, because the single event that closes **half the
remaining v1 rows** had no document. `WORLDGEN_FACTION_CHECKLIST.md` covers ONE
page of it, box by box, and is ratified. **This file is everything around that
page**, and its real job is §2: forcing the undecided inputs into the open
BEFORE the run rather than at the screen, at 3am, alone._

> 🔴 **This run is IRREVERSIBLE and it is not repeatable at will.** It costs a
> ~25–30 minute cold load, it is driven by hand, and several of its inputs are
> read exactly once and can never be patched afterwards. **A wrong answer here is
> not a bug — it is a new campaign.**

---

## 1. The gate — what must be TRUE before anyone books the load

🔴 **EVERY ROW BELOW IS A REPO-STATE GATE. NOT ONE OF THEM IS LIVE.** A ✅ here
means *"correct, committed, and ready to ship"* — it never means the running game
has it. **The deploy is step 3.2, and it is the only thing that makes any of this
real.** ⇒ **"verified in the binary" and "verified in the game" are different
claims, and this table can only ever make the first.**

⚠️ **The md5 mismatch this section used to cite as evidence (repo `b7730027` vs
deployed `82b48e53`) is now EXPECTED and is not a gate** — see the struck G1/G2
rows. The general lesson it taught stands; the `[v2]` file it names does not ship.

| # | precondition | owner | why it cannot slip |
|---|---|---|---|
| ~~G1~~ | ⛔ **DEAD — the sea left v1, and as of 2026-08-19 it is deleted.** ~~The sea assembly and the 5-part sea gate are `[v2]` (`V2_DREAMS.md`).~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. `JawaSeaShaper` is gone from the repo, the Mods folder and `ModsConfig.xml` (584 → 583); `sea_seed_sweep.py` and `worldgen_sea_spec.md` are deleted. B2/C15/C16 dropped, DECIDE's D-CRIT superseded 2026-08-15 | — | Deploy nothing for the sea, and do not rebuild it. The repo/deployed md5 mismatch noted above is expected, not a defect |
| ~~G2~~ | ⛔ **DEAD with G1** — ~~nothing registers `Jawa_SeaShaping` because nothing runs it~~. ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. We register no `WorldGenStepDef` at all. Kept as a struck row so nobody re-derives the gate from the mismatch above | — | — |
| **G0** | 🔴 **`TidallyLocked` is SELECTED in Mod Settings** — see §2.A. Ratified 2026-08-15, **not set as of that date** | the owner, before the run | Fails **silently**: `selectedPlanetType` reads `Default`, no config file exists, nothing logs, and the type cannot be changed from the world page. Every ruling R-H0..R-H10 rests on its curve |
| **G6** | 🔴 **`JawaWorld_BiomeMix.xml` actually applies** — today 28 `is not <li>` errors leave `biomeConfigs: []`, so all 24 abundance offsets fail behind a patch that looks fine | BUILD, **B63** | **Biome scoring runs ONCE, at worldgen.** Same dictionary-keyed `<li>` bug as B56 |
| **G7** | 🔴 **Chain steps 6 and 9 are SHIPPED AND LIVE** — the 11 ideos and the full faction roster (B40–B54) | BUILD | Factions and ideos are read **once**, at world creation, and cannot be retrofitted. With the sea gone, **this is the real gate on rows 2 and 7**. Owner 2026-08-15: this work IS v1; factions are near done **bar allowed items and descriptions** — and "allowed items" now has a fixed set to draw from, because the cherrypick froze |
| **G8** | 🔴 **The ideoligion LOADS and its 16 AbilityDefs resolve in the engine** — `NEXT_RELOAD.md` §5 L0b, CHECK C42 | CHECK | ✅ **The offline half is DONE, `6c0f307`** — CHECK built `validate_save_artifact.py` because `validate_ideoligion.py` cannot read a saved `.rid` (it answers *"no religions found"* and checks nothing). `The Salvation.rid`: 267 references, 251 resolve, **zero dangling**; `MandrakeJawa.xtp` 36/36. ⚠️ **101 precepts, not the 82 this row used to say.** What is left is live-only: does it load, and do the 16 `AbilityDef`s resolve — and 🔴 `AbilityDef.json` is one of the 79 EMPTY def-type files in the dump, so that half **cannot** be settled offline. It bakes at creation. ⛔ Do not report the ideo row done on files existing |
| G3 | **The companion DLL carries the shutdown-window tools** — `jawa/get_defs`, `jawa/fire_quest` | CHECK | Companion work needs a **shutdown**, not a startup. Miss it and row 3 waits a full cycle |
| G4 | ✅ **`isJunk` is RESOLVED — removed from both scatter defs, `de1018b`.** What remains is a **DEPLOY**: the game copy is still 2026-08-13 16:42 with `isJunk` present | BUILD deploys | §2.D. **Decided, not done** — the fix is repo-only until it ships |
| G5 | **The faction tick-list is to hand** — `WORLDGEN_FACTION_CHECKLIST.md`, ratified, 21 untick / 6 keep | the owner at the screen | The page is seen **once** |

**If any LIVE row is open — G0, G3, G4, G5, G6, G7, G8 — the run is not ready. Say so
rather than launching.** (G1 and G2 are struck; they are dead, not open.)

---

## 2. 🔴 THE UNDECIDED INPUTS — settle these BEFORE the load, not at the screen

**This is why the file exists.** Each is a one-shot choice with no ratified answer
anywhere in the repo as of 2026-08-14. I am not guessing them; I am naming them.

🔴 **OWNER'S RULING 2026-08-14: A, B and C are the OWNER'S, decided AT THE SCREEN.**
⛔ **Do not prepare recommended values and do not ratify them in advance.** The job
of this section is to put the constraints and the warnings in front of them at the
moment of the click — **not to pre-answer it.** Anyone who "helpfully" ratifies a
coverage or a seed here is overriding a decision the owner has explicitly kept.

### A. Planet coverage · seed · planet type
✅ **PLANET TYPE IS RATIFIED — `TidallyLocked`, owner 2026-08-15, asked and answered
directly.** His words: *"I will set it, and it's parked until factions and ideos and
almost everything else ships."* **He sets it himself, in Mod Settings.**

🔴 **AND IT IS NOT SET YET. This is the single most dangerous unchecked box on this
page.** Measured 2026-08-15: **no planet-type config file exists anywhere in
`Config\`** and `selectedPlanetType` still reads `Default`. Alien Worlds ships
exactly two types, `Default` and `TidallyLocked`. ⇒ **A world generated before he
clicks it is an ordinary vanilla planet** — no tidal lock, no
`avgTempByLatitudeCurve`, no rainfall curve, no biome blacklist — and **every ruling
R-H0..R-H10 assumes that curve**. `JawaWorld_BiomeMix.xml` patches the def **by
defName**, so it patches a type the world is not using.
⚠️ It fails **silently**. Nothing logs, nothing warns, and the run is irreversible.
`ferny.Worldbuilder` is inactive, so it is a **radio list in MOD SETTINGS, not a
button on the world page** — it cannot be fixed at the screen once he is there.

**⇒ Do not book this run until it is confirmed set.** That confirmation is a look at
Mod Settings, not a file we can write for him — recorded here rather than in a queue
because it is his click, not a build.

🔴 **COVERAGE IS NO LONGER OPEN — it is PINNED, and this is the half of the run the
2026-08-19 ruling explicitly KEEPS.** The generated world is the *input* the authored
map is stamped onto, and the tile IDs in `world/ASHKARR_WORLDMAP_tiles.csv` only mean
anything at one grid size: **My Little Planet subcount 7 · planet coverage 100% (1.0)**,
which yields exactly **21,872 tiles**. Any other value and every tile ID shifts and the
import silently paints the wrong planet. Details and the assert the importer must carry:
`worldmap-import-is-pinned-to-mlp-subcount-7-4c9e1a` in `queue/CHECK.md`.

**Seed remains open and remains the owner's, at the screen** — it chooses the base
planet, which the import overwrites.

### B. 🔴 THE LANDING TILE — now load-bearing, and it was not before
**Pick the tile against its MUTATORS, not only its biome.** Of 337 `TileMutatorDef`s
in the 01:20 def dump, five carry `junkDensityFactor` **0**: `Dunes`, `Iceberg`,
`VEE_DetachedIceberg`, `VEE_IceAndFire`, `VEE_QuicksandDunes`.

⇒ **On a `Dunes` tile our scrapfields and our ground hulk both place NOTHING,
silently, with no warning** — a scavenger clan with its scrap switched off by the
terrain it lives on. **Read the candidate tile's mutators before committing.**
→ **the owner picks; BUILD reads the mutators.**

### C. Temperature target for the landing site
The habitable ring is **~34–57° of arc from (lon 0, lat 0)** — +30 °C at 33.7°,
+15 °C at 44.3°, 0 °C at 57.3°. ⚠️ **Latitude alone cannot express this:**
lat 45 / lon 0 is warm; **lat 45 / lon 120 is ≈ −62 °C.** Same latitude, opposite
worlds. → **the owner's fiction call, on arc distance.**

### D. ✅ `isJunk` — DECIDED: dropped from both defs, `de1018b`. Not open.
CREATE removed it after OPS IL-confirmed that `GenStep_ScatterGroupPrefabs :
GenStep_Scatterer` inherits `GetPlacementFactor`. **With `isJunk` gone the factor
returns 1 unconditionally and `junkDensityFactor` never enters the product — on
any tile, dunes included.**

⭐ **So §2.B is now a DESIGN FIX, not a hazard to schedule a test for.** Do not
book a test for the dunes risk; it cannot bite once this deploys. **B survives
only as a tile-selection preference, no longer as a gate.**

🔴 **But it is repo-only.** The deployed `JawaScrapfields.xml` is still
2026-08-13 16:42 with `isJunk` present, and PID 16112 read its defs at 01:03:26
regardless. **Nothing measured on the running process can validate this fix**, and
a green from it would be meaningless. **It ships in the same window as G3.**

### E. Anomaly
**Already ruled and NOT open — ticked during this run, not separate work.**
Playstyle `Disabled` so content is at zero · **DLC stays ENABLED** so the assets
remain reachable · the owner's cherry-picked removals stand. Recorded here only so
nobody re-opens it at the screen.

---

## 3. The sequence

1. **Announce.** `LIVE BRIDGE TAKEN` — and the owner authorises connecting;
   announcing only informs.
2. **Shutdown window** — deploy the companion DLL (G3) **with `--gm`**, or it
   strips `jawa/fire_incident` and `jawa/send_letter` off the game copy. Deploy any
   def fixes in the same window.
3. **Cold load** (~25–30 min). Harvest the startup log the moment it is up —
   `NEXT_RELOAD.md` §2 — before anything else touches the game.
4. **World creation page** — planet type, coverage, seed (§2.A).
5. **Configure Factions** — `WORLDGEN_FACTION_CHECKLIST.md`, box by box.
   **21 untick / 6 keep, ratified. Do not re-litigate at the screen.**
6. **Anomaly settings** — §2.E.
7. **Generate.** ~~Then read the sea step's own `Report()` out of the log before
   choosing a tile.~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. **No step of ours runs during
   generation and nothing of ours writes to the log here.** The planet the generator
   produces is the INPUT; the authored map is written over it afterwards through the
   bridge — see `worldpaint-live-bridge-route-9d41c7` in `queue/CHECK.md`.
8. **Landing tile** — §2.B, mutators first.
9. **Land, then collect §4.**

---

## 4. What to collect, and which row it closes

| evidence | row | call |
|---|---|---|
| factions absent from the world | **2** | `jawa/list_factions` |
| the campaign world exists, on the intended planet type | **7** | `jawa/world_stats` |
| ~~the sea: ~25% water, 3 bodies, raggedness, band~~ | ~~W1~~ | ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. Nothing to collect — no step, no `Report()` |
| `ChunkSlagSteel` count on the campaign map | **4** | a cells sweep, or `jawa/get_things` if it has landed |
| the hulk present and ship-shaped | 4's rider | count the prefab pieces and their bounding box — ⛔ **not "reads as a downed ship"**, which no call can collect |
| *The Claim* fires and reaches an end state | **3** | `jawa/fire_quest`, then a state read at T+n |

⚠️ **Row 4's map-gen items appear on ANY fresh map** and do not need the campaign
world. **Row 3 does not either.** If the worldgen slips again, those still move —
do not let them wait on it.

---

## 5. What must NOT happen

- ⛔ **Do not read row 2 off a quicktest.** A debug quicktest never visits the
  Configure Factions page, so all 54 factions are present and the row looks failed.
  This nearly cost a regeneration once already.
- ⛔ **Do not author a new `PlanetTypeDef`.** Only one is active at a time; ours
  would *replace* `TidallyLocked` and drop the temperature curve the design rests
  on. **Patch the shipped def by defName.**
- ⛔ **Do not whitelist biomes.** A whitelist silently excludes `Space`, `Orbit`,
  `Underground` and the undercaves, breaking every pocket map. **Blacklist only.**
- ⛔ **Do not trust `elevationRange` as an ocean dial.** Its own author wrote *"I
  have absolutely no clue how it actually works."* ~~The step measures and hits 25%~~
  — ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. The generated planet's water is
  OVERWRITTEN by the imported map, so the field does not need to hit any target.
