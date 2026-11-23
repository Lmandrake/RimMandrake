## spec
A targeted Pyrelands testq job never loads the Pyrelands site, so every site-reading chain runs on whatever map the game
holds and ends UNMEASURED SITE. Measured 2026-11-13: the four scene jobs J20261113T054358Z-d106fe, J20261113T054419Z-102549,
J20261113T054436Z-323e75, J20261113T054459Z-0f057a (bridge split load 0.0 s), then probe J20261113T063457Z-633eac after
a94330aa35 fixed _on_site's loadedMaps read: `loadedMaps [{'mapId': 0, 'tile': 26641, 'biome': 'BorealForest'}]`. Earlier
jobs saw RM_TheRot and AridShrubland on map 1.

The site exists only as a registered save: `test_site_saves.json` entry `pyrelands`, save
`NS_Pyrelands_site_1_417df172fdb5_calm3`, loaded by `Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5
--tag calm3 --reload-only --tile 5` (`test_site_saves.load_site` refuses Pyrelands and points there). Neither the Steve
worker (infrastructure/stevedesktop/worker.py) nor modcheck runs that step for a Pyrelands job.

Build: before the first site chain, a Pyrelands testq job loads the registered site (worker pre-step or a suite setup
that calls the reload path), and reads UNMEASURED SITE only when that load fails (naming why). Check first that the save
is present in SteveDesktop's Saves folder; if not, ship it there.

Also seen: `_on_site` falls back to map id 1, while the only loaded map had uniqueID 0.

## acceptance
- Live: a Pyrelands testq job on SteveDesktop with chains
  ashfall_weather_accumulation,ashfall_drifts,cinderfall,blackrain,soaked_map_stays_smooth,no_ordinary_rain has no row whose
  detail starts `ExpectationFailed: UNMEASURED SITE` (red at a94330aa35: J20261113T063457Z-633eac, 6 of 6).
- Acceptance test (offline): none. This is live behaviour, a game load of a save; a mocked worker can only prove that
  the step is called, which the builder should add as its selftest.
