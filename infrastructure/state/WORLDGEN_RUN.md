# WORLDGEN_RUN.md — the one-shot run that closes v1 rows 2 and 7

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
real.** Measured 2026-08-14: the repo `JawaSeaShaper.dll` is md5 `b7730027`, the
deployed and loaded one is md5 `82b48e53`, mtime 08-13 23:57 — **older than the
01:03:26 launch.** ⇒ **"verified in the binary" and "verified in the game" are
different claims, and this table can only ever make the first.**

| # | precondition | owner | why it cannot slip |
|---|---|---|---|
| G1 | ✅ **READY IN THE REPO — `c3ee8e7`, on origin. NOT LIVE.** The sea step places on the right predicate — `effectiveLat = Acos(Cos(lon·Deg2Rad)·Cos(lat·Deg2Rad))·Rad2Deg`, banding on arc distance from the subsolar point, **not latitude** | CREATE | Verified by `strings -a -el` on the built DLL: `aspect {5:F1}` and `mean arc {7:F0} deg` present, the old `mean |lat|` literal **absent**. ⚠️ **Deploys SOLO** — a new assembly poisons attribution for everything beside it — and **cannot be written while RimWorld runs** (`OSError 22` on the locked file; the refusal is safe, it cannot truncate) |
| G2 | **`Jawa_SeaShaping` is registered** in `PlanetLayerDef[defName="Surface"]/worldGenSteps` | CREATE | ⚠️ **A `WorldGenStepDef` absent from the layer loads, validates and NEVER RUNS, with no log line.** Registration is silent both ways |
| G3 | **The companion DLL carries the shutdown-window tools** — `jawa/get_defs`, `jawa/fire_quest` | BRIDGE | Companion work needs a **shutdown**, not a startup. Miss it and row 3 waits a full cycle |
| G4 | ✅ **`isJunk` is RESOLVED — removed from both scatter defs, `de1018b`.** What remains is a **DEPLOY**: the game copy is still 2026-08-13 16:42 with `isJunk` present | CREATE decided · OPS deploys | §2.D. **Decided, not done** — the fix is repo-only until it ships |
| G5 | **The faction tick-list is to hand** — `WORLDGEN_FACTION_CHECKLIST.md`, ratified, 21 untick / 6 keep | OPS at the screen | The page is seen **once** |

**If any of G1–G5 is open, the run is not ready. Say so rather than launching.**

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
**No ratified value exists.** `TidallyLocked` is the intended planet type — the
whole temperature design rests on its curve, and `JawaWorld_BiomeMix.xml` patches
that def **by defName**. **Confirm the type is actually selectable at the page and
selected.** Coverage and seed are open. → **owner + VISION.**

### B. 🔴 THE LANDING TILE — now load-bearing, and it was not before
**Pick the tile against its MUTATORS, not only its biome.** Of 337 `TileMutatorDef`s
in the 01:20 def dump, five carry `junkDensityFactor` **0**: `Dunes`, `Iceberg`,
`VEE_DetachedIceberg`, `VEE_IceAndFire`, `VEE_QuicksandDunes`.

⇒ **On a `Dunes` tile our scrapfields and our ground hulk both place NOTHING,
silently, with no warning** — a scavenger clan with its scrap switched off by the
terrain it lives on. **Read the candidate tile's mutators before committing.**
→ **owner picks; OPS reads the mutators.**

### C. Temperature target for the landing site
The habitable ring is **~34–57° of arc from (lon 0, lat 0)** — +30 °C at 33.7°,
+15 °C at 44.3°, 0 °C at 57.3°. ⚠️ **Latitude alone cannot express this:**
lat 45 / lon 0 is warm; **lat 45 / lon 120 is ≈ −62 °C.** Same latitude, opposite
worlds. → **VISION's fiction call, on arc distance.**

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
   strips `jawa/fire_incident` and `jawa/send_letter` off the game copy. Deploy
   `JawaSeaShaper` and any def fixes in the same window.
3. **Cold load** (~25–30 min). Harvest the startup log the moment it is up —
   `NEXT_RELOAD.md` §2 — before anything else touches the game.
4. **World creation page** — planet type, coverage, seed (§2.A).
5. **Configure Factions** — `WORLDGEN_FACTION_CHECKLIST.md`, box by box.
   **21 untick / 6 keep, ratified. Do not re-litigate at the screen.**
6. **Anomaly settings** — §2.E.
7. **Generate.** Then **read the sea step's own `Report()` out of the log before
   choosing a tile** — it self-tests coverage, body count and raggedness.
   ⚠️ **A missing `Report()` means G2 failed and the step never ran.**
8. **Landing tile** — §2.B, mutators first.
9. **Land, then collect §4.**

---

## 4. What to collect, and which row it closes

| evidence | row | call |
|---|---|---|
| factions absent from the world | **2** | `jawa/list_factions` |
| the campaign world exists, on the intended planet type | **7** | `jawa/world_stats` |
| the sea: ~25% water, 3 bodies, raggedness, band | W1 | the step's `Report()` in the log |
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
  have absolutely no clue how it actually works."* **The step measures and hits
  25%**; the field is a coarse nudge at best.
