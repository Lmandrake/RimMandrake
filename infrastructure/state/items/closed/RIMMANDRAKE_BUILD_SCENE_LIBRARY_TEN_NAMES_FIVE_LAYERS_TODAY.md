# RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY

One ticket of the Bridge v2.0 build order, under the enacted pick of pass three. Read
`design/specs/2026-11-23-bridge-v2/11_design.md`, then the contract pages it names in
`design/specs/2026-11-23-bridge-v2/contracts/`. The order is the last section of
`design/specs/2026-11-23-bridge-v2/06_build_order.md`. Filed by `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`.

## spec

The skeleton of the scene library and its first two entry points. Python only; no companion build.

- **Builds:** `src/RimMandrake/Utils/scene.py`: the session object; the receipt on every return value (the build lines
  come from the game's handshake, never from the repo); `scene.Refused(NAME, repair)` and `scene.Fault(NAME, done)`; the
  request id given before a call is sent, and the recovery of a lost reply by that id; the process mark (TUNED,
  EXPLORED) read from the game on every call; a fake bridge that replays recorded replies, for the tests.
- **The first two entry points, to their contract pages:** `scene.open` (`contracts/open.md`) and `s.run`
  (`contracts/run.md`), by extraction from `validation_core.py`, `modcheck/helpers.py`, `modcheck/quiet_site.py` and
  `scenes/scenelib.py`, not by writing them again.
- `s.raw` and `scene.tools` (`contracts/raw.md`), because every act and read of a scene goes through them until its
  own name is built; `scene.py raw-census`.
- `scene.py help` and `help <name>`: the contract pages move to `src/RimMandrake/Utils/scene_contracts/`, with one
  pointer line left in `design/specs/2026-11-23-bridge-v2/contracts/README.md`; the page-against-signature check.
- The two launchers: `scene.py accept <script>` (a clean tree, the commit hash on the receipt, no older layer imported)
  and `scene.py explore <game>` (every run EXPLORED).
- The other seven names are not built here. Each is built by the ticket that first needs it
  (`RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP`).

## verify

Acceptance test (offline), 22 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_library.py
```

Seen red on base `47689bd93d` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** 22 checks against the fake bridge: each refusal of `contracts/open.md` by name, with nothing
  changed (8); the phase report names the refusing phase and what was put back (1); the receipt's build lines come from
  the game's reply (1); each refusal of `contracts/run.md` by name (6); an unreadable condition value ends as `unknown`
  and is never counted as false (1); a lost reply is recovered by its request id (1); a raw call of an undeclared tool
  marks the process EXPLORED, and a new session in that process carries the mark (1); `accept` refuses a tree that is
  not clean and a script that imports an older layer (1); a run from `explore` is EXPLORED (1); `help` prints ten names
  and each built page's arguments equal the function's signature (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\Utils\scene.py accept src\RimMandrake\bridgetools\scene_smoke_run.py`
  on ArchSmall or a SteveDesktop game: `open` reports six phases done; a run of 120 ticks stops on its tick; the receipt
  names the game and the loaded DLL hashes. It needs `jawa/run_until`
  (`RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH`); until then it runs on `jawa/scene_slice` and says so.

Live state at filing: UNRUN: `scene.py` does not exist yet.

## criteria

- The acceptance test prints 22 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** an `open` that reports a build it read from the repo; a run that counts an unreadable
  value as false; a second session in a marked process with no stamp; a page that names an argument the function does not
  take.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on a
  boundary page first (`design/specs/2026-11-23-bridge-v2/boundary.md`, or the contract page of the name it serves).
- No new script imports `validation_core.py`, `modcheck/helpers.py`, `quiet_site.py` or `scenelib.py` after this lands.
