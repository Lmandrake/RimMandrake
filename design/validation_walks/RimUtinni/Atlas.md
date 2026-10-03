# Atlas — validation walk
subject: src/RimUtinni/Atlas  (packageId `mandrake.rut.atlas`)
deps: none hard; reads mandrake.rm.lorestages and mandrake.rm.ninefold by reflection when present; entries name subjects in ~15 of our mods, each resolved at runtime
list: full Utinni list (entries need their subjects' mods); a minimal list proves only the framework and reports the rest "absent from this world"
status-hint: UTINNI_DISCOVERY_ACHIEVEMENTS_1 — the Scavenger's Atlas: an `RUT_Atlas` main tab drawing the Utinni as a ship, every `AtlasEntryDef` a running light; riddle cards flip to hints, lit cards offer lore by click-through; script = `src/RimUtinni/Atlas/validation.py`, plan = `northstar_plan.py`, selftest = `selftest_atlas.py`

## must be true
Every line ends in `→ chain.component` or `→ UNCOVERED: why`. Sources: the design doc's rulings table (`design/RimMandrake/utinni_discovery_achievements_design_2026-10-02.md`), `About.xml`, and Source/ (`GameComponent_Atlas.cs`, `AtlasTriggers.cs`, `AtlasSettings.cs`, `MainTabWindow_Atlas.cs`, `AtlasDebugActions.cs`).

Load and wiring
- The log carries no config error for `mandrake.rut.atlas`, no exception naming `RimMandrake.Utinni.Atlas`, and no `[Atlas] trigger ... threw` line. → log.log_clean
- `MainButtonDef RUT_Atlas` exists and opens `RimMandrake.Utinni.Atlas.MainTabWindow_Atlas`. → defs.tab_def
- Every `AtlasEntryDef` in `Defs/` loads (none silently discarded) and appears in the live report; which entries read "absent from this world" is recorded as evidence. → defs.entries_resolve
- Every entry's subjects exist as defs of the right type, every trigger Class is a real trigger type, every Keyed key the C# uses exists, and every .cs is compiled. → UNCOVERED: offline-only by nature; `selftest_atlas.py` (run by `run_selftests.py`) is the check

Mod Settings
- All eleven scalar fields read their shipped defaults (detection on, poll 250, hints allowed, true name hidden, absent shown, counters on, toasts on, flip animation on, pulse on, rewards OFF, reward scale 1), and a nonexistent field fails loudly. → settings.defaults
- Each scalar field is writable and restores (one chain per field, `settings_<field>.<field>_roundtrip`). → settings_detectionEnabled.detectionEnabled_roundtrip
- `disabledCategories` (per-region off) hides a region's lamps and stops its tracking. → UNCOVERED: a List<string> field; `jawa/mod_settings_field` is not known to write lists, and nothing was attempted

Detection (owner ruling Q6: seen / used / performed, per entry)
- With no evidence the scrap shrine entry is dark. → research_lights.unlit_before
- PERFORMED/USED: finishing `RUT_Rites_ScrapShrine` and polling lights `RUT_Atlas_ScrapShrine`. → research_lights.lit_after_research
- LIVED THROUGH: forcing `RUT_BoilingRain` on the map and polling lights `RUT_Atlas_BoilingRain`. → weather_lights.lit_under_boiling_rain
- SEEN: a mynock on an unfogged cell lights `RUT_Atlas_Mynock`. → seen_lights.lit_when_seen
- With `detectionEnabled` off a poll lights nothing even with evidence present. → detection_off.poll_lights_nothing_when_off
- A signal ending in a trigger's tag, or `Atlas.Notify(tag)`, lights the entry. → UNCOVERED: no entry in the first batch uses a signal trigger; add a chain with `jawa/signal_send` when one does
- Terrain triggers (canals, sealant, mirror pools) fire on the slow cadence; LoreStage and god-unveiled triggers read their mods by reflection. → UNCOVERED: not yet chained; each needs its subject mod loaded and a fixture (dig + fill a canal, `GameComponent_LoreStage.SetStage`, a Ninefold unveil)
- The first poll in a save, and every load, backfills durable facts silently (no toast, no reward). → UNCOVERED: needs a save/load cycle; no bridge chain written yet
- Rewards pay only for discoveries made after they were switched on, by drop pod. → UNCOVERED: needs a tick after enabling and a drop-pod read-back; not yet chained

The window (owner ruling Q1, Q4)
- The tab draws the Utinni (hull, two asymmetric mandibles with the dead prong, spine vanes, ventral pods, reliquary heart) with each entry as a lamp in its category's region; lit lamps glow, dark lamps show "?", absent lamps are crossed out. → UNCOVERED: visual; a judge pass or the owner's eyes (debug_process §4)
- Clicking a dark lamp's card flips riddle to hint (and back); with hints disallowed the card does not flip. → UNCOVERED: UI interaction; no bridge click tool reaches IMGUI reliably (memory: click fails silently)
- A lit card offers "Read the memory", which opens the lore only when clicked; nothing opens unasked. → UNCOVERED: UI interaction, as above

## the walk
1. [L] Player.log after load has no `Config error in mandrake.rut.atlas`, no exception naming `RimMandrake.Utinni.Atlas`
2. [D] `jawa/get_defs` MainButtonDef/RUT_Atlas → tabWindowClass = RimMandrake.Utinni.Atlas.MainTabWindow_Atlas
3. [B] dev action `Report entry availability` → one `[Atlas] REPORT entry=` line per entry
4. [B] finish research `RUT_Rites_ScrapShrine`, dev action `Poll all triggers now` → REPORT shows `RUT_Atlas_ScrapShrine lit=True`
5. [S] (human pass) open the Atlas tab: the ship reads as the Utinni; click a dark lamp, click its card, watch it flip to the hint; click a lit card's "Read the memory"

## anti-guessing notes
- RULED OUT: HiddenItemsManager.Hidden(def) as a "discovered" test for any def — it returns false for defs the manager does not track, so it would light at once; the trigger requires `hiddenWhileUndiscovered` (rimsage, RimWorld/HiddenItemsManager.cs `Hidden`).
- RULED OUT: FlowWorks canal fill being invisible to `TerrainGrid.TerrainAt` because it is temp terrain — `TerrainAt(int)` returns `tempGrid` first (rimsage, Verse/TerrainGrid.cs).
- RULED OUT: graffiti (category Filth) missing from `listerThings.ThingsOfDef` — `ListerThings.EverListable` excludes only motes and region-use projectiles (rimsage, Verse/ListerThings.cs).
