# `scene.open`: take one game, check its build, load the map, arm the recorders

**For:** it gives the script one session on one named game, in a known state, or it says by name why it cannot.

## Accepts

| argument | meaning | example |
|---|---|---|
| `game` | the game's name, in any letter case | `"ArchSmall"` |
| `needs["mods"]` | the mods that must be loaded (a tier name or mod names) | `["FlowWorks"]` |
| `needs["map"]` | a fixture save by name, or `"fresh:<kind>"` | `"RM_TestSite_river"` |
| `needs["calm"]` | the calm profile | `"standard"` |
| `contract` | the scene's contract | `moat` |

Use it as `with scene.open(...) as s:`. The session closes at the end of the block, also after an error.

## Returns

A session `s`, and `s.opened`, the **phase report**. For each phase in order (lock, identify, load, settle, calm, arm) it
says: done or refused, what it changed, and what was put back when a later phase refused.

Receipt: `game` and `build` as read from the game in the identify phase; `did`: the lock that was taken, the save that
was loaded, each calm control that was changed, each recorder that was armed; `hands`: the tools of each phase;
`could_not_look`: for example "the mod list fingerprint of the save differs from the loaded list: 2 mods".

## State changes

It takes the driver lock of that game. It may load a map. It applies the calm profile. It arms the recorders that the
contract needs, and the standard cast taps (spawn, death, damage), for the whole session. At close: the trace gets its
closing record, calm is undone, the lock is released, and the game stays paused. It never restarts a game, never
changes the mod list, and never puts the game in focus or in fullscreen.

## Refuses

| name | when | repair |
|---|---|---|
| `UNKNOWN_GAME` | the name is not one of the four | the message lists the four names |
| `GAME_HELD` | another process drives that game | the message names the holder; use a free game |
| `OWNER_HOLD` | his hold is on that game | use ArchSmall or SteveDesktop |
| `SESSION_OPEN` | a session is already open on that game | `scene.attach(game)` |
| `MOD_NOT_LOADED` | a needed mod is not in the loaded list | the message gives the mod list command and `./game` line |
| `WRONG_BUILD` | a loaded DLL of ours does not match the source at this commit | the message gives the deploy command |
| `CANONICAL_SAVE` | the map asked for is a canonical world save | name a fixture or a fresh map |
| `FIXTURE_MISSING` | the fixture save is not on that game | the message gives the copy command |

## Example (FlowWorks visit 9: `sc_moat_raid` ran on ArchSmall, on the save `RM_TestSite_river`)

```python
with scene.open("ArchSmall", contract=moat,
                needs={"mods": ["FlowWorks"], "map": "RM_TestSite_river", "calm": "standard"}) as s:
    print(s.opened)          # six phases, each done or refused
```

On visit 9 that save was not on ArchSmall. Here that is `FIXTURE_MISSING` with the copy command, before any load.

## The red check

`test_open_refuses_*` (one for each row), `test_open_phase_report_names_refusing_phase_and_what_was_put_back`,
`test_open_receipt_build_comes_from_game`. Planted fault: an `open` that reports a build it read from the repo.

## Limits

With no `map`, nothing is loaded and the receipt says so. `fresh:quicktest` is the one fresh map. A mod that ships no DLL and the cast
taps that are not built are lines of `could_not_look`. `NOT_CALM`, `LOAD_FAILED`, `LOAD_NOT_SETTLED`, `NO_MAP`, `NO_GAME` and
`WRONG_GAME` are faults, and each carries the phase report. `WRONG_BUILD` compares the needed mods' DLLs with the DLLs of this commit;
the companion is compared and reported (`is_source_at_this_commit`), and a difference does not refuse. `scene.attach` takes the session of a dead driver;
`scene.py end-session <game>` ends it without a look. It does six things in one call. The phase report is the guard; if agents cannot diagnose a refusal from the report,
`open` is split. A load on the full mod list takes many minutes, and `open` does not hide that time.
