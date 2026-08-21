## spec
The Cherry Picker settings file has never loaded. Two synthesised keys,
`ThingDef/<nodef#10>` and `<nodef#11>`, put a raw `<` in the XML; the game
logged `Caught exception while loading mod settings data for 3521312241.
Generating fresh settings.` and discarded ALL 1,308 cuts. Repaired offline:
1,306 keys, well-formed, written to the live config and the tracked freeze.

## verify
done offline — output parses, and is the ratified list minus exactly those
two lines (`diff <(grep -v nodef <freeze>) <new>` empty). See the closing
commit.
⭐ Owner answered the two open questions 2026-08-19 and both are applied:
all 11 recorded weapon/apparel cuts went in WITH the 4 turret buildings whose
guns they are, and 28 of the 30 recorded biome cuts went in. `AridShrubland`
and `Lake` are held out by name — 2,300 tiles of the frozen Ash'karr map are
those two biomes and BiomeDef is really DELETED, not neutered. Final: **1,349**.

## criteria
on the NEXT load, `Player.log` carries NO `mod settings data for 3521312241`
exception, and a cut def is actually gone — pick one that resolves in the
dump and is not from a dead mod, e.g. `ThingDef/Gun_BlastCharge`, and confirm
it no longer appears in game. ⚠️ Cherry Picker NEUTERS ThingDef/PawnKindDef/
IncidentDef in place rather than deleting them, so check the trade/craft/spawn
lists, not the def database.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

🔵 HALF PASSES 2026-08-20; the second half is suggestive, not proven.

**result:** ✅ **`grep -c "mod settings data for 3521312241"` = 0.** The settings exception
the item was filed for is gone on this load. That half is clean.
⚠️ **The cut def: `rimworld/spawn_thing Gun_BlastCharge` returns
`success: false, "Object reference not set to an instance of an object"` and the
target cell stays empty.** Consistent with Cherry Picker neutering the def in
place — a gutted def throws rather than refusing politely. But an NRE is a scruffy
instrument: it proves something is broken about that def, not specifically that
Cherry Picker is what broke it. 🔑 The item's own warning says to check the
trade/craft/spawn LISTS rather than the def database, and a spawn CALL is not a
spawn LIST. Close it by confirming the gun is absent from a trader's stock or a
crafting bill, which needs neither a new load nor a new tool.
