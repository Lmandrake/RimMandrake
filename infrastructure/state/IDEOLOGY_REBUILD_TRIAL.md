# The ideology rebuild trial — prove the import before deciding

**Owner, 2026-08-26, choosing between re-creating Ash'karr in full Ideology mode and shipping
classic mode: "Prove the import first."** This is that procedure.

🔑 **What it answers:** whether carrying the planet onto a fresh world is four file imports and a
script replay, or something worse. **The import half has never once been run** — everything said
about the cost so far, including my own estimate, is a plan.

⛔ **Nothing here touches Ash'karr.** The trial world is a throwaway.

---

## Phase A — while Ash'karr is UP. Mine, ~1 minute.

The `_final` bundle on disk is from **2026-08-25 08:25** and predates the hilliness pass and the
Wither rebuild, so it is not what would be carried. A current one has to be taken first.

```
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\Utils\vivify_world.py --live --out world\ASHKARR_PREREBUILD_2026-08-26
```

⚠️ **Take this BEFORE leaving Ash'karr for the main menu.** It writes `_tiles.csv` (whose `region`
column is what carries the named regions), `_links.csv`, `_settlements.csv`, `_mutators.csv`,
`_landmarks.csv` and `_meta.json`.

## Phase B — yours, at the screen. The bridge cannot reach any of it.

`BRIDGE_CANNOT_MAKE_A_WORLD_1`: `Page_CreateWorldParams` needs a Game object that does not exist in
the Entry scene, and the main menu's buttons are immediate-mode GUI that nothing enumerates. There
is no automating this half.

1. Main menu → **New Colony**.
2. **Configure Planet** — ⚠️ it must read **Scale 7** and **Coverage 100%**. Anything else gives a
   different tile count and every imported row lands on the wrong hex; the script refuses rather
   than writing. (If Scale reads 10 the preset was not read — abort rather than generate.)
3. 🔴 **Ideology: NOT classic mode.** This is the entire point of the trial. Classic gives one
   shared `Astropolitan` ideoligion, which is exactly the state we are trying to get out of.
4. Generate the world.
5. 🔴 **STOP at the landing-site page. Do not land, do not pick a tile.** The importer refuses while
   a map exists — §12.4 rule 3, and painting under an instantiated map is what destroyed the save
   twice.
6. Tell me it is there.

## Phase C — mine. Guards, dry run, import, read back.

```
python.exe D:\Luke\dev\Rimworld\world\_rebuild\import_trial.py --bundle D:\Luke\dev\Rimworld\world\ASHKARR_PREREBUILD_2026-08-26
python.exe ...\import_trial.py --bundle ... --apply
```

It refuses on any of four, before writing anything: **a map exists** · **the world is called
Ash'karr** (it would overwrite the source) · **the tile count is not 21,872** · **`ideosTotal` is 1**,
which means classic mode and a trial that proves nothing.

Then dry-runs all four imports, and only applies if every dry run succeeded. It reads back through
`world_tile_validate` (RAW fields — it cannot be fooled by RimWorld's lazy caches),
`world_links_validate` and `world_objects_validate`, never through the importers' own echo.

## What the trial cannot tell you, and I would rather say now

⚠️ **Mutators and landmarks will read ~0 after the import, and that is expected, not a failure.**
There is no `world_mutators_import` and no `world_landmarks_import` — `world_mutators_set` and
`world_landmarks_set` are per-batch, not per-file (`WORLD_MUTATOR_LANDMARK_IMPORTERS_1`). On the
source planet that is **13,569 mutator tiles and 579 landmarks**, and a rebuild would owe a script
replay for both.

⚠️ **A replay is not a restore.** A landmark's own `mutatorChances` rolls when it is placed; the
2026-08-26 pass measured those rolls dropping `MixedBiome`, `AnimalLife_Decreased`, `Stockpile`,
`AnimalHabitat` and `WildPlants` onto tiles nobody chose. Everything deliberate comes back; some of
the accidental character does not.

⚠️ **And the trial says nothing about the ideoligions themselves.** It proves the terrain crosses.
Whether the twelve `fixedIdeo` blocks actually produce twelve ideoligions on a non-classic world is
a separate reading — take it in the same session, with `jawa/ideo_of` and
`jawa/faction_leader_get`, before deciding anything.

## Then the decision is yours with numbers instead of my estimate

`ASHKARR_IDEOLOGY_MODE_CALL_1`.
