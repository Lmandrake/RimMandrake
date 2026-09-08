# RestrainingBolts — validation walk
subject: src/RimUtinni/RestrainingBolts  (packageId `mandrake.rut.restrainingbolts`)
deps: none declared in About.xml (soft-optional on neronix17.outerrim.droiddepot for OuterRim_RestraintBolt, and mandrake.rut.utinnipatches for the Jawa_FreeDroidEnclaves faction — both resolved lazily/GetNamedSilentFail, degrades to vanilla 100 if either is absent)
list: minimal (load-clean only); full needed to exercise the actual cap (Droid Depot's hediff + UtinniPatches' Jawa_FreeDroidEnclaves faction)
status-hint: caps player goodwill ceiling with the Free Droid Enclaves faction by live count of owned pawns carrying Droid Depot's restraint-bolt hediff — no stored state, no Harmony, recomputed every ~1000-tick GoodwillSituationManager recache.

## must be true
- GoodwillSituationDef `Jawa_RestrainingBolts` exists, workerClass `RimMandrake.Utinni.RestrainingBolts.GoodwillSituationWorker_RestrainingBolts`.
- With Droid Depot inactive OR no bolted pawns owned, GetMaxGoodwill for Jawa_FreeDroidEnclaves returns the vanilla default (100) — the situation degrades quietly rather than erroring.
- With N owned pawns holding the OuterRim_RestraintBolt hediff, the cap reads `max(-70, 100 - round(2.5*N))` (e.g. N=12 → 70, N=68 → -70 floor).
- The cap applies ONLY to Faction.def == Jawa_FreeDroidEnclaves — GetMaxGoodwill for every other faction is untouched (returns 100 from this worker; other factions' own situations are unaffected).
- No stored/Scribe state: the count is read live off currently-owned pawns each recache, so freeing a droid lifts the ceiling within one recompute with no removal hook.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.restrainingbolts"
2. [D] def read-back: GoodwillSituationDef Jawa_RestrainingBolts exists; workerClass = RimMandrake.Utinni.RestrainingBolts.GoodwillSituationWorker_RestrainingBolts
3. [B] jawa/faction_goodwill_situations {faction: "Jawa_FreeDroidEnclaves"} with zero owned bolted pawns → Jawa_RestrainingBolts situation reports max goodwill 100 (or absent from the situation list entirely if the worker early-outs before recording it)
4. [B] jawa/faction_goodwill_situations {faction: "Jawa_FreeDroidEnclaves"} after spawning/afflicting several owned pawns with OuterRim_RestraintBolt → reported max goodwill drops per the 100 - 2.5*N formula, floored at -70
5. [B] jawa/faction_goodwill_check {faction: <player faction defName>, other: "Jawa_FreeDroidEnclaves", goodwillChange: 1} → CanChangeGoodwillFor reflects the lowered ceiling once bolted droids are owned (a positive change beyond the cap is refused)
