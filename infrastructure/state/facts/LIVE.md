# LIVE — what the running game tells us. CHECK writes. DECIDE and BUILD read.

- A **quicktest builds a FULL world**, not a stub: 119,904 tiles, `waterPct 25.0`,
  2 water bodies, `seedString "green"`, `planetCoverage 0.3`, `previewOnly:false`.
  ⇒ the sea can be measured on disposable worlds without opening the planet page
  or the once-only Configure Factions screen.
- `waterPct 25.0` is a **mode, not a constant** — seed `sickle` read 16.74.
- `start_debug_game_ready` **times out at the client (30 s) and still works**;
  `hasCurrentGame` flips false→true after. Budget ~90 s. Do not retry a timeout.
- After a map exists the game is **not reactive for ~40 s**, whatever
  `currentMapReady` reports. Read-only calls are fine inside it; mutations are not.
- **A GenStep runs at map generation and never again.** Anything it scattered is
  frozen with the def that was deployed when that map was made — counting it on an
  older map measures the older def.
- `IncidentWorker_RaidEnemy` takes `IncidentParms` **by reference** and
  `PawnGroupMakerUtility` **overwrites `parms.faction`** if your faction is not
  hostile. The raid reports success and a different faction arrives. **Read the
  faction back out of the reply**, and pass `points` explicitly or the storyteller
  default gives one trivial attacker.
- Spawning the **second** pawn of a race whose flesh type we set `isOrganic=false`
  throws: no `Pawn_RelationsTracker`, and HAR dereferences it. First spawn of each
  def always succeeds. Confirmed live.
- **Vanilla art lives in asset bundles**, so a wrong `iconPath` and a right one look
  identical offline. Icon paths can only be settled by looking in-game.
- Live mod count is **585 active**; the last offline def dump was built from 580.
  Both are correct about different things — re-run `refresh.py` before trusting a
  disk-derived lookup.
- Companion DLL: **30 tools built (md5 `d7e7c6c1`), 26 deployed.** A companion
  deploy needs the game DOWN and **must pass `--gm`** or it strips
  `fire_incident` and `send_letter`.
