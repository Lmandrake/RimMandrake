# BOUNDARY: the receipt of what a running game has loaded, Design Version 0.1.0

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchReceiptCore.cs` (all of it), `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchReceipt.cs` (all of it), `src/RimMandrake/rimflow/loaded_build.py` (all of it).
The same page covers the `loadedOf` argument of `jawa/running_mods` (`JawaBenchNorthstarTools.cs`) and the `loaded`
subcommand of `build_match.py`. Item: `RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY`. Each promise has a test
of its name in `src/RimMandrake/rimflow/selftest_loaded_receipt.py`.

One call, `jawa/running_mods loadedOf=ours`, returns what THIS PROCESS loaded: for each of our mods each loaded
assembly's MVID (the id the compiler writes into the module; it is read from the loaded module, not from a file) and
whether the file on disk still holds that MVID; the fingerprint of the running mod list in order; the game's key; the
game version; the tick; the companion's own source hash. `build_match.py loaded` compares that with the deployed folder,
with the committed DLL and with `ModsConfig.xml`. `build_match.py identity` still hashes the deployed folder; it says
nothing about the running game.

## ACCEPTS (the only inputs this is built for)

- **a-receipt-from-a-live-game.** The reply of `jawa/running_mods` with `loadedOf`, as JSON (a file, stdin, or read over
  the bridge with `--live`).
- **load-from-a-file.** The game loads a mod DLL with `Assembly.LoadFrom` (`ModAssemblyHandler.ReloadAll`, 1.6), so a
  loaded assembly has a Location.

## DOES NOT SURVIVE (not promised)

- **stale-defs-patches-and-art.** Only code is identified. A Def, patch or texture replaced on disk after the load is not
  seen. A mod with no DLL reads NO_ASSEMBLY, never MATCH.
- **a-dll-loaded-by-hand.** An assembly that another mod loads from bytes has no Location; its row reads COULD_NOT_READ.
- **two-builds-with-one-mvid.** A tool that edits a DLL and keeps its MVID is not seen. Our compiler does not do this.
- **native-code-and-asset-bundles.** Not read.

## PROMISES (each one is owed a test of the same name)

- **the-fingerprint-is-the-same-in-game-and-in-python.** The C# and the Python fingerprints of one list are equal; case
  and a `_steam` suffix do not change it; a swap of two mods, a missing mod and an empty list each change it.
- **the-game-key-is-read-from-the-games-own-folders.** A data folder `instances\<letter>` gives `<machine>.<letter>`; any
  other folder gives `<machine>`; no machine name gives no key, never a default game.
- **a-dll-holds-its-own-mvid-and-no-other.** The MVID of a compiled module is found in its own file, and a different MVID
  is not. An empty or unreadable file answers "could not read", never "no".
- **a-mod-state-names-the-first-fault.** A mod reads LOADED, FILE_CHANGED, DLL_NOT_LOADED, FOREIGN_COPY, NO_ASSEMBLY or
  COULD_NOT_READ; LOADED only when every DLL is loaded from the mod's own folder and every file still holds the loaded
  code.
- **a-wrong-build-is-red-and-the-right-one-is-green.** The loaded MVID in both the deployed and the committed DLL reads
  MATCH; a loaded MVID absent from either reads WRONG_BUILD and names which; a DLL that is not loaded reads NOT_LOADED.
- **a-wrong-list-is-red.** A running list that differs from the expected list reads WRONG_LIST and names the first
  difference; an expected list that could not be read reads COULD_NOT_LOOK.
- **a-wrong-game-is-red.** With an expected game, another game's receipt reads WRONG_GAME; a receipt with no game key reads
  COULD_NOT_LOOK.
- **could-not-look-is-never-match.** A failed reply, a reply without `loaded`, a mod that is not in the running list and
  an unreadable DLL each give a verdict that is not MATCH and a non-zero exit, each with its own cause.

**LIVE PROOF** (2026-11-23): Steve1, testq `J20261124T011611Z-348324` (receipt rows 6 of 6) and ArchSmall (45 of 45, all three tools, `prove_three_tools.py` at 9d022c7087). On ArchSmall `build_match.py loaded` read MATCH for LuminousPigment and WeatherSuite, WRONG_BUILD for FlowWorks, GimmeSomeSlack, Pyrelands and HugeThings (their deployed DLLs were older than the commit: sha256 differs), NOT_LOADED for Graffiti and WRONG_GAME when asked for ArchBig. A Steve2 job on an old companion read every row red.

Later lists beside this page: `polish.md`, `next_version.md` (none yet).
