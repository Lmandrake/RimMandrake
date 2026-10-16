# Gimme Some Slack: review-map coverage

Every feature of Gimme Some Slack today, mapped to the review-map station that shows it, or to the reason it has none.
Built 2026-10-15 for the owner's request (*"a nice, orderly station-by-station demonstration of the mechanics to test, the
art to examine, etc. That showed more hidden bugs than anything."*). The map: `human_review.py` (31 stations, art board M,
free area F). The key sheet it writes: `Transient/mc_human_review/keysheet.html`, filed into this folder by
`save_review_map.py`.

## Live build command and expected runtime

For the single live driver, with the game up on a tier carrying Gimme Some Slack (ratchet_pilot was used for the
2026-10-15 walk; nothing here needs FlowWorks since the hose stations left) and the bridge held. Run from the repo root
(`/home/mandrake/rm/bench`):

```
python.exe src/RimMandrake/GimmeSomeSlack/human_review.py --build --fresh-map | tr -d '\r'
python.exe src/RimMandrake/GimmeSomeSlack/save_review_map.py --name RM_gss_review_20261015 | tr -d '\r'
```

- **Expected runtime: about 3 minutes for the build, then about 30 s for the save.** That is roughly 90 s for the fresh
  quicktest map (CLAUDE.md's measure) plus about 75 s to build. The build figure is an estimate: the last measured build
  took 59.8 s for 33 stations (flowworks tier, 2026-10-06), and the 31-station build has not been timed.
- **Before saving, read the build's last line** (`DONE in Ns; notes: ...`). Every refusal is listed there and in the key
  sheet's "This build" block. These are the new round-8 staging calls, so they are the ones most likely to be refused:
  `owner:` (station 30), `spawn_thing Filth_Fuel` (29), `cplace ...:build` blueprints (31), and `cplace WaterproofConduit`
  (24).
- Then frame station 1 with `--goto 1` and take one OS screenshot (`system_screenshot.py`) to check the labels can be read.
- The save stays in the Saves folder until the owner says to delete it.

## How to read this

- **Station N**: the station number on the map. It is also the world label, the key-sheet card, and the `--goto N` target.
- **F**: the free build area. **M**: the art-slot board. **any**: every station shows it.
- **poke**: the card's *Poke it* line tells the owner how to trigger the feature. The station shows the starting state.
- **No hose here**: the hose moved to FlowWorks on 2026-10-11, and on 2026-10-15 its review stations followed it (owner:
  *"But wait! GimmeSomeSlack shouldn't even have hoses in it anymore! It should just have the cables! We moved the hoses
  into FlowWorks! Get rid of those hoses..."*). The hose's states, lanes, crossings, mazes, relay, carried hose and
  per-look reels are stations on the FlowWorks review map (`src/RimMandrake/FlowWorks/review_map.py`, section carry).
  Stations were renumbered 41 -> 31 the same day.
- Global Mod Settings get **one switch each**: `human_review.py --set gss.FIELD=V` / `--set aerial.FIELD=V`. They are
  never shown as fake copies side by side.

## Buildables and styles

| # | feature | station |
|---|---|---|
| 1 | Power conduit in each of the four looks (Scrapper, Industrial, Modern, Futuristic) | 1-4 (one each), 7-10 |
| 2 | Modern colour entries: random mix, one colour per run, orange, green, brown, yellow, blue | 5 |
| 3 | Waterproof conduit in the four looks | 24 |
| 4 | Waterproof conduit, unstyled | 19, 25 |
| 5 | Hidden conduit stays hidden (never a cord) | 25 |
| 6 | Power switch in the four looks, on | 1-4, 10 |
| 7 | Power switch, off-state art per look | 1-4 (poke: flick the switch) |
| 8 | Floor lamp in the four looks | 1-5, 7-10, 24 |
| 9 | Power mast in the four looks | 6, 10 |
| 10 | Lamp mast in the four looks | 6, 10 |
| 11 | Wall bracket in the four looks | 6 |
| 12 | Wall bracket on every wall face (N, E, S, W) | 26 |
| 13 | Power-tap clamp | 14, 27 |
| 14 | Power-tap clamp art per look (it draws the look of the run it bites) | 27 (poke: `--style`) |
| 15 | Unstyled pieces (older saves) draw the DEFAULT look; the save migration on first rebuild | 11; also 12-30 except 24 |
| 16 | The look rides blueprint -> frame -> building | 31; F (god mode off) |
| 17 | Every buildable can be built from stock | F (another faction's grid for a clamp, a wall for brackets) |

## States and mechanics

| # | feature | station |
|---|---|---|
| 18 | Floor cords: slack, loops and heaps along the run | 1-4, 12 |
| 19 | A dense conduit field becomes one tangle | 1-4 (3x3), 16 |
| 20 | A needless stub (2 cells or fewer) becomes a pointless loop | 25 |
| 21 | Cords dive into walls through a plate on every face, and into rock | 12 |
| 22 | Wall terminal: a loose live wire hangs out of the wall and drips sparks | 12 |
| 23 | Cords dive under water | 19, 24 |
| 24 | Cut floor cord: the live end sparks and whips, the dead end lies limp | 1-4 |
| 25 | Machine hookups: insulator choice, big devices, in-wall cooler, wall lamps, turret | 15, 16 |
| 26 | Selecting a powered building highlights its net's cords | 23 (poke) |
| 27 | Neighbouring nets keep their own cords and colours | 23 |
| 28 | Blueprints draw no cord | 23 |
| 29 | Save and load bring back the same cords | 23 (poke: save, then load) |
| 30 | Nothing is drawn past the map edge | 18 |
| 31 | Hanging cords sway in the wind; floor ripple is off by default | 12, 1-4 (unpause) |
| 32 | Far zoom simplifies cords | any (zoom out) |
| 33 | Overhead span sag and ground shadow | 6, 21 |
| 34 | Real power travels across a span | 6, 13, 17, 26, 28 (lamps lit) |
| 35 | A span over fog stays hidden in the fog | 17 |
| 36 | A span may pass over a roof; an anchor under a roof is refused; a new roof cuts a span | 20, 16 (poke) |
| 37 | Range limit: 20 links, 21 is refused | 21 |
| 38 | Diagonal, odd-angle and very short spans | 21 |
| 39 | A full anchor refuses a fifth link | 22 |
| 40 | A cut span: halves fall to one point, the live end sparks | 13, 29 |
| 41 | Explosions cut wires | 13 (poke: dev explosion) |
| 42 | A live fallen wire shocks and throws back whoever touches it | 29 (poke: draft a colonist onto it) |
| 43 | A live fallen wire lights spilled fuel | 29 (unpause) |
| 44 | Claiming a pole coils its wires to the other owner | 30 (poke: Claim) |
| 45 | A tap drains one way and the two grids never merge | 14, 27 |
| 46 | Tap clamp pose: bites their cord, handles turn away from ours | 27 |
| 47 | Tap clamp sparks | 14, 27 (unpause) |
| 48 | A clamp on your own grid is refused | 27 (poke, in F) |
| 49 | Caught theft: a letter, then goodwill drains every day | 14 (poke: spawn one of their pawns) |
| 50 | Run merge: the bigger run wins | 7 |
| 51 | Run merge tie: the older run wins | 8 |
| 52 | A split keeps the look on both halves | 9 |
| 53 | Restyle a whole run: cords, switch, poles, span, lamps | 10, 6 |
| 54 | A lamp keeps its own look through a run restyle; *Match its cable run* undoes it | 10 |
| 55 | Auto-link joins only anchors of the same look | 6 (poke), F |
| 56 | Modern random mix: colour per piece, stable across restyles | 5 |
| 57 | Modern one colour per run | 3, 5 |
| 58 | Industrial picks a cable kind per net (black rubber, corrugated steel, coiled) | 2, 9 |

## Gizmos, menus, messages, alerts

| # | feature | station |
|---|---|---|
| 60 | The build button's style menu (four looks, Modern colours, remembers the pick) | F, 7 (before row) |
| 61 | Placement hint: "joins X run" / "bridges A + B runs: X wins" | 7 (hover the gap) |
| 62 | Merge message names both looks | 7, 8 |
| 63 | *Link wire* | 17, 21, 26, 28 |
| 64 | *Unlink wire* | 16, 17, 26 |
| 65 | *Unlink all* | 28 |
| 66 | *Re-string cut wires* | 13, 29 |
| 67 | *Auto-link selected* (shortest set of wires) | 28 |
| 68 | *Restyle this run* | 1-6, 10 |
| 69 | *Restyle this lamp* | 10 |
| 70 | *Wire down* alert, which jumps to the anchor when clicked | 13, 29 |
| 71 | *Power theft discovered* letter | 14 (poke) |
| 72 | Shock messages (knocked out; a weak heart gives out) | 29 (poke) |
| 73 | Vanilla *Claim* on an enemy pole | 30 |

## Mod Settings

These 48 settings span both settings classes. The selftest checks that every saved field has a row. The key sheet's
"Mod Settings: one switch each" table (`SETTINGS` in `human_review.py`) is the full list. Each row gives the shipped
value, what the setting does, and the station to watch while flipping it with `--set`. All of them have a station except
the three below.

| setting | why it has no station |
|---|---|
| `gss.maxSparkingEnds` (24) | It only shows once more than 24 live ends are on one map. The matrix covers it. |
| `aerial.keepWiresOnGravship` | It needs a gravship launch and landing. The live proof covers it. |
| `aerial.kineticSway` | It needs a Kinetic Arms push wave (`KINETIC_BLAST_WEAPONS_1`). Poke it on 6 or 21 if that weapon is loaded. |

`gss.excludedConduits` is a list, so `--set` refuses it. Flip it in the Mod Settings window and watch 24 and 25.

## Art assets

There are 120 PNGs under `Textures/RimMandrake/GimmeSomeSlack`. Board M lists every per-look slot. It works from the
files on disk at the paths the code reads, so it shrinks as art lands.

| art group | station |
|---|---|
| Scrapper cord pieces (strand, plug, junction tape/tin, wall/rock stubs, frayed ends, power strip) | 1, 12 |
| Industrial cord pieces and its 3 strand kinds | 2, 9 |
| Modern cord pieces, the five colour strands, and per-colour plugs, junctions, stubs and dead ends | 3, 5 |
| Futuristic (Cybertek) cord pieces | 4 |
| Live frayed end per look | 1-4 |
| Power strip, dark (Modern) | 3 (the tangle's strips, when their net is unpowered) |
| Switch, on and off, per look | 1-4, 10 |
| Floor lamp per look | 1-4, 10, 24 |
| Power mast and its top, per look | 6, 10 |
| Lamp mast and its top, per look | 6, 10 |
| Wall bracket, east/north/south faces (west is east mirrored), per look | 6, 26 |
| Tap clamp per look | 27 (`--style`) |
| Shared aerial art: span shadow | 6, 21, 22 |
| `Aerial/Insulator.png`, `Aerial/PoleTopDown.png`, root `Aerial/SpanWire.png` (the code reads only `Aerial/Styles/<Look>/SpanWire`) | none: no reader in `Source/` or `Defs/` (grep 2026-10-15), so these may be orphan art. The owner should rule keep or cut. |
| Spark glow, strand shadow | 1, 13, 29 |
| ConduitTransparent (hides vanilla's conduit art under the cords) | any (master switch off shows vanilla) |

## Not on the map (with the reason)

| feature | reason |
|---|---|
| Kinetic blasts swing wires instead of cutting them | Needs a Kinetic Arms push wave; see Mod Settings above. |
| Wires kept strung through a gravship flight | Needs a launch; the live proof covers it. |
| More than 24 sparking ends per map | The matrix covers the budget. |
| Settings-file key migration (`LegacyName`) | A settings-file rename with nothing to see on a map; `LegacyNameChecks` covers it. |
| Determinism, motion buckets, cord audit, fuzz, the unroutable census | Offline selftests (`Source/SelfTest`), not a look. |
| Removing the mod from a save | `debug_process.md` §6b keeps removal checks off review maps. |
| *Debug: draw the node graph* | A developer view. `--set gss.debugDraw=True` works on any station. |
