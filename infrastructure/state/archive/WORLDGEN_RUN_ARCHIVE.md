# WORLDGEN_RUN_ARCHIVE.md — moved out of the live run sheet, 2026-08-23

> 📦 **This is HISTORY. The live file is `infrastructure/state/WORLDGEN_RUN.md`.**
> Every block below is the ORIGINAL BYTES, moved unchanged. Nothing was deleted. Each block
> carries one line saying why it moved.

---

## MOVED: lines 3-41 — the adoption / `remaking` banners of 2026-08-22

*Why: three overlapping banners, one of them a strike that was itself withdrawn, restating a
state that `infrastructure/state/canon.yml` holds authoritatively (`planet.status: remaking`,
`planet.status_src`). The live file now carries two lines and a pointer. The substance is
unchanged: authoring is open, the map is `world/ASHKARR_WORLDMAP_*.csv` edited in place, and
`remaking` is a four-step sequence whose step 4 — THE FREEZE IS A SAVEGAME — has not happened.*

> ✅ **AUTHORING IS OPEN, AND THE MAP IS THE REPO BUNDLE — owner, 2026-08-22 11:00, direct to
> DECIDE.** Asked which artifact he meant by *"DECIDE and I have an out of game map we are
> working on together"*, he answered: **`world/ASHKARR_WORLDMAP_*.csv` in this repo IS it.**
> ⇒ 🔑 **"Remake it an entirely different way" meant the METHOD — direct hand-authoring
> judged by looking — NOT a different planet.** Ash'karr as painted is the map in progress.
> **Keep editing it in place:** continuity repairs, landmarks, named places, settlements,
> terrain detail. The banner below stands.
>
> ⚠️ **I struck that banner earlier today and I was wrong; the strike is withdrawn.** It read
> `canon.yml`'s `planet.status: remaking` as "the old paint is history". It is not — see the
> next line for what `remaking` actually means.
>
> 🔑 **`remaking` is a FOUR-STEP SEQUENCE, not a verdict on the paint** (owner, 2026-08-22
> 10:57, quoted in full in `canon.yml`): **(1)** the out-of-game map — this bundle — is worked
> on and is not final; **(2)** it must be shown to survive a port into the game through the
> live bridge (`WORLD_PORT_SURVIVES_BRIDGE_1`, CHECK); **(3)** factions, leader names and
> ideoligions are finalised **in parallel**, because they bake at initiation and cannot be
> retrofitted; **(4)** only then is a game saved, and ⭐ **THE FREEZE IS THAT SAVEGAME** — not
> a CSV, not a doc, not an approved render.
> ⇒ **`status: remaking` is correct and stays** until step 4 exists on disk. It does **not**
> mean stop authoring; it means nothing is frozen yet.
> 🔑 What did NOT change: **there is still no worldgen feature, in any version.** Which canon
> values carry forward is `CANON_SUSPENDED_FOR_REMAKE_1`, paused by the owner.

> ✅ **THE MAP IS ADOPTED, AND AUTHORING IS OPEN AGAIN — owner, 2026-08-22.** Verbatim, after
> looking at the four-globe sheet: *"That world, upon examination, really isn't very bad at all…
> we're thinking of trying to adopt it."* ⇒ **Ash'karr as it stands IS the v1 planet**, and work
> on it continues: continuity repairs, landmarks, named places, settlements, terrain detail.
>
> ⛔ **This REPLACES the 2026-08-21 freeze banner**, which said the opposite and is struck. The
> freeze lasted one evening and did its job — it stopped a redraft nobody wanted.
> ⚠️ **What did NOT come back:** re-running `ashkarr_paint.py` to regenerate the bundle, the
> reference-match harness (`refmatch.py` stays cancelled ⚠️ **— wrong since 2026-08-22: it is DEFERRED TO v2** (`436bf693`)), and worldgen, which is out of every
> version and always was. **The map is edited DIRECTLY, one map, in place** — that is the whole
> method, per `the_one_map.md`.
> 🔮 `design/V2_DREAMS.md > PLANET_METHOD_RETHINK_1` stands as history, not as a plan.
> Ruling: `WORLD_ADOPTED_AUTHORING_OPEN_1` · supersedes `WORLD_FROZEN_RETHINK_PLANET_1`.
> ✅ **RECONFIRMED by the owner 2026-08-22 11:00** against DECIDE's own mistaken strike.


---

## MOVED: lines 43-67 — the 2026-08-15 standing worldgen ruling

*Why: carried verbatim in `CLAUDE.md` and in six other state files.*

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

---

## MOVED: lines 70-74 and 99-107 — the assembly note, and 'REHEARSE IT FIRST'

*Why: the assembly note is provenance. The rehearsal pointer describes two gates in terms that
are now WRONG — it says `OnlyOurFactions.xml` zeroes four KEEPs 'in a way the Configure
Factions page cannot undo'. Verified 2026-08-23: that file zeroes only
`startingCountAtWorldCreation`, never `maxConfigurableAtWorldCreation`, so the rows are still
on the page and the owner CAN set them by hand. The live gate table carries the corrected
form. `WORLDPAINT_REHEARSAL.md` §5/§6 are also a live hazard and are archived themselves.*

_Assembled by a retired seat, 2026-08-14, because the single event that closes **half the
remaining v1 rows** had no document. `WORLDGEN_FACTION_CHECKLIST.md` covers ONE
page of it, box by box, and is ratified. **This file is everything around that
page**, and its real job is §2: forcing the undecided inputs into the open
BEFORE the run rather than at the screen, at 3am, alone._


> ⭐ **REHEARSE IT FIRST — added 2026-08-21, CHECK.**
> `infrastructure/state/WORLDPAINT_REHEARSAL.md` paints the same 21,872-tile bundle onto a
> **throwaway** generated world, proving the import end to end and putting the planet on
> screen for the owner to judge, at no cost to this run. It also records the two gates that
> are shut on THIS file right now: **no `ScenarioDef` exists**, and `JawaFactionSlate`'s
> generated `OnlyOurFactions.xml` zeroes four factions the ratified checklist marks KEEP —
> including `guy762_KotORFaction_RogueDroids` — in a way the Configure Factions page cannot
> undo. Settle both before booking this load.

---

## MOVED: gate rows G1 and G2 (lines 125-126) — struck dead

*Why: both are `⛔ DEAD` rows about the sea assembly, deleted from the repo on 2026-08-19.
They were kept struck so nobody re-derived the gate from the md5 mismatch; the live table now
says that in one line instead of two dead rows.*

```
| ~~G1~~ | ⛔ **DEAD — the sea left v1, and as of 2026-08-19 it is deleted.** ~~The sea assembly and the 5-part sea gate are `[v2]` (`V2_DREAMS.md`).~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. `JawaSeaShaper` is gone from the repo, the Mods folder and `ModsConfig.xml` (584 → 583); `sea_seed_sweep.py` and `worldgen_sea_spec.md` are deleted. B2/C15/C16 dropped, DECIDE's D-CRIT superseded 2026-08-15 | — | Deploy nothing for the sea, and do not rebuild it. The repo/deployed md5 mismatch noted above is expected, not a defect |
| ~~G2~~ | ⛔ **DEAD with G1** — ~~nothing registers `Jawa_SeaShaping` because nothing runs it~~. ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. We register no `WorldGenStepDef` at all. Kept as a struck row so nobody re-derives the gate from the mismatch above | — | — |
```

---

## MOVED: lines 206-220 — §2.D, `isJunk`

*Why: DECIDED and closed (`de1018b` removed it from both scatter defs), and the section's own
text says the risk 'cannot bite once this deploys'. It survives in the live file only as §2.B's
tile-selection preference, which stays.*

### D. ✅ `isJunk` — DECIDED: dropped from both defs, `de1018b`. Not open.
A retired seat removed it after another retired seat IL-confirmed that `GenStep_ScatterGroupPrefabs :
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


---

## MOVED: lines 262-278 — §4, what to collect and which row it closes

*Why: an evidence table for v1 rows 2, 3, 4 and 7 that still carries the struck sea row W1.
The collection calls (`jawa/list_factions`, `jawa/world_stats`, `jawa/fire_quest`) live in the
items themselves; this table restated them for an event that has no date.*

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


---

## CORRECTED IN THE LIVE FILE, 2026-08-23 — original bytes kept here

*Why: two places still told the owner '21 untick / 6 keep' at the screen. The untick list is
dead (`OnlyOurFactions.xml`) and R5 left 4 keeps, not 6.*

Original gate row G5, live line 133:

```
| G5 | **The faction tick-list is to hand** — `WORLDGEN_FACTION_CHECKLIST.md`, ratified, 21 untick / 6 keep | the owner at the screen | The page is seen **once** |
```

Original sequence step 5, live lines 249-250:

```
5. **Configure Factions** — `WORLDGEN_FACTION_CHECKLIST.md`, box by box.
   **21 untick / 6 keep, ratified. Do not re-litigate at the screen.**
```
