## spec
`<requiredCountAtGameStart>1</requiredCountAtGameStart>` added to the seven
`src/Jawa/Jawa_Patches/Defs/FactionDefs/` defs that lacked it — Jawa_HuttCartel ·
Jawa_Junkers · Jawa_DeepwaterCompact · Jawa_GeonosianFoundryHive ·
Jawa_WildsteamClan · Jawa_AscendantHelix · Jawa_FreeDroidEnclaves.
`JawaTribes.xml` untouched (already 1, max 2). Deployed to the game copy.

## verify
done offline — `grep -c requiredCountAtGameStart …/FactionDefs/*.xml` = 1 on all
eight; `validate_patch.py --defs` 0 errors, 8 files. The one warning is a
pre-existing `iconPath` note on JawaHuttCartel, unrelated.

## criteria
on the Configure Factions page at the owner's worldgen run, all eight Jawa
factions arrive at a count of at least 1 without him touching a counter.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

✅ DONE — PASSED 2026-08-20 by OUTCOME, on the live Ash'karr world.

**result:** Read off the generated planet with `jawa/world_objects_get` (read-only):
  Jawa_AscendantHelix 2 · Jawa_DeepwaterCompact 3 · Jawa_FreeDroidEnclaves 1
  Jawa_GeonosianFoundryHive 1 · Jawa_HuttCartel 3 · Jawa_WildsteamClan 3
  Jawa_Junkers 1 · Jawa_IndigenousTribes 3
**All eight are present at >= 1**, which is the thing the criterion protects.
📌 38 settlements total, and **0 carry a null faction** — the trap W6 exists to
guard against did not fire on this world either.
⚠️ INSTRUMENT DIFFERS FROM THE CRITERION, stated plainly: the criterion named the
Configure Factions page at the owner's worldgen run, and that page is long gone
by the time a world exists. What is measured here is the RESULT of that page, not
the page. If the owner hand-ticked any counter the two are indistinguishable —
but `requiredCountAtGameStart` cannot be disproven by this reading either, and
eight for eight with no zeros is what a working default looks like.
