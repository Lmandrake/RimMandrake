# AGENT_CREATE_state.md — where CREATE is

_Updated 2026-08-13 after the game-down offline session. Queue:
`infrastructure/state/queue/CREATE.md` — **drained 1,113 → 147 lines, so it is
now current rather than a pile**; read it, not this, for what is owed._

---

## 0. Live state — what is true right now

**TEN fix mods now exist; EIGHT are live.** Deployed and ENABLED (572 → 580
active, listed-but-absent 0): the seven per-donor art-fix mods plus
`mandrake.desertvehiclereskin`.
🔴 **Two are NOT deployed and NOT in `ModsConfig.xml`** — `mandrake.phytokinbarkheadfix`
(`cb6c2f7`) and `mandrake.kotorbandoliernorthfix` (`dd66fe6`). Filed at OPS
`38f6d82`. **The KotOR one must not join the 556–564 slot: its donor is at 573
with loose art, so it would be silently invisible there.** All eight went in as
one slot after `mandrake.missingartfixes`; OPS placed them, the owner orders in
RimSort. 🔴 **I do not touch the mod list — order or contents. Owner's ruling,
`fdedc68`, in my identity file.**

**Built, deployed, NEVER SEEN:** v1 **row 3** (`Jawa_TheClaim` + `Jawa_ClaimRumour`)
and v1 **row 4** (salt pans, dune seas, scrapfields) plus the **ground hulk** rider.
`V1_SCOPE.md`'s gate is *seen in-game once*, so **none of these are closed.**

**Capacity ceiling is 4500, not 632.8.** Raised live through Bigger Gravships'
settings dial + "Apply Settings Now!", no restart, and **it persists**. Anything
quoting 632.8 is stale.

---

## 0b. 🔴 THE PRE-WORLDGEN GATES — what shipped in the 2026-08-14 window

Worldgen was HELD for these. All are deployed and `VERIFIED in sync`.

| gate | what | why it could not wait |
|---|---|---|
| **W2** | `JawaXenotype_Repoint.xml` — both Jawa pawn kinds → `BTD_Jawa` (+20 °C) | `xenotypeSet` is read at **pawn generation**; a later patch never fixes an existing world's colonists |
| **W3** | `JawaWorld_BiomeMix.xml` — 29 `biomeBlacklist` exclusions + abundance tiers, patched into the **shipped `TidallyLocked` def** | biome scoring runs once, `WorldGenStep_Terrain` order 0 |
| **W1** | sea step built (`JawaSeaShaper`, order 20) — ⏳ **placement code HELD** for VISION's settled spec | a `WorldGenStep` runs once, at world creation |
| — | `Fleshbeast_TrispikeCull.xml` — Trispike out of Bulbfreak's and Dreadmeld's divide lists | a cherry-picked kind is **neutered, not deleted**, so it is still summonable BY NAME |

🔴 **Three measured facts that decided the shape of W1/W3, none of them guessable:**
1. **Only ONE `AlienWorlds.PlanetTypeDef` is active** (`activePlanetType`, mod
   settings, scribed per save). A second def would REPLACE tidal lock and drop its
   temperature curve ⇒ **patch the shipped def, never author ours.**
2. **`scoreOffset` is in DEGREES** — `BiomeWorker_Desert::Score` is literally
   `tile.temperature`. ⚠️ And disallowed biomes floor at **0**, so on the negative
   nightside a big negative offset loses the argmax to a biome that is not even
   allowed. **Do not deepen past ~−5.**
3. **`elevationRange` is NOT an ocean dial** — its author's own comment is *"I have
   absolutely no clue how it actually works"*. Coarse nudge only.

⛔ **Cherry Picker: 22 keys live** (owner's Anomaly picks + GravTech's three).
Picked defs are **neutered, not deleted**, so they stay dev-spawnable — which is
what reconciled "content at zero" with "creatures stay reachable for reskinning".
Generator: `src/RimMandrake/Utils/cherrypick_build.py`. **Never hand-edit** — one
key without a `/` aborts every removal after it.

⭐ **`src/RimMandrake/Utils/preload_check.py` is the pre-launch gate.** Nine checks,
all silent-failure classes. Run it as the LAST act before boot; the config moved
three times on 2026-08-13/14, once from a seat writing `ModsConfig` directly.

---

## 1. Closed today

| item | commit | note |
|---|---|---|
| **C3a** eopie sled, all three owner fixes | `2a9a004` `65c1590` `7e3018e` | **APPROVED AND SHIPPED.** Sled tint was a def edit, not art; east snout was a *scale* failure |
| **C5** blast-door `FrameAsync_east` | `48e5e16` | the brief's transform was **wrong** — donor's own C# shows same quad, different altitude |
| **C6** two typo-fix mods | `cb95f60` | |
| **C8** sprite validator | `365e599` | most of it already existed |
| **C11** `MissingArtFixes` split, 4 mods | `61fe954` | old mod now has **zero unique textures** — safe for OPS to retire |
| **C12** duplicate-file collision | `6f52185` | 🔴 two fix mods were **inert** — `Jawa_Patches` at 581 shadowed them at 561-2, identical bytes hid it |
| **C-v3** restraint bolt recon | `8353622` | verdict **CAP**; one XML def + ~40 lines C# |
| **v1 row 3** authored | `47733f8` | |
| **v1 row 4** authored | `73ca76c` | `Jawa_SaltCrust` **PASSED live** — 144 cells, art renders |
| **ground hulk** (row 4 rider) | `00a1398` | 619 cells of 1,200 |
| **salvage filter** (v1 deliverable) | `7bf4d4f` | script + output; 1,049 defs → 73 excluded, 315 with yields, **635 return nothing** |
| **gravship flight invariants** | `07cf00d`..`cdaa2f1` | the document the gravship skill will encode |
| **C7 rows 1–3** — the "do first" set | `cb6c2f7` `dd66fe6` `dd4f386` | 22 files, 2 new mods. Rows 1 and 3 needed **zero art** |
| **C-LOAD** load-order gaps | `731e9c5` `bd90813` | `Jawa_Doctrine` declared **none** and patches 630 defs across 42 mods |
| **queue drained to budget** | `315d190` | 1,113 → 147 lines |

---

## 2. Owed — what the next session picks up

🔴 **Everything below needs ONE fresh quicktest map. Nothing else.**

| # | owed | needs |
|---|---|---|
| 1 | **row 3 gate** — spawn `Jawa_ClaimRumour`, read it, quest fires and resolves | any map |
| 2 | **row 4, scrapfields** — slag scatter. **LOOK BEFORE ANY DESTROY**; the last map's evidence died in a 43,288-thing wipe | fresh map, any biome |
| 3 | **row 4, dune seas** — ⚠️ **do NOT eyeball this.** It is a density change (threshold 0.65→0.55) and unjudgeable without a control map. **Read the live `BiomeDef` and confirm `terrainPatchMakers` shows 0.55 / 0.50.** That is the actual claim | one def read |
| 4 | **ground hulk** — wide shot + one casket bank close | fresh map |
| 5 | **the ten art mods** — one spawn, one look each (two are not live yet) | any map |
| 6 | **`NoPathToPilotConsole`** — doors exist and are in the export, but **a door is not a path.** Walk a pawn to the console's interaction cell | needs B-v3 |

⚠️ **Nobody has ever seen an `AncientCryptosleepCasket`.** Vanilla art ships inside
AssetBundles — `Data/*/Textures` does not exist — so 297 usable wreck defs cannot
be rendered offline. Defs, sizes and yields are verified; **the look is not.**

⛔ **That diagnostic was WRONG — struck 2026-08-13 (BRIDGE).** `ShipChunk_Mech`
needs `Light`, not `Heavy`, and `BrokenSubstructure` appends to `FloorBase` so it
supplies Light/Medium/Heavy/Walkable/Substructure. **Either layer satisfies it.**
Missing props ⇒ look at prefab placement, blocked cells, `spotMustBeStandable`.

---

## 3. Blocked / not mine

- **Three stale files in `Jawa_Patches`' game copy** (the C12 shadows) — OPS's, they
  own that deploy.
- **Retiring `mandrake.missingartfixes`** — OPS; its blocking dependency is cleared.
- **Bigger Gravships upstream bug** — BG rebuilds `CompProperties_GravshipFacility`
  and **drops the `statOffsets`** carrying `SubstructureSupport 250`. Extender links,
  offers nothing. Reportable; worked around by the slider.

---

## 4. The three lessons that cost the most today

1. **Live def beats dump beats XML** — and three separate times offline evidence
   disagreed with the running game. Bigger Gravships stamps after XML patching, so
   the disk is never final here.
2. **An absence is only evidence if you can show the probe would have shown a
   presence.** Two live reads reported truncated or wrongly-scoped output as
   absence; the extender bug hid behind both. The discriminator was comparing the
   *shape* of a healthy def's response against the suspect one.
3. **Art can be correct at source and broken at render** (`traps-art.md` #45), and
   **`Graphic_Multi` falls back to the bare path while render nodes build lazily**
   (#46) — so a clean log proves almost nothing about art.
4. **A donor's mask is the donor's own segmentation, and his complete set is a
   TEST HARNESS.** `CutoutComplex` splits tinted material from fixed furniture, so
   the author had already separated leather from pouches. And the obvious recipe
   was killed by scoring it against the facing he *had* drawn — 77.2% where
   mirroring alone gives 77.1%. **Score before you apply.**

---

# Session 2026-08-14 (evening) — hand-off at fleet shutdown

**Everything below is committed and pushed. Nothing of mine is uncommitted, and
the scratchpad has been triaged.**

## What shipped

**⭐ The Jawa ideoligion, on the owner's direct request.** Owner authored a
skeleton `.rid` and asked CREATE to fill the choices and all flavour text from
lore. Result:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\The Salvation (CREATE).rid`
The owner's original is **untouched beside it** — both load in the ideo browser.
Builder is `src/RimMandrake/Utils/build_salvation_rid.py --check|--write`; it
never rewrites the source, asserts unique IDs and no dangling `Precept_<ID>`, and
is byte-identical on re-run. **The `.rid` is derived — regenerate it, do not
hand-edit it.** Filed at `queue/OPS.md`; detail at `queue/CREATE.md` C15.

**Row 7 (thruster) closed OFFLINE, and it killed a planned stern deck re-lay.**
Cost is ONE `GravshipHull` cell per small thruster. Derivation rescued from the
scratchpad into `src/RimMandrake/Utils/thruster_placement_scan.py`.
🔴 **`gravship_flight_invariants.md` §11 is wrong on BOTH branches and still
needs correcting** — nobody has done it.

**Row 6 (pilot console) is BLOCKED, not pending** — `PilotConsole` count in the
export is **zero**. There is nothing to path to. It was filed for a year as "one
paused call"; it is not, and it is a deck-authoring job.

## The four findings that outlive the files

1. **`AM_Structure_Scavenger` is `deityCount 0`.** The nine-god pantheon can
   never be seated in this ideo, and no installed structure meme allows more
   than four. That is *why* the gods live in the description. ⛔ **Do not "fix"
   it by swapping the structure meme.**
2. **`comps: []` DOES NOT MEAN INERT** — the measure the project's own rubric
   uses. Of 65 comps-less precepts only 29 are truly inert: 32 are
   ritual/building/relic classes whose mechanics live elsewhere, and 4 are live
   via `statOffsets` / `expectationsOffset` / inbound `nullifyingPrecepts`.
   `AM_Barracks_Preferred` and `DarknessCombat_Preferred` both read inert and are
   fully live. ⇒ **read `comps ∪ statOffsets ∪ expectationsOffset ∪ inbound
   nullifyingPrecepts`**, and exempt the ritual/building/relic classes.
3. **A prediction is only a test if the instrument can read its TERMS.** I handed
   the live seat an A/B whose verdict was an inspect string, having never checked
   that any tool could read one. Pre-registering the prediction made it *feel*
   more rigorous while doing nothing about aiming at an invisible target. Filed
   in `skills/rimbridge/references/traps.md`.
4. **The `jawa/` prefix says who SUPPLIES a tool, not what it does.** 139
   `rimworld/` names against 26 `jawa/`, so guessing `jawa/` is wrong ~84% of the
   time by count. Also filed in the rimbridge traps.

## Open riders — taste, not rulings

- `guy762_JawaHood` is live and literally species-named; the file currently uses
  `OuterRim_DesertHood`. One word.
- Lore sanctifies ration paste (`:360`) but the ideo sets
  `NutrientPasteEating_Disgusting`. Unresolved contradiction.
- Sh'kaar is written as "the sun that never sets"; the older doc says **twin
  suns**, and the tidally-locked world postdates it.

## Recorded so nobody re-derives it: doctrines with NO legal precept

Begging (charity has no negative position, and all three positive ones conflict
with `Trader`) · farming-as-impious (no growing issue exists) · ancient complexes
revered · sacred scrap / do-not-melt · being caught stealing · mating only in
darkness. **All six confirmed absent across 685 precepts.**

⛔ **`VME_Nomad` is a trap** — −50 mood at 60 days, and its own description
admits it cannot see non-vanilla movement. `Nomadic_Preferred` is a **precept**,
costs no meme slot, and a gravship jump correctly resets it
(`GravshipUtility::ArriveNewMap` stamps `IdeoManager.lastResettledTick`).
