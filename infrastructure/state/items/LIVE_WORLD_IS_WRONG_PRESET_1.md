## spec

🔴 **MEASURED ON THE LIVE BRIDGE, 2026-08-23 07:28 — the running world is the WRONG
GEOMETRY for our paint, and it is not close.**

`PRESET_ONSCREEN_CHECK_UNVERIFIED_1` says the `myLittlePlanetSubcount 7` /
`planetCoverage 1` preset was never confirmed on the creation screen. It has now been
measured on a world that actually exists, and it is wrong:

```
jawa/world_info_get
  name            "Ash'karr"
  seedString      "seductive"
  planetCoverage  0.3          🔴 we require 1.0
  tilesCount      119904       🔴 we require 21872
  factionCount    0
```

⇒ **5.5× the tiles.** `world/ASHKARR_WORLDMAP_tiles.csv` addresses tiles 0…21871. Against a
119,904-tile grid **every one of those IDs points at different ground**, and a paint would
report success while writing a scrambled planet. This is precisely the failure the geometry
gate exists to catch, and the gate would correctly refuse.

⚠️ **The world is NAMED Ash'karr, which is the trap.** A name check passes; the geometry
check is the one that matters. Do not let "it says Ash'karr" stand in for "it is our planet".

## 🔴 And a second, independent blocker on the same reading

```
rimworld/get_ui_state    programState "Playing"   hasCurrentGame true
rimworld/get_game_info   mapCount 1               ticksGame 1
```

**A map exists.** `PAINT_UNDER_MAP_DESTROYS_GAME_1` measured that repainting under a live
map destroys game state — it killed two saves and ~2 cold loads on 2026-08-18, and
`w9_run.py` hard-refuses unless `--despite-map`. ⛔ **Do not pass that flag to get past this.**

🔑 `ticksGame: 1` with `mapCount: 1` says this is a **freshly started game**, almost certainly
a scratch colony rather than the paint target. That is fine and nothing here is a defect in
someone's work — but it means **the world now loaded is not a candidate for the paint**, and
nobody should reach for it because the bridge happens to be answering.

## what this settles

- ✅ **`PRESET_ONSCREEN_CHECK_UNVERIFIED_1` is no longer a hypothetical.** A world got made at
  coverage 0.3, so the wrong preset is reachable in practice, not just in principle.
- 🔑 **The check must be `tilesCount == 21872`, read from the bridge, BEFORE any write** —
  never the coverage slider by eye and never the world's name.

## verify

    python.exe src/RimMandrake/Utils/w9_run.py        # dry run; it makes both checks itself

**PASS =** the dry run reaches its stage plan without refusing. Today it cannot: it dies at
`rimworld/get_game_info` on the map count, and the geometry gate would refuse behind it.

## criteria

- [ ] A world exists at `tilesCount == 21872` and `planetCoverage == 1.0`.
- [ ] `mapCount == 0` at the moment of the paint.
- [ ] Both read off the bridge and recorded, not eyeballed on the screen.
- [ ] ⛔ Neither `--despite-map` nor `--despite-abort` used to reach a green run.

## watch out

- ⚠️ **Bridge calls at this screen are SLOW.** `rimworld/get_ui_state` took over 25 s and the
  default client timeout is 30 s. Below that, calls time out and the NEXT call then reads the
  previous call's late response — an id-mismatch cascade that looks like four different
  failures. Use `timeout=150` and a fresh connection per call, or read a lie.
- ⚠️ `rimworld/get_game_info` answers here, contrary to the note that it throws at
  `Page_SelectStartingSite` — because this is `programState: Playing`, not the site screen.
  The two states behave differently and the probe must not assume which one it is in.
