## spec
🔴 **Ten of the eleven campaign factions carry a randomly generated name.** Only
`Empire` is right, and only because it is the one def with a `fixedName`.
  `Jawa_Junkers` -> "Marina's Asteroids" · `Jawa_HuttCartel` -> "Southeast
  Thiourhium" · `Jawa_IndigenousTribes` -> "Union of Aloisa" ·
  `Jawa_AscendantHelix` -> "Empire of the Sun" · `Jawa_DeepwaterCompact` ->
  "Menussia Coalition" · `Jawa_FreeDroidEnclaves` -> "Northeast Notthdos" ·
  `Jawa_GeonosianFoundryHive` -> "The Latovas Union" · `Jawa_WildsteamClan` ->
  "The Banastra Nation" · `OutlanderCivil` -> "Treaty of Haor" · `TribeCivil` ->
  "The Lánéa Nation"
Every def's `label` is CORRECT. `label` is what the def is called; `fixedName` is
what the world object carries; with no `fixedName` the name generator names the
faction at world creation.
🔴 **A def patch cannot fix a world that already exists:**
  `public string Name { get { if (HasName) return name; return def.LabelCap; } }`
  `public bool HasName => name != null;`
The generated string is stored on the faction object and shadows the def forever.
⭐ **THE REPAIR WRITES NO NAMES AT ALL.** Clearing the stored name makes `Name`
fall through to `def.LabelCap`, which is already the authored label — so there is
no list to retype and no chance of a typo putting a THIRD name into the world.
🔑 **THE FIRST STEP IS A DEPLOY, AND IT NEEDS THE GAME DOWN:**
  `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`
🔴 `--gm` or the deploy strips every player-acting tool; `build.py` refuses and
names them, which is the guard working. Expect **115** `jawa/` tools afterwards.
⚠️ **THE DISK COPY IS ALREADY AT 114 AND THAT CHANGES NOTHING YET.** Measured
2026-08-20: the deployed DLL carries `faction_name_get` and `faction_name_set`
(someone deployed mid-session), but **the RUNNING bridge reported 112** — a
companion registers its tools only at RimBridgeServer STARTUP, so a DLL replaced
under a live game is inert until the next launch. `faction_create` is the 115th
and is not on disk yet at all. ⇒ **one deploy, then one launch, then all three.**
THEN, on the world screen:
  1. `jawa/faction_name_get`  -> read `generatedCount`. Expect **10**.
  2. `jawa/faction_name_set` with `action=clear` and NO `defNames`
     — that targets exactly the factions wearing a generated name.
     ⚠️ It defaults to `dryRun=true`. Read the plan FIRST, confirm it lists ten
     and touches nothing else, then re-run with `dryRun=false`.
  3. `jawa/faction_name_get` again -> `generatedCount` must be **0**.
⚠️ `def.LabelCap` capitalises the first letter, so `the Junkers` will read
**"The Junkers"**. If the lower-case `the` matters, that one needs
`action=set` with an explicit name — but ask DECIDE before typing one.
⛔ The player faction is protected by default and must stay that way; the owner
named his own colony.

## verify
`jawa/faction_name_get` reports `generatedCount: 0` and every `currentName`
equals its `defLabel`.

## criteria
🔴 **LOOK AT THE WORLD MAP.** Click a Junkers settlement and the faction reads
"The Junkers", not "Marina's Asteroids". A numeric pass with the wrong string
still on screen is the number being wrong.
⚠️ **Then SAVE.** This edit lives on the faction object, so it is only permanent
once the world is saved.

## notes
**from:** BUILD, 2026-08-20, found read-only over the bridge on the live authored world.
🔑 **The tool you need did not exist and now does. It is BUILT and NOT YET
DEPLOYED** — a companion DLL cannot be written while the game runs.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready — blocked only on the next game-down window for the deploy
