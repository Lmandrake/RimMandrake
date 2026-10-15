# Clean saved test maps — design (TESTSITE_SAVES_BUILD_ONE_CALM_MAP, 2026-10-15)

**Ruling** (owner, by card 2026-10-15, *"How should we change the way the three mods are tested live? → Clean saved
maps"*): live testing of the ratchet pilot uses one cleared, calm map per suite. Each map is saved once, and every run
loads it (~90 s) instead of generating a fresh map.

**Why:** rounds 5-8 spent ~6 h live. They met ~9 test-environment hazards and found ~0 mod defects. The hazards were
heat, fogged mechs and shrine pawns, storm fires, spiders and hives, stray drones, a river ending at the sea, and ferry
banks. Every one arrived with a freshly generated map.

**Also owner, 2026-10-15:** *"The pawns that emerge from an ancient danger (hidden site on the map) may not be there
before you open it, not sure."* So the saved maps contain no ancient-danger structures and no caskets.

## 1. How each suite gets its map today

| suite | today | map needs |
|---|---|---|
| GSS `proof_all.py --live` | P1 makes a fresh quicktest map (`--no-fresh-map` = current map); P2c/P3 `calm_map()` disarms triggers, removes hostile buildings and non-colonists, unfogs the whole map and re-sweeps | 250x250, Playing, ≥3 colonists, clear ground at `run_live.REGION` (it clears its own sites), Clear weather, noon pin (its own) |
| FlowWorks `validation_v2.py --live --fresh-map` | rolls up to 4 quicktest maps to avoid frozen biomes; L1 refuses a non-pristine engine or rain | 250x250, pristine FlowWorks engine (0 bodies/excavations/superdeep), dry, not frozen |
| FlowWorks rivers `extension_proof.py --site river` | `river_site.py` first: founds a colony on a mild river tile in the current world, requires moving water on ≥2 edges, drops rejected maps | a current with a fast lane, ≥2 moving-water edges, fish biome, mild (14-20 C mean), 3 drafted colonists |
| Pyrelands (northstar_driver plan) | already uses a SAVE: `northstar_site.py --reload-only --tag r6` reloads `NS_Pyrelands_site_1_417df172fdb5_r6`, then settles 1500 ticks | RM_Pyrelands at ~50 C (the heat is the subject), its ruins (`ruins` chain) and wildlife (`animal_census`) kept |

Pyrelands proved the pattern: none of its rounds hit a shrine or a hive, and a fixture reload is ~90 s. Fresh-map
hazards came only from the three fresh-map suites.

## 2. Design choice: three saves, not one and not four

- **`calm`, shared by GSS proof_all and FlowWorks v2.** Both need the same thing: a 250x250 quicktest home with 3
  colonists, mild, dry, not frozen, and a pristine FlowWorks engine. Both clear their own sites. Neither keeps state
  between runs, because every run starts from a fresh load of the same file. One save means one thing to build, check
  and rebuild.
- **`river`, for FlowWorks rivers.** It cannot be shared: the plot chains' 40x30 Soil repaints cut a river (MEASURED
  2026-10-06), and v2's L1 needs a pristine engine. The site comes from `river_site.py`'s own selection: a current with a
  fast lane, ≥2 moving-water edges, and a fish biome. The quicktest home map is then dropped, so the save holds one map.
- **`pyrelands`, its own.** The site's 50 C heat is the subject, and its ruins and wildlife are measured. Built from the
  existing fixture with the narrower `danger` profile (below) and saved as tag `calm`.

## 3. The build (`src/RimMandrake/Utils/modcheck/test_site_saves.py build <site>`)

1. **calm**: a fresh quicktest map, re-rolled (≤6) until it is 250x250, the biome is not frozen/desert/swamp, outdoor
   temperature is 8-27 C (a 3 C margin inside the 5-30 C band), it is not raining and the FlowWorks engine is pristine.
   **river**: a fresh quicktest map, then `river_site.py` (its own checks), then the home map is dropped.
2. `clean_map(profile)`, in this order (every step is read back):
   1. disarm every fog/proximity trigger and signal action (`testenv_guards.disarm_fog_triggers`);
   2. **ancient-danger containers and threats go by Vanish, before the unfog.** Matched by `DANGER_RE`: caskets, hermetic
      crates, sarcophagi, hives, egg sacs, glow pods, turrets, spawners, mech drops. Explosive and pulser items (r8:
      antigrain warheads in two shrines) also go. `Building_Casket.Destroy(Vanish)` runs
      `innerContainer.ClearAndDestroyContents()` (rimsage 1.6), so a sleeper inside is destroyed with its casket and
      never dropped. This answers the owner's "may not be there before you open it";
   3. every non-colonist pawn vanishes (`destroy_bulk nonColonists`);
   4. **calm profile only:** every unowned artificial building (ruins, walls, columns, shrine décor) vanishes. Natural
      scenery (geysers) stays;
   5. the WHOLE map is unfogged, then re-swept until the hostile listing is empty (`testenv_guards.clear_map_fog`; r8:
      the unfog released 5 fleshbeasts / 5 mechs, swept in one pass). A save with no fog has no pocket for a later wall
      removal to flood, so no "Area revealed" letter can come and no sleeper can wake;
   6. a second trigger and danger pass, which sees whatever the fog hid;
   7. the map-only quiet profile (`quiet_site.MAP_ONLY` + modal broker): threat structures, hostiles, proximity letters;
   8. `calm_sky`: Clear locked, transitioned twice (no storm tail), every fire out, 0 Fire read back; incident queue cleared.
3. `check_map(site)` read-back: 0 fogged cells, 0 triggers, 0 danger things, 0 ruins (calm), 0 hostile pawns, 0
   threat structures, 0 fires, not raining, outdoor temperature in band (calm/river 5-30 C; Pyrelands has no band),
   ≥3 standing colonists, 250x250. **Nothing is saved unless every reading is clean.**
4. Back up the whole Saves folder to `Transient/test_site_saves/saves_backup_<stamp>/` (project rule), save under the
   stable name, then STAT: the new `.rws` appeared and no existing file changed (the wrong-slot trap). **A save is never
   overwritten.** A rebuild takes the next version (`RM_TestSite_calm_v2`), and `SITES` in the module names the current one.
5. The registry `src/RimMandrake/Utils/modcheck/test_site_saves.json` records the save name, tile, mapId, biome, HEAD
   at build, profile, outdoor temperature at save and byte size. The `.rws` files live in the game's Saves folder on this
   machine only. They are derived (rebuildable by the command above), so they are never committed.

Stable names: `RM_TestSite_calm_v1`, `RM_TestSite_river_v1`, `NS_Pyrelands_site_1_<fp12>_calm`.

## 4. Loading: the default for every suite

`load_site(call, site)` does the following:
1. go to the main menu (loading over a live game NREs in the teardown: northstar_site.py, measured 2026-10-01);
2. `load_game`, then poll for Playing plus a map answering;
3. make the registry's tile current;
4. re-apply the map-only quiet profile and `calm_sky` (a load resets the storyteller static and the weather lock);
5. clear the queue;
6. **`check_map` again**.

A load that does not read back clean is a SITE failure, and the suite refuses to run on it.

| suite | default now | old path kept behind |
|---|---|---|
| GSS `proof_all.py --live` | P1 loads `calm` (`--site-save`), row P1_fresh_map carries `mapMode` + the site receipt | `--fresh-map` (new quicktest), `--no-fresh-map` (current map) |
| FlowWorks `validation_v2.py --live` | loads `calm` before L1 | `--fresh-map`, `--current-map` |
| FlowWorks `extension_proof.py --live --site river` | loads `river` | `--current-map` (after `river_site.py`) |
| Pyrelands | `northstar_site.py --site 1 --fingerprint <fp> --tag calm --reload-only --tile <t>` | `--tag r6` (the uncleaned fixture) |

The suites' own guards (calm_map, quiet profile, heat guard, storm tail) stay. On a clean save they find nothing, and
anything they do find is evidence that the save drifted.

## 5. What this does not change

- The integration suite (owner 2026-10-13: two suites) still runs the world as it is. These saves are for the isolated
  mechanism suites only.
- Every DLC stays loaded. The clean pass removes content from the map, never from the mod list.
- A save is pinned to the mod set it was built on. A tier change (a new mod, a changed def) can make a load raise
  dialogs or lose defs. The read-back catches the visible half. Rebuild a save (next `_vN`) when its tier changes,
  just as the Pyrelands fixture is renamed by fingerprint/tag.
