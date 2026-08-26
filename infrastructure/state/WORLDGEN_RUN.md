# WORLDGEN_RUN.md — the one-shot run that closes v1 rows 2 and 7

> there on 2026-08-23, byte-unchanged. **Nothing was deleted.** What moved: the three
> overlapping 2026-08-22 adoption/`remaking` banners, the 2026-08-15 standing worldgen ruling
> (verbatim in `CLAUDE.md`), the 'rehearse it first' pointer, the struck G1/G2 sea gates, §2.D
> (`isJunk`, closed) and §4 (the evidence table).
>
> 🔑 **State of the planet, in two lines, authoritative in `infrastructure/state/canon.yml`:**
> `planet.status: remaking` — a FOUR-STEP sequence, not a verdict on the paint. Authoring is
> OPEN and the map is `world/ASHKARR_WORLDMAP_*.csv`, edited **directly, one map, in place**.
> ⭐ **The freeze is a SAVEGAME** (step 4) and it does not exist yet. There is still **no
> worldgen feature, in any version** — `CLAUDE.md`.

_Assembled 2026-08-14 because the single event that closes half the remaining v1 rows had no
document. `WORLDGEN_FACTION_CHECKLIST.md` covers ONE page of it; **this file is everything
around that page**, and its real job is §2: forcing the undecided inputs into the open BEFORE
the run rather than at the screen, at 3am, alone._

> 🔴 **This run is IRREVERSIBLE and it is not repeatable at will.** It costs a
> ~25–30 minute cold load, it is driven by hand, and several of its inputs are
> read exactly once and can never be patched afterwards. **A wrong answer here is
> not a bug — it is a new campaign.**

> 🔴 **THE IDEOLIGION MODE ON THE WORLD-CREATION PAGE DECIDES WHETHER THE ELEVEN FAITHS
> EXIST AT ALL — measured 2026-08-21, CHECK, and this file did not say so.**
>
> On the rehearsal world, `jawa/ideo_of` reports `ideologyActive: true` and
> **`ideosTotal: 2`** — the player's `Astropolitan` (zero memes, no `structureMeme`, 54
> precepts, `initialPlayerIdeo: true` — the signature of **Classic ideoligion**) and one
> other. Every one of the sixteen factions returns a null ideo name, zero memes, zero
> deities. **None of the eleven authored faiths generated.**
>
> ✅ **The defs are not at fault.** All twelve `ideoName` values are in the deployed
> FactionDefs, and the one NPC ideo that DOES exist is `the Contract` — Blackstar Company's
> faith — which appeared only because Blackstar was created by hand with
> `jawa/faction_create` *after* worldgen. So the FactionDef ideo block works; worldgen
> never applied it.
>
> ⇒ **On the real run, do NOT accept Classic ideoligion.** An Ideo is generated once at
> world creation and cannot be retrofitted, so this click is the difference between eleven
> faiths and none, forever. `B54` · `CLASSIC_IDEO_ERASES_FAITHS_1`.

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
| ~~G1~~ · ~~G2~~ | ⛔ **DEAD, and struck. Both were sea gates**; the sea left v1 and `JawaSeaShaper` was deleted from the repo, the Mods folder and `ModsConfig.xml` on 2026-08-19. We register no `WorldGenStepDef` at all. The repo/deployed md5 mismatch above is expected, not a defect. Full rows: the archive | — | Dead, not open. Do not re-derive a gate from the mismatch |
| **G0** | 🔴 **the `tidally locked world` PRESET is picked on the world page, and Configure Planet reads Scale 7 / Coverage 100%** — see §2.A. The Mod Settings route is dead; `ferny.worldbuilder` is active | the owner, at the screen | Fails **silently**: the wrong preset gives an ordinary vanilla planet and nothing logs. Scale 10 means the preset lost its parameters and every tile ID shifts. Every ruling R-H0..R-H10 rests on that curve |
| **G7** | 🔴 **Chain steps 6 and 9 are SHIPPED AND LIVE** — the 11 ideos and the full faction roster (B40–B54) | BUILD | Factions and ideos are read **once**, at world creation, and cannot be retrofitted. With the sea gone, **this is the real gate on rows 2 and 7**. Owner 2026-08-15: this work IS v1; factions are near done **bar allowed items and descriptions** — and "allowed items" now has a fixed set to draw from, because the cherrypick froze |
| **G8** | 🔴 **The ideoligion LOADS and its 16 AbilityDefs resolve in the engine** — `NEXT_RELOAD.md` §5 L0b, CHECK C42 | CHECK | ✅ **The offline half is DONE, `6c0f307`** — CHECK built `validate_save_artifact.py` because `validate_ideoligion.py` cannot read a saved `.rid` (it answers *"no religions found"* and checks nothing). `The Salvation.rid`: 267 references, 251 resolve, **zero dangling**; `MandrakeJawa.xtp` 36/36. ⚠️ **101 precepts, not the 82 this row used to say.** What is left is live-only: does it load, and do the 16 `AbilityDef`s resolve — and 🔴 `AbilityDef.json` is one of the 79 EMPTY def-type files in the dump, so that half **cannot** be settled offline. It bakes at creation. ⛔ Do not report the ideo row done on files existing |
| G3 | **The companion DLL carries the shutdown-window tools** — `jawa/get_defs`, `jawa/fire_quest` | CHECK | Companion work needs a **shutdown**, not a startup. Miss it and row 3 waits a full cycle |
| G4 | ✅ **`isJunk` is RESOLVED — removed from both scatter defs, `de1018b`.** What remains is a **DEPLOY**: the game copy is still 2026-08-13 16:42 with `isJunk` present | BUILD deploys | §2.D. **Decided, not done** — the fix is repo-only until it ships |
| **G5** | **The faction sheet is to hand** — `WORLDGEN_FACTION_CHECKLIST.md`. 🔴 **The 21-row untick list is DEAD** (`OnlyOurFactions.xml` zeroes `startingCountAtWorldCreation` on 48 defs; the page opens as our twelve, one each). What is LIVE on that sheet: **4 KEEPs**, of which `JDSCIS_CIS_Faction` and `guy762_KotORFaction_RogueDroids` default to 0 and must be set by hand, plus Section 4b's 13 rows | the owner at the screen | The page is seen **once** |

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

🔴 **THE ROUTE CHANGED — `ferny.worldbuilder` IS ACTIVE (measured 2026-08-19).** The
Mod Settings radio list described here until now is **DISABLED** under that backend and
`selectedPlanetType` is forced to `"Unknown"`. **The preset NAME is the planet type**, so
it is chosen ON the world-creation page: pick the **tidally locked world** preset.
The rest of the old warning still holds — a world generated on the wrong preset is an
ordinary vanilla planet, no `avgTempByLatitudeCurve`, no biome blacklist, and it fails
**silently**. `JawaWorld_BiomeMix.xml` patches the def by defName, so on the wrong type it
patches something the world is not using.
🔑 **The preset now lives at**
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Worldbuilder\TidallyLocked\Preset.xml`,
which is scanned before mod folders and wins first. The workshop copy is deleted and
regenerated as a parameterless stub at **every** launch, so it is not the one to read.
🔴 **THE ON-SCREEN CHECK, and it is an ABORT gate:** Configure Planet must read
**Scale 7** and **Coverage 100%**. If Scale reads **10**, the preset lost its parameters
— Worldbuilder's own Reset path sets subcount 10 — and every tile ID in
`world/ASHKARR_WORLDMAP_tiles.csv` is wrong. **Do not generate.**

✅ **THE PLANET NAME IS TYPEABLE, and it arrives pre-filled.** Worldbuilder draws a
planet-name text field on this page and writes it straight to `WorldInfo.name`.
`JawaWorld_Name.xml` replaces Core's `NamerWorld` rule pack with the single rule
`Ash'karr`, which is what seeds that field — so **do not retype it**. `’` (U+2019) reads
identically to `'` (U+0027) and compares unequal.

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

### E. Anomaly
**Already ruled and NOT open — ticked during this run, not separate work.**
🔴 **CORRECTED 2026-08-19: the playstyle is `AmbientHorror`, NOT `Disabled`.**
`Disabled` carries `enableAnomalyContent:false` and kills study, the research tab, the
codex and tome trading. `AmbientHorror` keeps all of that, generates no monolith, and
with the threat fraction at **0** spawns nothing on its own while leaving
`PitGate`/`FleshmassHeart` available to fire deliberately.

⚠️ **The fraction does not start at zero — drag it to 0.** `AmbientHorror` replaces the
per-category sliders with a single 0..1 slider, seeded at **0.15**. That value lives on
the runtime `Difficulty` object, so **Custom difficulty is mandatory, not a preference**.

🔴 Both are set behind the "Anomaly settings…" button, which is drawn under a
`ProgramState.Entry` guard — **it does not exist in an existing save.** DLC stays
ENABLED; the owner's cherry-picked removals stand.

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
5. **Configure Factions** — `WORLDGEN_FACTION_CHECKLIST.md`, and read its banner first.
   ⛔ **Do not work the old 21-row untick list; it is dead and archived.** The page should open
   as our twelve at one each. **Set `JDSCIS_CIS_Faction` and `guy762_KotORFaction_RogueDroids`
   by hand — they default to 0.** Then Section 4b. Do not re-litigate at the screen.
6. **Anomaly settings** — §2.E.
7. **Generate.** ~~Then read the sea step's own `Report()` out of the log before
   choosing a tile.~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. **No step of ours runs during
   generation and nothing of ours writes to the log here.** The planet the generator
   produces is the INPUT; the authored map is written over it afterwards through the
   bridge — see `worldpaint-live-bridge-route-9d41c7` in `queue/CHECK.md`.
8. **Landing tile** — §2.B, mutators first.
9. **Land, then collect §4.**

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
