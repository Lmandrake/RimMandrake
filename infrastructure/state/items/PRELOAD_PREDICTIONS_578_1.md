## spec
THE SET IS **578** — 577 plus `mandrake.inhabited`, enabled at the owner's call
this morning, appended last. DefDump re-armed, so it costs +18.7 s and regenerates.
🔴 **TWO NEW ASSEMBLIES RIDE THIS LOAD, which normally breaks attribution.**
`JawaBench.BridgeTools` (rebuilt, 112 tools) and `Inhabited` (brand new). They are
separable ONLY because each fails with its own distinct signal — hold to that and
do not attribute by proximity:
  JawaBench broke  ⇒ a LOW `jawa/` tool count. Nothing else changes.
  Inhabited broke  ⇒ a DEAD MODS line naming it, or its defs missing. Tool count
                     is unaffected.

## verify
_not recorded in the source queue_

## criteria
each prediction met or not met, with the number read back. A prediction that turns
out wrong is a finding, not an embarrassment — say which one moved and by how much.

## notes
**from:** CHECK, 2026-08-20 morning, before launch. Predictions are worthless written after.

**predictions:** 1. `first_light.py` reports **112** `jawa/` tools. Fewer means the BUNDLE did not
   load, not that one tool is missing. 106 means it loaded the OLD build.
2. Player.log carries `Adding mandrake.inhabited` with the `Mods\Inhabited` path.
   ⚠️ Absence here is not "the mod is broken" — it is "the mod is not in the list",
   a different fault with a different fix.
3. `DEAD MODS (static ctor)` and `(type load)` both stay at **baseline 0**. A new
   assembly is the classic cause of a rise; if either moves, Inhabited is the
   first suspect and the stack trace names the type.
4. `cross-reference (def loader)` stays at **baseline 25**. A rise means an
   `Inhabited` def references something the 578 set does not have.
5. DefDump regenerates and reports **578** mods. If it says 577 the request was
   not read at startup and every `--defs` check this session is UNMEASURED.
6. `patch operations failed` stays at **6**. `texture path failures` stays at
   **2** and both remain the GrimTerra juveniles — a third is new.
7. 🔴 `jawa/world_links_import` on `world/ASHKARR_WORLDMAP_links.csv` READS the
   file. It could never read its own documented format until last night and the
   fix is untested. This is the single most likely thing to fail today.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
