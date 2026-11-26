# MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH

## spec

`src/RimMandrake/Utils/modmanifest.py check|diff|capture|gap` compares three mod lists: the intended ordered manifest
(`infrastructure/state/modlists/manifest.<NAME>.json`), the next-load `ModsConfig.xml`, and the mods that the running
game loaded. It names CORE_ONLY, MISSING, EXTRA, REORDERED, DUPLICATE_ID, NOT_LOADED and UNEXPECTED_LOADED, and it
writes a proposal of our shipping mods that FULL.LATEST omits. Built at ec78d34fbd (2026-10-10).

## verify

- `python3 src/RimMandrake/Utils/selftest_modmanifest.py` (offline, 12 checks).
- Live: `preflight_bridge.py` reads its intended list through `modmanifest.load_manifest`, and
  `northstar_driver/preflight.py::check_running_list` compares the running game's mods with `modmanifest.compare`.

## criteria

- A1: after a load, `modmanifest.py check --manifest <tier> --loaded <ids>` reports NOT_LOADED empty for the tier
  that was swapped in.
- A2: the owner rules the FULL.LATEST gap proposal rows (add or not-shipping).

## refs

file: src/RimMandrake/Utils/modmanifest.py
file: src/RimMandrake/Utils/selftest_modmanifest.py
file: infrastructure/state/modlists/manifest.FULL.json
